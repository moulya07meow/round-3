"""
Clinical Decision Support (CDS) Triage Models & Scoring Engine
--------------------------------------------------------------
Implements evidence-based clinical risk stratification:
- NEWS2 (National Early Warning Score 2)
- qSOFA & Sepsis Risk Indices
- Shock Index (SI)
- Medical Image Finding Classification & Saliency (Grad-CAM) Estimation
- Dynamic Case Prioritization Queue Algorithm
"""

import math
import time
from typing import Dict, List, Any, Optional, Tuple


class ClinicalIndices:
    """Standardized physiological scoring tools approved for triage."""

    @staticmethod
    def calculate_news2(
        respiratory_rate: int,
        spo2: float,
        supplemental_o2: bool,
        systolic_bp: int,
        heart_rate: int,
        consciousness: str,  # 'A' (Alert), 'C' (Confusion), 'V' (Voice), 'P' (Pain), 'U' (Unresponsive)
        temperature: float,
        hypercapnic_scale: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates the National Early Warning Score 2 (Royal College of Physicians).
        Returns total score, category, and sub-score breakdown.
        """
        subscores = {}

        # 1. Respiration Rate (breaths/min)
        if respiratory_rate <= 8:
            subscores['respiratory_rate'] = 3
        elif 9 <= respiratory_rate <= 11:
            subscores['respiratory_rate'] = 1
        elif 12 <= respiratory_rate <= 20:
            subscores['respiratory_rate'] = 0
        elif 21 <= respiratory_rate <= 24:
            subscores['respiratory_rate'] = 2
        else:
            subscores['respiratory_rate'] = 3

        # 2. SpO2 (%)
        if not hypercapnic_scale:
            if spo2 <= 91:
                subscores['spo2'] = 3
            elif spo2 in (92, 93):
                subscores['spo2'] = 2
            elif spo2 in (94, 95):
                subscores['spo2'] = 1
            else:
                subscores['spo2'] = 0
        else:
            # Scale 2: for patients with confirmed hypercapnic respiratory failure
            if spo2 <= 83:
                subscores['spo2'] = 3
            elif spo2 in (84, 85):
                subscores['spo2'] = 2
            elif spo2 in (86, 87):
                subscores['spo2'] = 1
            elif 88 <= spo2 <= 92:
                subscores['spo2'] = 0
            elif spo2 in (93, 94):
                subscores['spo2'] = 1
            elif spo2 in (95, 96):
                subscores['spo2'] = 2
            else:
                subscores['spo2'] = 3

        # 3. Supplemental Oxygen
        subscores['supplemental_o2'] = 2 if supplemental_o2 else 0

        # 4. Systolic BP (mmHg)
        if systolic_bp <= 90:
            subscores['systolic_bp'] = 3
        elif 91 <= systolic_bp <= 100:
            subscores['systolic_bp'] = 2
        elif 101 <= systolic_bp <= 110:
            subscores['systolic_bp'] = 1
        elif 111 <= systolic_bp <= 219:
            subscores['systolic_bp'] = 0
        else:
            subscores['systolic_bp'] = 3

        # 5. Heart Rate (bpm)
        if heart_rate <= 40:
            subscores['heart_rate'] = 3
        elif 41 <= heart_rate <= 50:
            subscores['heart_rate'] = 1
        elif 51 <= heart_rate <= 90:
            subscores['heart_rate'] = 0
        elif 91 <= heart_rate <= 110:
            subscores['heart_rate'] = 1
        elif 111 <= heart_rate <= 130:
            subscores['heart_rate'] = 2
        else:
            subscores['heart_rate'] = 3

        # 6. Consciousness (ACVPU)
        c_code = consciousness.upper()
        if c_code == 'A':
            subscores['consciousness'] = 0
        else:
            subscores['consciousness'] = 3

        # 7. Temperature (°C)
        if temperature <= 35.0:
            subscores['temperature'] = 3
        elif 35.1 <= temperature <= 36.0:
            subscores['temperature'] = 1
        elif 36.1 <= temperature <= 38.0:
            subscores['temperature'] = 0
        elif 38.1 <= temperature <= 39.0:
            subscores['temperature'] = 1
        else:
            subscores['temperature'] = 2

        total_score = sum(subscores.values())
        single_3_trigger = any(v >= 3 for v in subscores.values())

        if total_score >= 7:
            risk_level = "High (STAT - Emergency Response)"
            action = "Immediate assessment by critical care team; consider ICU escalation"
            color = "red"
        elif total_score in (5, 6) or single_3_trigger:
            risk_level = "Medium (Urgent Clinical Response)"
            action = "Urgent review by attending team within 1 hour; continuous vital monitoring"
            color = "amber"
        elif 1 <= total_score <= 4:
            risk_level = "Low (Ward Routine Assessment)"
            action = "Ward-based response; repeat assessment every 4-6 hours"
            color = "green"
        else:
            risk_level = "Normal (Baseline Stable)"
            action = "Routine care monitoring"
            color = "blue"

        return {
            "total_score": total_score,
            "risk_level": risk_level,
            "color": color,
            "action": action,
            "single_parameter_3": single_3_trigger,
            "subscores": subscores
        }

    @staticmethod
    def calculate_qsofa(respiratory_rate: int, systolic_bp: int, gcs_or_altered_mentation: bool) -> Dict[str, Any]:
        """
        Calculates quick Sequential Organ Failure Assessment (qSOFA).
        Score >= 2 suggests high risk of poor outcome / sepsis in infected patients.
        """
        score = 0
        criteria = []

        if respiratory_rate >= 22:
            score += 1
            criteria.append("Tachypnea (RR >= 22 breaths/min)")
        if systolic_bp <= 100:
            score += 1
            criteria.append("Hypotension (SBP <= 100 mmHg)")
        if gcs_or_altered_mentation:
            score += 1
            criteria.append("Altered Mental Status (GCS < 15 or acute confusion)")

        return {
            "score": score,
            "positive": score >= 2,
            "criteria_met": criteria,
            "interpretation": "High risk of sepsis / ICU transfer" if score >= 2 else "Low immediate qSOFA sepsis mortality signal"
        }

    @staticmethod
    def calculate_shock_index(heart_rate: int, systolic_bp: int) -> Dict[str, Any]:
        """Shock Index = Heart Rate / Systolic Blood Pressure. Normal: 0.5 - 0.7."""
        if systolic_bp <= 0:
            si = 99.0
        else:
            si = round(heart_rate / systolic_bp, 2)

        elevated = si >= 0.9
        return {
            "shock_index": si,
            "elevated": elevated,
            "status": "Critical / Hemodynamic Collapse Risk" if si >= 1.0 else ("Borderline Elevated" if si >= 0.9 else "Normal")
        }


class MedicalImagingTriageEngine:
    """
    Simulates and validates clinical decision support for medical imaging (Chest X-Rays).
    Provides finding probabilities, calibrated confidence intervals, Grad-CAM attention regions,
    and Cardiothoracic Ratio (CTR) quantification.
    """

    KNOWN_PATHOLOGIES = {
        "tension_pneumothorax": {
            "label": "Tension Pneumothorax",
            "urgency_tier": "STAT",
            "base_urgency": 98,
            "target_tat_min": 10,
            "acuity_flag": "LIFE_THREATENING",
            "typical_region": {"x": 0.72, "y": 0.28, "w": 0.22, "h": 0.35, "hemithorax": "right_upper"},
            "guidelines": "ACR Appropriateness: Immediate needle thoracostomy / tube thoracostomy indicated; do not delay for repeat imaging."
        },
        "pneumothorax": {
            "label": "Pneumothorax",
            "urgency_tier": "STAT",
            "base_urgency": 90,
            "target_tat_min": 15,
            "acuity_flag": "CRITICAL",
            "typical_region": {"x": 0.70, "y": 0.25, "w": 0.20, "h": 0.30, "hemithorax": "right_apical"},
            "guidelines": "BTS / ACR Guidelines: Assess percentage pneumothorax and clinical stability. Consider chest drain if symptomatic or > 2 cm rim."
        },
        "massive_pleural_effusion": {
            "label": "Massive Pleural Effusion",
            "urgency_tier": "STAT",
            "base_urgency": 86,
            "target_tat_min": 25,
            "acuity_flag": "URGENT_AIRWAY_RISK",
            "typical_region": {"x": 0.18, "y": 0.65, "w": 0.30, "h": 0.28, "hemithorax": "left_basal"},
            "guidelines": "ACR Guidelines: Significant costophrenic blunting and mediastinal shift. Diagnostic/therapeutic thoracentesis recommended."
        },
        "cardiomegaly_pulmonary_edema": {
            "label": "Cardiomegaly with Pulmonary Edema",
            "urgency_tier": "URGENT",
            "base_urgency": 82,
            "target_tat_min": 45,
            "acuity_flag": "ACUTE_CHF",
            "typical_region": {"x": 0.35, "y": 0.50, "w": 0.35, "h": 0.35, "hemithorax": "central_cardiac"},
            "guidelines": "AHA/ACC: CTR > 0.55 with perihilar batwing alveolar opacities. Urgent IV diuresis & cardiology evaluation indicated."
        },
        "lobar_consolidation_pneumonia": {
            "label": "Lobar Consolidation (Pneumonia)",
            "urgency_tier": "URGENT",
            "base_urgency": 76,
            "target_tat_min": 60,
            "acuity_flag": "SEPSIS_FOCUS",
            "typical_region": {"x": 0.68, "y": 0.52, "w": 0.24, "h": 0.28, "hemithorax": "right_middle_lower"},
            "guidelines": "IDSA/ATS Guidelines: Dense airspace consolidation with air bronchograms. Initiate targeted antimicrobial therapy within 4 hours."
        },
        "solitary_pulmonary_nodule": {
            "label": "Solitary Pulmonary Nodule",
            "urgency_tier": "EXPEDITED",
            "base_urgency": 58,
            "target_tat_min": 120,
            "acuity_flag": "MALIGNANCY_SURVEILLANCE",
            "typical_region": {"x": 0.28, "y": 0.32, "w": 0.12, "h": 0.12, "hemithorax": "left_upper"},
            "guidelines": "Fleischner Society 2017 Guidelines: 8mm solid nodule in high-risk patient requires chest CT with contrast in 3 months or PET-CT."
        },
        "atelectasis": {
            "label": "Bibasilar Subsegmental Atelectasis",
            "urgency_tier": "EXPEDITED",
            "base_urgency": 40,
            "target_tat_min": 240,
            "acuity_flag": "POST_OP_COLLAPSE",
            "typical_region": {"x": 0.20, "y": 0.72, "w": 0.60, "h": 0.16, "hemithorax": "bilateral_basal"},
            "guidelines": "Incentive spirometry, early ambulation, and respiratory physiotherapy."
        },
        "normal_chest": {
            "label": "No Acute Cardiopulmonary Abnormality",
            "urgency_tier": "ROUTINE",
            "base_urgency": 12,
            "target_tat_min": 480,
            "acuity_flag": "UNREMARKABLE",
            "typical_region": {"x": 0.5, "y": 0.5, "w": 0.05, "h": 0.05, "hemithorax": "none"},
            "guidelines": "Normal cardiovascular silhouette, clear lung fields, sharp costophrenic angles. Routine read."
        }
    }

    @classmethod
    def evaluate_case(
        cls,
        primary_finding_key: str,
        confidence: float,
        ctr_ratio: float = 0.48,
        findings_differential: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Produces detailed CDS radiological evaluation, including confidence intervals,
        Grad-CAM attention heatmap parameters, and clinical recommendation.
        """
        meta = cls.KNOWN_PATHOLOGIES.get(primary_finding_key, cls.KNOWN_PATHOLOGIES["normal_chest"])

        # 95% Confidence Interval simulation based on sample calibration
        err_margin = max(0.02, round((1.0 - confidence) * 0.35, 3))
        ci_lower = max(0.0, round(confidence - err_margin, 3))
        ci_upper = min(1.0, round(confidence + err_margin, 3))

        # Grad-CAM heatmap grid (8x8 coordinate weights for attention map)
        region = meta["typical_region"]
        attention_map = cls._generate_saliency_grid(region["x"], region["y"], region["w"], region["h"])

        differential = findings_differential or [
            {"finding": meta["label"], "probability": confidence, "tier": meta["urgency_tier"]},
            {"finding": "Subsegmental Atelectasis", "probability": round((1.0 - confidence) * 0.45, 2), "tier": "EXPEDITED"},
            {"finding": "Artifact / Projectional Variation", "probability": round((1.0 - confidence) * 0.25, 2), "tier": "ROUTINE"}
        ]

        return {
            "primary_finding": meta["label"],
            "finding_key": primary_finding_key,
            "urgency_tier": meta["urgency_tier"],
            "base_urgency": meta["base_urgency"],
            "target_tat_min": meta["target_tat_min"],
            "acuity_flag": meta["acuity_flag"],
            "confidence": round(confidence, 3),
            "confidence_percent": int(confidence * 100),
            "confidence_interval_95": [ci_lower, ci_upper],
            "cardiothoracic_ratio": round(ctr_ratio, 2),
            "cardiomegaly_present": ctr_ratio > 0.50,
            "region_of_interest": region,
            "saliency_grid": attention_map,
            "clinical_guidelines": meta["guidelines"],
            "differential_findings": differential
        }

    @staticmethod
    def _generate_saliency_grid(rx: float, ry: float, rw: float, rh: float, grid_size: int = 16) -> List[List[float]]:
        """Generates a 2D attention activation matrix centered around the target ROI."""
        cx = rx + rw / 2.0
        cy = ry + rh / 2.0
        sigma_x = max(0.08, rw / 1.5)
        sigma_y = max(0.08, rh / 1.5)

        grid = []
        for i in range(grid_size):
            row = []
            gy = (i + 0.5) / grid_size
            for j in range(grid_size):
                gx = (j + 0.5) / grid_size
                dx = (gx - cx) / sigma_x
                dy = (gy - cy) / sigma_y
                val = math.exp(-0.5 * (dx * dx + dy * dy))
                # Add baseline noise for realism
                val = max(0.02, min(1.0, val))
                row.append(round(val, 3))
            grid.append(row)
        return grid


class CasePrioritizer:
    """
    Dynamically sorts clinical and imaging cases into a unified triage queue.
    Balances disease severity, NEWS2 clinical score, wait time degradation, and high-risk flags.
    """

    @staticmethod
    def calculate_composite_urgency(
        imaging_urgency: int,
        news2_score: int,
        qsofa_positive: bool,
        wait_time_minutes: int,
        has_critical_flag: bool = False
    ) -> Dict[str, Any]:
        """
        Combines radiological AI risk with clinical vital score and time elapsed.
        Urgency Scale: 0 to 100.
        Tiers:
          - STAT (90 - 100): Immediate review required
          - URGENT (70 - 89): Review within 60 min
          - EXPEDITED (40 - 69): Review within 120 min
          - ROUTINE (0 - 39): Review within 480 min
        """
        # Base components
        # Clinical NEWS2 scaled to 0-100: NEWS2 of 7+ is severe (scaled to ~90)
        news2_factor = min(100, news2_score * 12.5)

        # Base composite: 55% imaging urgency, 35% clinical vital signs
        composite = 0.55 * imaging_urgency + 0.35 * news2_factor

        # Wait-time penalty (prevents starvation of routine cases, escalates stagnant urgent cases)
        # Adds up to 15 points based on wait time relative to target
        time_factor = min(15.0, (wait_time_minutes / 30.0) * 2.5)
        composite += time_factor

        # Escalation rules
        if has_critical_flag:
            composite = max(composite, 92.0)
        if qsofa_positive and news2_score >= 5:
            composite = max(composite, 88.0)

        composite = round(min(100.0, max(0.0, composite)), 1)

        # Categorize tier
        if composite >= 88.0:
            tier = "STAT"
            tier_color = "#EF4444"  # Red
            max_tat = 15
        elif composite >= 70.0:
            tier = "URGENT"
            tier_color = "#F59E0B"  # Amber
            max_tat = 60
        elif composite >= 40.0:
            tier = "EXPEDITED"
            tier_color = "#3B82F6"  # Blue
            max_tat = 120
        else:
            tier = "ROUTINE"
            tier_color = "#10B981"  # Emerald
            max_tat = 480

        overdue = wait_time_minutes > max_tat

        return {
            "composite_urgency": composite,
            "priority_tier": tier,
            "priority_color": tier_color,
            "target_tat_minutes": max_tat,
            "minutes_waiting": wait_time_minutes,
            "is_overdue": overdue,
            "urgency_breakdown": {
                "imaging_contribution": round(0.55 * imaging_urgency, 1),
                "clinical_news2_contribution": round(0.35 * news2_factor, 1),
                "wait_time_escalation": round(time_factor, 1)
            }
        }
