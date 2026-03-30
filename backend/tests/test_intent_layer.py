"""
Tests for the Intent Layer: DSR-CRAG, LLM Parser, and Pydantic schema validation.
"""
import pytest
from pydantic import ValidationError
from backend._1_intent_layer.schemas.fiber_schemas import (
    LMAFiberSpec, HCPCFDesignSpec, ARFGeometry,
    GuidingMechanism, ModeFilteringStrategy
)
from backend._1_intent_layer.schemas.si_photonics import (
    SiPhotonicSpec, SiPhotonicsProcess, ModulatorType
)
from backend._1_intent_layer.schemas.fabrication_drc import (
    AIMPhotonics300mmDRC
)
 
 
class TestLMAFiberSchema:
    def test_valid_comb_index_lma(self, lma_comb_geometry):
        spec = LMAFiberSpec(**lma_comb_geometry)
        assert spec.core_diameter_um == 50.0
        assert spec.target_mfa_um2 == 2010.0
 
    def test_rejects_negative_core_diameter(self):
        with pytest.raises(ValidationError):
            LMAFiberSpec(
                design_family="lma_fiber", subtype="comb_index",
                core_diameter_um=-10.0, wavelength_nm=1064.0
            )
 
    def test_rejects_unphysical_index_delta(self):
        """Index delta > 0.025 exceeds CVD silica capability (Paper 3 constraint)."""
        with pytest.raises(ValidationError):
            LMAFiberSpec(
                design_family="lma_fiber", subtype="comb_index",
                core_diameter_um=50.0, peak_index_delta=0.05,  # > 0.025 limit
                wavelength_nm=1064.0
            )
 
    def test_mode_filtering_strategy_enum(self):
        spec = LMAFiberSpec(
            design_family="lma_fiber", subtype="step_index",
            core_diameter_um=30.0, wavelength_nm=1030.0,
            mode_filtering=ModeFilteringStrategy.BEND_LOSS
        )
        assert spec.mode_filtering == ModeFilteringStrategy.BEND_LOSS
 
 
class TestHCPCFSchema:
    def test_valid_ar_fiber(self, hcpcf_ar_geometry):
        geo = ARFGeometry(
            core_radius_um=15.0,
            tube_wall_thickness_um=0.42,
            num_tubes=6,
            tube_radius_um=7.0,
            nested=True
        )
        spec = HCPCFDesignSpec(
            mechanism=GuidingMechanism.ANTI_RESONANT,
            geometry=geo,
            target_wavelength_nm=1064.0,
            target_loss_db_per_m=0.000001,  # 0.001 dB/km = 0.000001 dB/m
            application="beam_delivery"
        )
        assert spec.mechanism == GuidingMechanism.ANTI_RESONANT
 
    def test_arrow_condition_wavelength_property(self):
        """ARROW condition: t = mλ/2√(n²-1). At λ=1064nm, t should be ~0.42µm."""
        geo = ARFGeometry(
            core_radius_um=15.0,
            tube_wall_thickness_um=0.42,
            num_tubes=6,
            tube_radius_um=7.0
        )
        # First-order ARROW wavelength for t=0.42µm, n_glass=1.444:
        # λ = 2 * 0.42 * √(1.444²-1) = 2 * 0.42 * 1.066 ≈ 895nm
        # Checking the property exists and returns a float
        assert isinstance(geo.antiresonance_wavelength_nm, float)
        assert 800 < geo.antiresonance_wavelength_nm < 1200  # Reasonable range
 
    def test_rejects_loss_above_threshold(self):
        """Target loss > 1 dB/m is outside HC-PCF design envelope."""
        geo = ARFGeometry(core_radius_um=10.0, tube_wall_thickness_um=0.5,
                          num_tubes=6, tube_radius_um=5.0)
        with pytest.raises(ValidationError):
            HCPCFDesignSpec(
                mechanism=GuidingMechanism.ANTI_RESONANT,
                geometry=geo,
                target_wavelength_nm=1064.0,
                target_loss_db_per_m=5.0,  # > 1.0 limit
                application="beam_delivery"
            )
 
 
class TestSiPhotonicsSchema:
    def test_valid_strip_waveguide(self, si_photonics_geometry):
        spec = SiPhotonicSpec(**si_photonics_geometry)
        assert spec.waveguide_width_nm == 450
        assert spec.pdk_node == SiPhotonicsProcess.AIM_300MM
 
    def test_aim_drc_minimum_width_enforced(self):
        """AIM PDK 300mm: minimum waveguide width 400nm."""
        with pytest.raises(ValidationError):
            SiPhotonicSpec(
                design_family="si_photonics",
                waveguide_width_nm=200,  # Below 400nm AIM minimum
                si_thickness_nm=220,
                pdk_node="AIM_PDK_300mm",
                wavelength_nm=1550.0
            )
 
    def test_aim_drc_minimum_bend_radius(self):
        """AIM PDK 300mm: minimum bend radius 5µm (from ring modulator paper)."""
        drc = AIMPhotonics300mmDRC()
        assert drc.min_bend_radius_um == 5.0
        assert drc.min_width_nm == 400
        assert drc.si_thickness_nm == 220
 
 
class TestDSRCRAGRetrieval:
    """Tests for the Dual-State Corrective RAG constraint retrieval."""
 
    def test_retrieves_constraints_for_known_pdk(self, mock_mongodb):
        from backend._1_intent_layer.constraint_db import ConstraintDB
        db = ConstraintDB(client=mock_mongodb)
        constraints = db.get_pdk_constraints("AIM_PDK_300mm")
        assert constraints["min_width_nm"] == 400
        assert constraints["min_bend_radius_um"] == 5.0
 
    def test_corrective_loop_rejects_drc_violation(self, mock_mongodb):
        """DSR-CRAG must reject a geometry that violates retrieved DRC rules."""
        from backend._1_intent_layer.dsr_crag import DSRCRAGEngine
        engine = DSRCRAGEngine(constraint_db=mock_mongodb)
 
        violating_geometry = {
            "waveguide_width_nm": 200,  # Violates 400nm minimum
            "pdk_node": "AIM_PDK_300mm"
        }
        result = engine.validate(violating_geometry)
        assert result.passed is False
        assert "min_width_nm" in result.violations[0]
 
    def test_passes_compliant_geometry(self, mock_mongodb):
        from backend._1_intent_layer.dsr_crag import DSRCRAGEngine
        engine = DSRCRAGEngine(constraint_db=mock_mongodb)
 
        valid_geometry = {
            "waveguide_width_nm": 450,  # Passes 400nm minimum
            "pdk_node": "AIM_PDK_300mm"
        }
        result = engine.validate(valid_geometry)
        assert result.passed is True 




