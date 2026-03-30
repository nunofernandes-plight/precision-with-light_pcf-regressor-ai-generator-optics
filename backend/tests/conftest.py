CONFTEST = 
import pytest
import numpy as np
import torch
from unittest.mock import MagicMock
 
 
# ── Shared geometry fixtures ─────────────────────────────────
 
@pytest.fixture
def lma_comb_geometry():
    """Comb-index LMA fiber — based on MDPI Sensors 2023 paper."""
    return {
        "design_family": "lma_fiber",
        "subtype": "comb_index",
        "core_diameter_um": 50.0,
        "num_rings": 4,
        "ring_width_um": 1.5,
        "ring_spacing_um": 2.0,
        "peak_index_delta": 0.008,
        "gradient_ring_outer_radius_um": 28.0,
        "wavelength_nm": 1064.0,
        "target_mfa_um2": 2010.0,
    }
 
 
@pytest.fixture
def hcpcf_ar_geometry():
    """Double-nested AR fiber — based on MDPI Photonics 2025 paper."""
    return {
        "design_family": "hc_pcf",
        "subtype": "anti_resonant_nested",
        "core_radius_um": 15.0,
        "tube_radius_um": 7.0,
        "tube_wall_thickness_um": 0.42,   # ARROW condition: t = λ/2√(n²-1)
        "nested": True,
        "inner_tube_radius_um": 3.5,
        "num_tubes": 6,
        "wavelength_nm": 1064.0,
        "target_loss_db_per_km": 0.00088,
    }
 
 
@pytest.fixture
def si_photonics_geometry():
    """450nm SOI waveguide — AIM PDK 300mm standard geometry."""
    return {
        "design_family": "si_photonics",
        "subtype": "strip_waveguide",
        "waveguide_width_nm": 450,
        "si_thickness_nm": 220,
        "box_thickness_um": 2.0,
        "pdk_node": "AIM_PDK_300mm",
        "wavelength_nm": 1550.0,
        "target_neff": 2.45,
    }
 
 
@pytest.fixture
def fwm_pcf_geometry():
    """PCF for 1064→770nm FWM — MDPI Photonics 2023 inverse design target."""
    return {
        "design_family": "pcf_nonlinear",
        "subtype": "fwm_phase_matched",
        "pitch_um": 2.3,
        "d_over_pitch": 0.5,
        "core_radius_um": 1.5,
        "pump_wavelength_nm": 1064.0,
        "target_signal_nm": 770.0,
        "phase_matching_condition": "degenerate_fwm",
    }
 
 
@pytest.fixture
def mock_mongodb():
    """Mock MongoDB Atlas connection for intent layer tests."""
    db = MagicMock()
    db.constraints.find_one.return_value = {
        "pdk": "AIM_PDK_300mm",
        "min_width_nm": 400,
        "min_bend_radius_um": 5.0,
        "si_thickness_nm": 220,
        "max_index_delta": 0.025,
    }
    return db
 
 
@pytest.fixture
def device():
    return torch.device("cpu")


