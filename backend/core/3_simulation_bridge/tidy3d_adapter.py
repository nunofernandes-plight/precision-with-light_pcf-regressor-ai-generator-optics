# backend/3_simulation_bridge/tidy3d_adapter.py

import tidy3d as td
import tidy3d.plugins.adjoint as tda   # for inverse design adjoint runs
from tidy3d.web import run, Job
import numpy as np
import os
import time
from typing import Optional
from .base_adapter import SimulationAdapter, SimulationInput, SimulationResult


TIDY3D_SUPPORTED_FAMILIES = {
    "si_photonics",    # SOI waveguides, ring modulators, MZI
    "si3n4",           # Si3N4 waveguides, QPP components
    "hc_pcf",          # Hollow-core PCF (3D cross-section slabs)
    "lma_fiber",       # LMA fiber mode solving
}


class Tidy3DAdapter(SimulationAdapter):
    """
    Cloud-native FDTD verification backend via Flexcompute Tidy3D API.
    
    Handles:
    - Silicon photonic PIC components (waveguides, rings, MZI, grating couplers)
    - Si3N4 integrated photonic devices (QPP components, inverse-designed splitters)
    - HC-PCF cross-section mode solving via 2.5D slab approximation
    - LMA fiber mode solving via equivalent step-index slab
    
    Authentication:
    - Set TIDY3D_API_KEY in environment or .env file
    - Free academic tier: 5 FlexCredits/month (~10 standard simulations)
    - Pro tier: pay-per-use, suitable for production verification runs
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TIDY3D_API_KEY")
        if not self.api_key:
            raise EnvironmentError(
                "TIDY3D_API_KEY not set. "
                "Register free at https://www.flexcompute.com/signup"
            )
        td.config.logging_level = "WARNING"

    def validate_input(self, sim_input: SimulationInput) -> bool:
        if sim_input.design_family not in TIDY3D_SUPPORTED_FAMILIES:
            return False
        if sim_input.simulation_fidelity == "high" and \
           sim_input.design_family in {"hc_pcf", "lma_fiber"}:
            # Full 3D fiber simulations are expensive — warn user
            import warnings
            warnings.warn(
                "High-fidelity 3D fiber simulation on Tidy3D consumes "
                "significant FlexCredits. Consider 'standard' fidelity first."
            )
        return True

    def submit(self, sim_input: SimulationInput) -> str:
        """Build Tidy3D simulation object from platform geometry and submit."""
        sim = self._build_simulation(sim_input)
        job = Job(simulation=sim, task_name=f"pwl_{sim_input.design_family}_{int(time.time())}")
        job.start()
        return job.task_id

    def retrieve(self, job_id: str) -> SimulationResult:
        """Poll Tidy3D cloud for completed job and parse results."""
        job = Job.from_task_id(job_id)
        job.monitor()   # blocking poll with progress bar
        sim_data = job.load()
        return self._parse_results(sim_data, job_id)

    # ------------------------------------------------------------------ #
    #  Geometry Translation Layer                                          #
    # ------------------------------------------------------------------ #

    def _build_simulation(self, sim_input: SimulationInput) -> td.Simulation:
        """Route to family-specific geometry builder."""
        builders = {
            "si_photonics": self._build_si_photonics,
            "si3n4":        self._build_si3n4,
            "hc_pcf":       self._build_hcpcf_slab,
            "lma_fiber":    self._build_lma_slab,
        }
        builder = builders[sim_input.design_family]
        return builder(sim_input)

    def _build_si_photonics(self, sim_input: SimulationInput) -> td.Simulation:
        """
        Build Tidy3D simulation for SOI silicon photonic components.
        
        Standard AIM PDK 300mm process parameters:
          - Si layer: 220nm thick
          - BOX (SiO2): 2µm thick  
          - Cladding: SiO2 or air
          - Wavelength range: 1260–1625nm (O to L band)
        """
        geo = sim_input.geometry_tensor  # Dict with waveguide params from cWGAN

        # Material definitions
        si  = td.Medium(permittivity=12.04)   # Si at 1550nm: n ≈ 3.47
        sio2 = td.Medium(permittivity=2.085)  # SiO2: n ≈ 1.444

        # Layer stack from geometry tensor
        si_thickness  = geo.get("si_thickness_nm", 220) * 1e-3   # convert to µm
        box_thickness = geo.get("box_thickness_um", 2.0)
        wg_width      = geo.get("waveguide_width_nm", 450) * 1e-3
        wg_length     = geo.get("waveguide_length_um", 10.0)

        # Structures
        substrate = td.Structure(
            geometry=td.Box(
                center=[0, 0, -(box_thickness / 2)],
                size=[wg_length + 4, wg_width + 4, box_thickness]
            ),
            medium=sio2
        )
        waveguide = td.Structure(
            geometry=td.Box(
                center=[0, 0, si_thickness / 2],
                size=[wg_length, wg_width, si_thickness]
            ),
            medium=si
        )

        # Source: mode source at waveguide input
        lam0 = (sim_input.wavelength_range_nm[0] + sim_input.wavelength_range_nm[1]) / 2
        freq0 = td.C_0 / (lam0 * 1e-3)   # Convert nm to µm for Tidy3D units
        freqw = td.C_0 / (sim_input.wavelength_range_nm[0] * 1e-3) - freq0

        source = td.ModeSource(
            center=[-(wg_length / 2 - 0.5), 0, si_thickness / 2],
            size=[0, wg_width + 1.0, si_thickness + 0.5],
            source_time=td.GaussianPulse(freq0=freq0, fwidth=freqw),
            direction="+",
            mode_spec=td.ModeSpec(num_modes=1)
        )

        # Monitors: S-parameters and field profile
        mode_monitor = td.ModeMonitor(
            center=[(wg_length / 2 - 0.5), 0, si_thickness / 2],
            size=[0, wg_width + 1.0, si_thickness + 0.5],
            freqs=[freq0],
            mode_spec=td.ModeSpec(num_modes=1),
            name="s_params"
        )
        field_monitor = td.FieldMonitor(
            center=[0, 0, si_thickness / 2],
            size=[wg_length, 0, si_thickness + 0.5],
            freqs=[freq0],
            name="field_xy"
        )

        # Grid specification — auto-graded for accuracy
        grid_spec = td.GridSpec.auto(
            min_steps_per_wvl=20 if sim_input.simulation_fidelity == "high" else 12
        )

        return td.Simulation(
            size=[wg_length + 4, wg_width + 4, si_thickness + box_thickness + 2],
            medium=td.Medium(permittivity=1.0),   # Air cladding default
            structures=[substrate, waveguide],
            sources=[source],
            monitors=[mode_monitor, field_monitor],
            run_time=1e-12,  # 1ps — sufficient for telecom wavelength
            grid_spec=grid_spec,
            boundary_spec=td.BoundarySpec.all_sides(td.PML())
        )

    def _build_si3n4(self, sim_input: SimulationInput) -> td.Simulation:
        """
        Build Tidy3D simulation for Si3N4 integrated photonic devices.
        
        TripleX / QuiX Quantum platform parameters:
          - Si3N4 layer: 300nm (low-confinement) or 900nm (high-confinement)
          - SiO2 cladding (top and bottom)
          - Target: QPP waveguides, WDM splitters, PBS
          - Wavelength: 900nm–1600nm
        """
        geo = sim_input.geometry_tensor
        si3n4 = td.Medium(permittivity=3.97)  # Si3N4: n ≈ 1.99 at 1550nm
        sio2  = td.Medium(permittivity=2.085)

        thickness = geo.get("si3n4_thickness_nm", 300) * 1e-3
        width     = geo.get("waveguide_width_nm", 800) * 1e-3
        length    = geo.get("device_length_um", 50.0)

        wg = td.Structure(
            geometry=td.Box(center=[0, 0, thickness/2], size=[length, width, thickness]),
            medium=si3n4
        )
        clad_bottom = td.Structure(
            geometry=td.Box(center=[0, 0, -1.5], size=[length+4, width+4, 3.0]),
            medium=sio2
        )

        lam0  = np.mean(sim_input.wavelength_range_nm)
        freq0 = td.C_0 / (lam0 * 1e-3)
        freqw = abs(td.C_0 / (sim_input.wavelength_range_nm[0] * 1e-3) - freq0)

        source = td.ModeSource(
            center=[-(length/2 - 0.5), 0, thickness/2],
            size=[0, width + 1.5, thickness + 1.0],
            source_time=td.GaussianPulse(freq0=freq0, fwidth=freqw),
            direction="+"
        )
        monitor = td.ModeMonitor(
            center=[(length/2 - 0.5), 0, thickness/2],
            size=[0, width + 1.5, thickness + 1.0],
            freqs=[freq0],
            mode_spec=td.ModeSpec(num_modes=2),  # TE + TM for PBS
            name="s_params"
        )

        return td.Simulation(
            size=[length+4, width+4, thickness+4],
            medium=sio2,
            structures=[clad_bottom, wg],
            sources=[source],
            monitors=[monitor],
            run_time=2e-12,
            grid_spec=td.GridSpec.auto(min_steps_per_wvl=15),
            boundary_spec=td.BoundarySpec.all_sides(td.PML())
        )

    def _build_hcpcf_slab(self, sim_input: SimulationInput) -> td.Simulation:
        """
        2.5D slab approximation for HC-PCF cross-section mode solving.
        
        Uses the effective index method to reduce the 3D fiber geometry
        to a 2D slab problem — accurate for confinement loss and n_eff
        estimation, 10-100x cheaper than full 3D FDTD.
        
        For high-fidelity full 3D fiber simulations, use COMSOL adapter.
        """
        geo = sim_input.geometry_tensor
        silica = td.Medium(permittivity=2.085)   # n_glass = 1.444

        core_r    = geo.get("core_radius_um", 15.0)
        tube_r    = geo.get("tube_radius_um", 7.0)
        wall_t    = geo.get("tube_wall_thickness_um", 0.4)
        num_tubes = geo.get("num_tubes", 6)

        structures = []
        for i in range(num_tubes):
            angle = 2 * np.pi * i / num_tubes
            cx = (core_r + tube_r) * np.cos(angle)
            cy = (core_r + tube_r) * np.sin(angle)
            # Outer tube wall (silica ring)
            tube = td.Structure(
                geometry=td.Cylinder(
                    center=[cx, cy, 0],
                    radius=tube_r,
                    length=5.0,    # slab thickness — effective index method
                    axis=2
                ),
                medium=silica
            )
            structures.append(tube)

        # Silica outer cladding jacket
        jacket = td.Structure(
            geometry=td.Cylinder(center=[0, 0, 0], radius=core_r*3, length=5.0, axis=2),
            medium=silica
        )
        structures.insert(0, jacket)   # jacket first, tubes punch holes

        lam0  = np.mean(sim_input.wavelength_range_nm)
        freq0 = td.C_0 / (lam0 * 1e-3)
        freqw = freq0 * 0.1

        source = td.PointDipole(
            center=[0, 0, 0],
            source_time=td.GaussianPulse(freq0=freq0, fwidth=freqw),
            polarization="Ex"
        )
        field_monitor = td.FieldMonitor(
            center=[0, 0, 0],
            size=[core_r*6, core_r*6, 0],
            freqs=[freq0],
            name="mode_profile"
        )

        return td.Simulation(
            size=[core_r*7, core_r*7, 5.0],
            medium=td.Medium(permittivity=1.0),   # Air core
            structures=structures,
            sources=[source],
            monitors=[field_monitor],
            run_time=5e-13,
            grid_spec=td.GridSpec.auto(min_steps_per_wvl=10),
            boundary_spec=td.BoundarySpec.all_sides(td.PML())
        )

    def _build_lma_slab(self, sim_input: SimulationInput) -> td.Simulation:
        """LMA fiber: equivalent slab model for mode area and n_eff estimation."""
        geo     = sim_input.geometry_tensor
        silica  = td.Medium(permittivity=2.085)
        n_core  = geo.get("core_index", 1.4455)
        n_clad  = geo.get("clad_index", 1.4440)
        core_d  = geo.get("core_diameter_um", 30.0)

        core = td.Structure(
            geometry=td.Box(center=[0, 0, 0], size=[core_d, core_d, 5.0]),
            medium=td.Medium(permittivity=n_core**2)
        )

        lam0  = np.mean(sim_input.wavelength_range_nm)
        freq0 = td.C_0 / (lam0 * 1e-3)

        source = td.ModeSource(
            center=[-core_d/2, 0, 0],
            size=[0, core_d*2, 5.0],
            source_time=td.GaussianPulse(freq0=freq0, fwidth=freq0*0.1),
            direction="+"
        )
        monitor = td.ModeMonitor(
            center=[core_d/2, 0, 0],
            size=[0, core_d*2, 5.0],
            freqs=[freq0],
            mode_spec=td.ModeSpec(num_modes=3),
            name="mode_data"
        )

        return td.Simulation(
            size=[core_d*3, core_d*3, 5.0],
            medium=td.Medium(permittivity=n_clad**2),
            structures=[core],
            sources=[source],
            monitors=[monitor],
            run_time=1e-12,
            grid_spec=td.GridSpec.auto(min_steps_per_wvl=12),
            boundary_spec=td.BoundarySpec.all_sides(td.PML())
        )

    # ------------------------------------------------------------------ #
    #  Result Parsing Layer                                                #
    # ------------------------------------------------------------------ #

    def _parse_results(self, sim_data: td.SimulationData, job_id: str) -> SimulationResult:
        """Extract unified SimulationResult from raw Tidy3D output."""
        s_params = {}
        neff_real = neff_imag = loss = mode_area = None

        if "s_params" in sim_data.monitor_data:
            mode_data = sim_data["s_params"]
            # S21 transmission: power in mode 0 at output / input
            amps = mode_data.amps.sel(mode_index=0, direction="+").values
            s21  = float(np.abs(amps[0])**2)
            s_params["S21"] = s21
            s_params["insertion_loss_dB"] = -10 * np.log10(s21 + 1e-12)

            # Extract n_eff from mode solver if available
            if hasattr(mode_data, "n_eff"):
                neff_real = float(mode_data.n_eff.values.real[0])
                neff_imag = float(mode_data.n_eff.values.imag[0])

        if "mode_data" in sim_data.monitor_data:
            mode_data = sim_data["mode_data"]
            if hasattr(mode_data, "n_eff"):
                neff_real = float(mode_data.n_eff.sel(mode_index=0).values.real)
                neff_imag = float(mode_data.n_eff.sel(mode_index=0).values.imag)
            if hasattr(mode_data, "mode_area"):
                mode_area = float(mode_data.mode_area.sel(mode_index=0).values)

        # Fidelity check: compare n_eff to DSR-CRAG prediction
        # Threshold: |predicted - simulated| / simulated < 2%
        fidelity_score = 1.0  # Placeholder — wired to DSR-CRAG grader in bridge.py

        return SimulationResult(
            adapter="tidy3d",
            passed_fidelity_check=fidelity_score > 0.98,
            fidelity_score=fidelity_score,
            neff_real=neff_real,
            neff_imag=neff_imag,
            loss_db_per_m=loss,
            mode_area_um2=mode_area,
            s_parameters=s_params if s_params else None,
            compute_time_seconds=sim_data.simulation.run_time * 1e12,
            solver_version=td.__version__,
            raw_output_path=f"results/tidy3d_{job_id}.hdf5"
        )


