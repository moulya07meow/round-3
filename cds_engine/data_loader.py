"""
Preloaded Clinical Cohort & Synthetic Radiology Generators
----------------------------------------------------------
Provides realistic, compliant, de-identified clinical test cases,
synthetic procedural chest radiographs, and tabular clinical EHR cohorts.
"""

import json
from typing import Dict, List, Any


def get_default_clinical_cases() -> List[Dict[str, Any]]:
    """
    Returns 8 diverse, realistic clinical triage cases covering:
    - Emergency critical (Tension Pneumothorax, Sepsis, Massive Effusion)
    - Urgent inpatient/ED (Cardiomegaly with Edema, Lobar Pneumonia)
    - Expedited surveillance (Solitary Pulmonary Nodule, Post-Op Atelectasis)
    - Routine baseline (Pre-op normal, pre-employment screening)
    """
    return [
        {
            "id": "CASE-101",
            "mrn": "ANON-88219",
            "patient_name": "De-identified Patient A",
            "age": 64,
            "sex": "M",
            "encounter_type": "Emergency Department (Resus)",
            "admit_time": "2026-11-17T11:45:00Z",
            "wait_time_minutes": 22,
            "clinical_history": "Sudden onset right-sided pleuritic chest pain and acute shortness of breath following central venous catheter placement.",
            "vitals": {
                "heart_rate": 128,
                "systolic_bp": 86,
                "diastolic_bp": 54,
                "respiratory_rate": 28,
                "spo2": 88.0,
                "supplemental_o2": True,
                "temperature": 37.1,
                "consciousness": "C"  # Confused / agitated
            },
            "labs": {
                "wbc": 11.2,
                "lactate": 3.8,
                "creatinine": 1.1,
                "troponin": 0.02,
                "pao2_fio2": 210
            },
            "imaging": {
                "modality": "CXR (AP Portable)",
                "finding_key": "tension_pneumothorax",
                "confidence": 0.96,
                "ctr_ratio": 0.46,
                "description": "Right-sided tension pneumothorax with complete right lung collapse, flattening of right hemidiaphragm, and contralateral leftward mediastinal shift.",
                "pathology_type": "tension_pneumothorax"
            },
            "critical_flag": True,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-102",
            "mrn": "ANON-64102",
            "patient_name": "De-identified Patient B",
            "age": 58,
            "sex": "F",
            "encounter_type": "Medical ICU",
            "admit_time": "2026-11-17T12:05:00Z",
            "wait_time_minutes": 18,
            "clinical_history": "Post-op Day 3 exploratory laparotomy. Worsening hypoxemia refractory to 4L nasal cannula, dullness to percussion at left base.",
            "vitals": {
                "heart_rate": 112,
                "systolic_bp": 98,
                "diastolic_bp": 62,
                "respiratory_rate": 24,
                "spo2": 91.0,
                "supplemental_o2": True,
                "temperature": 38.3,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 16.8,
                "lactate": 2.9,
                "creatinine": 1.8,
                "troponin": 0.04,
                "pao2_fio2": 240
            },
            "imaging": {
                "modality": "CXR (AP Portable)",
                "finding_key": "massive_pleural_effusion",
                "confidence": 0.94,
                "ctr_ratio": 0.52,
                "description": "Dense homogeneous opacification occupying the lower two-thirds of the left hemithorax with a characteristic concave upper meniscus and compression of adjacent lung.",
                "pathology_type": "massive_pleural_effusion"
            },
            "critical_flag": True,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-103",
            "mrn": "ANON-33918",
            "patient_name": "De-identified Patient C",
            "age": 72,
            "sex": "F",
            "encounter_type": "Emergency Department (Acute)",
            "admit_time": "2026-11-17T11:15:00Z",
            "wait_time_minutes": 55,
            "clinical_history": "Progressive 3-day orthopnea, paroxysmal nocturnal dyspnea, bilateral 2+ pitting pretibial edema. Known heart failure with reduced ejection fraction.",
            "vitals": {
                "heart_rate": 104,
                "systolic_bp": 168,
                "diastolic_bp": 94,
                "respiratory_rate": 22,
                "spo2": 92.0,
                "supplemental_o2": True,
                "temperature": 36.8,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 8.4,
                "lactate": 1.6,
                "creatinine": 1.4,
                "troponin": 0.08,
                "bnp": 1420
            },
            "imaging": {
                "modality": "CXR (PA & Lateral)",
                "finding_key": "cardiomegaly_pulmonary_edema",
                "confidence": 0.91,
                "ctr_ratio": 0.63,
                "description": "Marked cardiomegaly (CTR 0.63). Perihilar alveolar haze (batwing pattern), vascular cephalization, and bilateral Kerley B lines indicative of acute decompensated heart failure.",
                "pathology_type": "cardiomegaly_pulmonary_edema"
            },
            "critical_flag": False,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-104",
            "mrn": "ANON-55721",
            "patient_name": "De-identified Patient D",
            "age": 49,
            "sex": "M",
            "encounter_type": "Inpatient Medicine",
            "admit_time": "2026-11-17T11:30:00Z",
            "wait_time_minutes": 40,
            "clinical_history": "Fever up to 39.4°C, productive cough with rust-colored sputum, right pleuritic pain for 48 hours. Crackles and bronchial breath sounds at right lung base.",
            "vitals": {
                "heart_rate": 108,
                "systolic_bp": 114,
                "diastolic_bp": 72,
                "respiratory_rate": 23,
                "spo2": 93.0,
                "supplemental_o2": True,
                "temperature": 39.2,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 18.5,
                "lactate": 2.1,
                "creatinine": 0.9,
                "troponin": 0.01,
                "crp": 165
            },
            "imaging": {
                "modality": "CXR (PA View)",
                "finding_key": "lobar_consolidation_pneumonia",
                "confidence": 0.89,
                "ctr_ratio": 0.47,
                "description": "Dense airspace consolidation with prominent air bronchograms localized to the right middle and lower lobes. Costophrenic sulci remain clear.",
                "pathology_type": "lobar_consolidation_pneumonia"
            },
            "critical_flag": False,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-105",
            "mrn": "ANON-90184",
            "patient_name": "De-identified Patient E",
            "age": 56,
            "sex": "M",
            "encounter_type": "Outpatient Pulmonary Clinic",
            "admit_time": "2026-11-17T10:00:00Z",
            "wait_time_minutes": 130,
            "clinical_history": "35 pack-year smoking history. Follow-up chest X-ray for lingering post-viral cough.",
            "vitals": {
                "heart_rate": 74,
                "systolic_bp": 128,
                "diastolic_bp": 82,
                "respiratory_rate": 16,
                "spo2": 97.0,
                "supplemental_o2": False,
                "temperature": 36.6,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 6.8,
                "lactate": 0.9,
                "creatinine": 0.8,
                "troponin": 0.01,
                "hemoglobin": 14.5
            },
            "imaging": {
                "modality": "CXR (PA & Lateral)",
                "finding_key": "solitary_pulmonary_nodule",
                "confidence": 0.85,
                "ctr_ratio": 0.45,
                "description": "Well-circumscribed, non-calcified 12mm solitary soft-tissue nodule in the left upper lobe peripheral zone. No prior films available for comparison.",
                "pathology_type": "solitary_pulmonary_nodule"
            },
            "critical_flag": False,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-106",
            "mrn": "ANON-11029",
            "patient_name": "De-identified Patient F",
            "age": 41,
            "sex": "F",
            "encounter_type": "Post-Anesthesia Care Unit (PACU)",
            "admit_time": "2026-11-17T11:00:00Z",
            "wait_time_minutes": 70,
            "clinical_history": "Status post uncomplicated laparoscopic cholecystectomy. Shallow guarding breathing pattern secondary to abdominal soreness.",
            "vitals": {
                "heart_rate": 84,
                "systolic_bp": 118,
                "diastolic_bp": 74,
                "respiratory_rate": 18,
                "spo2": 95.0,
                "supplemental_o2": False,
                "temperature": 37.0,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 9.1,
                "lactate": 1.1,
                "creatinine": 0.7,
                "troponin": 0.01,
                "hemoglobin": 12.8
            },
            "imaging": {
                "modality": "CXR (AP Supine)",
                "finding_key": "atelectasis",
                "confidence": 0.82,
                "ctr_ratio": 0.48,
                "description": "Linear discoid/plate-like opacities parallel to the diaphragm at both lung bases consistent with subsegmental atelectasis. Clear apices and mid-zones.",
                "pathology_type": "atelectasis"
            },
            "critical_flag": False,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-107",
            "mrn": "ANON-77821",
            "patient_name": "De-identified Patient G",
            "age": 35,
            "sex": "F",
            "encounter_type": "Occupational Health Clinic",
            "admit_time": "2026-11-17T09:30:00Z",
            "wait_time_minutes": 160,
            "clinical_history": "Routine pre-employment screening examination. Asymptomatic, no toxic exposures, non-smoker.",
            "vitals": {
                "heart_rate": 68,
                "systolic_bp": 116,
                "diastolic_bp": 76,
                "respiratory_rate": 14,
                "spo2": 99.0,
                "supplemental_o2": False,
                "temperature": 36.7,
                "consciousness": "A"
            },
            "labs": {
                "wbc": 6.2,
                "lactate": 0.8,
                "creatinine": 0.7,
                "troponin": 0.01,
                "hemoglobin": 13.4
            },
            "imaging": {
                "modality": "CXR (PA View)",
                "finding_key": "normal_chest",
                "confidence": 0.98,
                "ctr_ratio": 0.44,
                "description": "Lungs are well-expanded and clear of focal consolidation, effusion, or pneumothorax. Cardiothoracic ratio is normal (0.44). Mediastinal contours and hila unremarkable.",
                "pathology_type": "normal_chest"
            },
            "critical_flag": False,
            "physician_status": "PENDING_REVIEW"
        },
        {
            "id": "CASE-108",
            "mrn": "ANON-44901",
            "patient_name": "De-identified Patient H",
            "age": 68,
            "sex": "M",
            "encounter_type": "Emergency Department (Triage)",
            "admit_time": "2026-11-17T12:15:00Z",
            "wait_time_minutes": 10,
            "clinical_history": "Transferred from skilled nursing facility with lethargy, shivering, cloudy urine, and acute decompensation over 12 hours.",
            "vitals": {
                "heart_rate": 122,
                "systolic_bp": 88,
                "diastolic_bp": 50,
                "respiratory_rate": 26,
                "spo2": 92.0,
                "supplemental_o2": True,
                "temperature": 39.4,
                "consciousness": "V"  # Responds to voice only
            },
            "labs": {
                "wbc": 24.1,
                "lactate": 4.6,
                "creatinine": 2.4,
                "troponin": 0.06,
                "platelets": 98
            },
            "imaging": {
                "modality": "CXR (AP Portable)",
                "finding_key": "atelectasis",
                "confidence": 0.75,
                "ctr_ratio": 0.49,
                "description": "Mild bibasilar atelectatic streaking; no acute pulmonary edema or focal lobar consolidation.",
                "pathology_type": "atelectasis"
            },
            "critical_flag": True,  # High sepsis / qSOFA flag
            "physician_status": "PENDING_REVIEW"
        }
    ]


