# backend/3_simulation_bridge/bridge.py

from .lumerical_adapter import LumericalAdapter
from .comsol_adapter    import COMSOLAdapter
from .tidy3d_adapter    import Tidy3DAdapter
from .base_adapter      import SimulationInput, SimulationResult
import os


ADAPTER_PRIORITY = ["lumerical", "comsol", "tidy3d"]

# Tidy3D is the preferred backend for silicon photonics (faster GPU FDTD)
# and the mandatory fallback when proprietary licenses are unavailable
SI_PREFERRED_BACKENDS = ["tidy3d", "lumerical", "comsol"]


def get_adapter(sim_input: SimulationInput):
    """
    Select the best available adapter for the given design family.
    
    Priority logic:
    1. Silicon photonics / Si3N4 → prefer Tidy3D (fastest GPU FDTD)
    2. Fiber designs with high fidelity → prefer COMSOL (best FEM for cross-sections)
    3. Fallback chain: check env vars for license availability
    """
    if sim_input.design_family in {"si_photonics", "si3n4"}:
        priority = SI_PREFERRED_BACKENDS
    else:
        priority = ADAPTER_PRIORITY

    for adapter_name in priority:
        adapter = _try_init_adapter(adapter_name)
        if adapter and adapter.validate_input(sim_input):
            return adapter

    raise RuntimeError(
        "No simulation adapter available. "
        "Set TIDY3D_API_KEY, LUMERICAL_PATH, or COMSOL_PATH."
    )


def _try_init_adapter(name: str):
    try:
        if name == "lumerical" and os.getenv("LUMERICAL_PATH"):
            return LumericalAdapter()
        elif name == "comsol" and os.getenv("COMSOL_PATH"):
            return COMSOLAdapter()
        elif name == "tidy3d" and os.getenv("TIDY3D_API_KEY"):
            return Tidy3DAdapter()
    except Exception:
        return None
    return None


