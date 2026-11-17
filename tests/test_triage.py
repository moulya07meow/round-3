"""
Unit & Integration Tests for Clinical Decision Support (CDS) Engine
-------------------------------------------------------------------
Verifies clinical acuity calculation, imaging triage, prioritization,
and FHIR R4 interoperability.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cds_engine.triage_models import ClinicalIndices, MedicalImagingTriageEngine, CasePrioritizer
from cds_engine.data_loader import get_default_clinical_cases, get_tabular_clinical_dataset
from cds_engine.fhir_exporter import FHIRExporter, HL7v2Exporter


class TestClinicalIndices(unittest.TestCase):

    def test_news2_normal_patient(self):
        """Test healthy baseline patient yields NEWS2 = 0."""
        res = ClinicalIndices.calculate_news2(
            respiratory_rate=16,
            spo2=98.0,
            supplemental_o2=False,
            systolic_bp=120,
            heart_rate=72,
            consciousness='A',
            temperature=37.0
        )
        self.assertEqual(res["total_score"], 0)
        self.assertIn("Normal", res["risk_level"])

    def test_news2_critical_patient(self):
        """Test severe patient (hypotension, tachypnea, hypoxemia, altered mentation) yields high score."""
        res = ClinicalIndices.calculate_news2(
            respiratory_rate=28, # +3
            spo2=88.0,           # +3
            supplemental_o2=True,# +2
            systolic_bp=86,      # +3
            heart_rate=128,      # +2
            consciousness='C',   # +3
            temperature=39.2     # +2
        )
        # Total = 3 + 3 + 2 + 3 + 2 + 3 + 2 = 18
        self.assertEqual(res["total_score"], 18)
        self.assertIn("High", res["risk_level"])
        self.assertEqual(res["color"], "red")

    def test_qsofa_criteria(self):
        """Test qSOFA identifies septic patients meeting >= 2 criteria."""
        q1 = ClinicalIndices.calculate_qsofa(respiratory_rate=24, systolic_bp=95, gcs_or_altered_mentation=True)
        self.assertEqual(q1["score"], 3)
        self.assertTrue(q1["positive"])

        q2 = ClinicalIndices.calculate_qsofa(respiratory_rate=16, systolic_bp=125, gcs_or_altered_mentation=False)
        self.assertEqual(q2["score"], 0)
        self.assertFalse(q2["positive"])

    def test_shock_index(self):
        """Test shock index calculation."""
        # 120 bpm / 80 mmHg = 1.5 (Critical)
        si = ClinicalIndices.calculate_shock_index(120, 80)
        self.assertEqual(si["shock_index"], 1.5)
        self.assertTrue(si["elevated"])

        # 70 bpm / 120 mmHg = 0.58 (Normal)
        si_norm = ClinicalIndices.calculate_shock_index(70, 120)
        self.assertEqual(si_norm["shock_index"], 0.58)
        self.assertFalse(si_norm["elevated"])


class TestImagingTriageEngine(unittest.TestCase):

    def test_tension_pneumothorax_evaluation(self):
        eval_res = MedicalImagingTriageEngine.evaluate_case(
            primary_finding_key="tension_pneumothorax",
            confidence=0.96,
            ctr_ratio=0.46
        )
        self.assertEqual(eval_res["urgency_tier"], "STAT")
        self.assertGreaterEqual(eval_res["base_urgency"], 95)
        self.assertEqual(eval_res["target_tat_min"], 10)
        self.assertIn("Appropriateness", eval_res["clinical_guidelines"])
        self.assertEqual(len(eval_res["saliency_grid"]), 16)

    def test_cardiomegaly_evaluation(self):
        eval_res = MedicalImagingTriageEngine.evaluate_case(
            primary_finding_key="cardiomegaly_pulmonary_edema",
            confidence=0.91,
            ctr_ratio=0.62
        )
        self.assertTrue(eval_res["cardiomegaly_present"])
        self.assertEqual(eval_res["urgency_tier"], "URGENT")


class TestCasePrioritization(unittest.TestCase):

    def test_stat_prioritization(self):
        prio = CasePrioritizer.calculate_composite_urgency(
            imaging_urgency=98,
            news2_score=9,
            qsofa_positive=True,
            wait_time_minutes=25,
            has_critical_flag=True
        )
        self.assertEqual(prio["priority_tier"], "STAT")
        self.assertGreaterEqual(prio["composite_urgency"], 90.0)
        self.assertTrue(prio["is_overdue"]) # Target is 15 min, waited 25 min


class TestInteroperability(unittest.TestCase):

    def test_fhir_bundle_generation(self):
        cases = get_default_clinical_cases()
        c = cases[0]
        c["calculated_news2"] = {"total_score": 9, "risk_level": "High"}
        eval_res = MedicalImagingTriageEngine.evaluate_case("tension_pneumothorax", 0.96)
        bundle = FHIRExporter.export_case_to_fhir_bundle(c, eval_res)

        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertGreater(len(bundle["entry"]), 0)
        report = bundle["entry"][0]["resource"]
        self.assertEqual(report["resourceType"], "DiagnosticReport")
        self.assertIn("Tension Pneumothorax", report["conclusion"])

    def test_hl7_oru_generation(self):
        cases = get_default_clinical_cases()
        c = cases[0]
        eval_res = MedicalImagingTriageEngine.evaluate_case("tension_pneumothorax", 0.96)
        msg = HL7v2Exporter.generate_oru_message(c, eval_res)
        self.assertIn("MSH|^~\\&|CDS_TRIAGE", msg)
        self.assertIn("OBX|1|TX|FINDING", msg)


if __name__ == "__main__":
    unittest.main()