def get_tabular_clinical_dataset() -> List[Dict[str, Any]]:
    """
    Returns a benchmark cohort of 20 clinical cases with multi-system parameters
    for batch triage risk stratification and deteriorating inpatient prediction.
    """
    cases = []
    cohort_specs = [
        # (id, age, sex, hr, sbp, rr, spo2, o2, gcs_alt, temp, lactate, wbc, cr, expected_urgency)
        ("PT-001", 67, "M", 124, 88, 27, 89, True, True, 39.1, 4.2, 22.1, 2.3, "STAT"),
        ("PT-002", 74, "F", 115, 92, 25, 91, True, False, 38.6, 3.1, 19.4, 1.9, "STAT"),
        ("PT-003", 55, "M", 102, 142, 22, 93, True, False, 38.4, 2.0, 14.5, 1.2, "URGENT"),
        ("PT-004", 48, "F", 88, 128, 18, 96, False, False, 37.2, 1.2, 8.4, 0.9, "ROUTINE"),
        ("PT-005", 81, "M", 132, 84, 29, 87, True, True, 35.8, 5.1, 26.0, 2.8, "STAT"),
        ("PT-006", 62, "F", 96, 110, 20, 94, False, False, 37.8, 1.8, 11.2, 1.1, "EXPEDITED"),
        ("PT-007", 39, "M", 72, 120, 14, 98, False, False, 36.9, 0.9, 6.7, 0.8, "ROUTINE"),
        ("PT-008", 70, "F", 108, 164, 24, 92, True, False, 37.0, 1.7, 9.1, 1.5, "URGENT"),
        ("PT-009", 58, "M", 110, 96, 23, 93, True, False, 38.9, 2.8, 17.2, 1.6, "URGENT"),
        ("PT-010", 29, "F", 64, 114, 16, 99, False, False, 36.7, 0.8, 5.9, 0.7, "ROUTINE"),
        ("PT-011", 85, "F", 128, 78, 30, 86, True, True, 39.5, 6.2, 28.5, 3.1, "STAT"),
        ("PT-012", 44, "M", 80, 126, 16, 97, False, False, 37.1, 1.0, 7.3, 0.9, "ROUTINE"),
        ("PT-013", 69, "M", 104, 102, 21, 94, True, False, 38.2, 2.2, 13.8, 1.4, "EXPEDITED"),
        ("PT-014", 53, "F", 90, 134, 18, 96, False, False, 37.4, 1.3, 8.9, 1.0, "ROUTINE"),
        ("PT-015", 77, "M", 118, 90, 26, 90, True, True, 36.0, 3.9, 21.0, 2.2, "STAT"),
        ("PT-016", 61, "M", 98, 138, 19, 95, False, False, 37.5, 1.4, 10.1, 1.1, "EXPEDITED"),
        ("PT-017", 33, "F", 68, 118, 15, 98, False, False, 36.8, 0.9, 6.4, 0.8, "ROUTINE"),
        ("PT-018", 79, "F", 112, 152, 23, 93, True, False, 37.2, 1.9, 12.0, 1.6, "URGENT"),
        ("PT-019", 52, "M", 82, 122, 16, 97, False, False, 36.9, 1.1, 7.8, 0.9, "ROUTINE"),
        ("PT-020", 66, "F", 122, 86, 28, 88, True, True, 39.3, 4.7, 24.5, 2.6, "STAT")
    ]

    for item in cohort_specs:
        pid, age, sex, hr, sbp, rr, spo2, o2, gcs_alt, temp, lac, wbc, cr, expected = item
        cases.append({
            "patient_id": pid,
            "age": age,
            "sex": sex,
            "heart_rate": hr,
            "systolic_bp": sbp,
            "respiratory_rate": rr,
            "spo2": spo2,
            "supplemental_o2": o2,
            "altered_mentation": gcs_alt,
            "temperature": temp,
            "lactate": lac,
            "wbc": wbc,
            "creatinine": cr,
            "expected_urgency": expected
        })
    return cases
