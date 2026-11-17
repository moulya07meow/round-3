"""
FHIR R4 & HL7 Interoperability Exporter for Clinical Decision Support
---------------------------------------------------------------------
Converts CDS triage findings, physiological scores, and physician sign-offs
into standardized HL7 FHIR R4 DiagnosticReport / Observation resources
and HL7 v2.5.1 ORU messages.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List


SNOMED_FINDING_CODES = {
    "tension_pneumothorax": {"code": "275308003", "display": "Tension pneumothorax (disorder)"},
    "pneumothorax": {"code": "36118008", "display": "Pneumothorax (disorder)"},
    "massive_pleural_effusion": {"code": "60046008", "display": "Pleural effusion (disorder)"},
    "cardiomegaly_pulmonary_edema": {"code": "81802008", "display": "Cardiomegaly with pulmonary edema (disorder)"},
    "lobar_consolidation_pneumonia": {"code": "233604007", "display": "Pneumonia (disorder)"},
    "solitary_pulmonary_nodule": {"code": "399229000", "display": "Solitary pulmonary nodule (finding)"},
    "atelectasis": {"code": "46621007", "display": "Atelectasis (disorder)"},
    "normal_chest": {"code": "168731009", "display": "Normal chest radiograph (finding)"}
}


class FHIRExporter:
    """Exports CDS Case to FHIR R4 DiagnosticReport bundle."""

    @classmethod
    def export_case_to_fhir_bundle(cls, case_data: Dict[str, Any], evaluation: Dict[str, Any], audit_record: Dict[str, Any] = None) -> Dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        case_id = case_data["id"]
        mrn = case_data["mrn"]
        finding_key = evaluation.get("finding_key", "normal_chest")
        snomed = SNOMED_FINDING_CODES.get(finding_key, SNOMED_FINDING_CODES["normal_chest"])

        is_signed = audit_record is not None and audit_record.get("status") in ("APPROVED", "MODIFIED")
        report_status = "final" if is_signed else "preliminary"

        # DiagnosticReport resource
        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": f"dr-{case_id}",
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/DiagnosticReport"]
            },
            "status": report_status,
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": "RAD",
                            "display": "Radiology"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "24648-8",
                        "display": "XR Chest PA or AP view"
                    }
                ],
                "text": "Chest Radiograph - Computer-Aided Triage & Decision Support"
            },
            "subject": {
                "reference": f"Patient/{mrn}",
                "display": f"Anonymized Patient ({case_data.get('age', 'N/A')}yo {case_data.get('sex', '')})"
            },
            "effectiveDateTime": case_data.get("admit_time", now_iso),
            "issued": now_iso,
            "conclusion": (
                f"CDS PRELIMINARY IMPRESSION: {evaluation.get('primary_finding')}. "
                f"AI Triage Priority: {evaluation.get('urgency_tier')}. "
                f"Confidence: {evaluation.get('confidence_percent')}%. "
                f"{evaluation.get('clinical_guidelines')}"
            ),
            "conclusionCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": snomed["code"],
                            "display": snomed["display"]
                        }
                    ]
                }
            ],
            "result": [
                {"reference": f"Observation/obs-news2-{case_id}"},
                {"reference": f"Observation/obs-ctr-{case_id}"},
                {"reference": f"Observation/obs-finding-{case_id}"}
            ]
        }

        # Observations
        observations = [
            {
                "resourceType": "Observation",
                "id": f"obs-news2-{case_id}",
                "status": "final",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "86645-9", "display": "NEWS2 total score"}],
                    "text": "National Early Warning Score 2"
                },
                "valueInteger": case_data.get("calculated_news2", {}).get("total_score", 0),
                "interpretation": [
                    {
                        "text": case_data.get("calculated_news2", {}).get("risk_level", "Routine")
                    }
                ]
            },
            {
                "resourceType": "Observation",
                "id": f"obs-ctr-{case_id}",
                "status": "final",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "88288-6", "display": "Cardiothoracic ratio"}],
                    "text": "Cardiothoracic Ratio (CTR)"
                },
                "valueQuantity": {
                    "value": evaluation.get("cardiothoracic_ratio", 0.48),
                    "unit": "ratio",
                    "system": "http://unitsofmeasure.org",
                    "code": "{ratio}"
                },
                "referenceRange": [
                    {"high": {"value": 0.50, "unit": "ratio"}}
                ]
            },
            {
                "resourceType": "Observation",
                "id": f"obs-finding-{case_id}",
                "status": "preliminary" if not is_signed else "final",
                "code": {
                    "coding": [{"system": "http://snomed.info/sct", "code": snomed["code"], "display": snomed["display"]}],
                    "text": "Primary CDS Imaging Finding"
                },
                "valueQuantity": {
                    "value": evaluation.get("confidence_percent", 0),
                    "unit": "%",
                    "system": "http://unitsofmeasure.org",
                    "code": "%"
                }
            }
        ]

        if audit_record:
            diagnostic_report["extension"] = [
                {
                    "url": "http://antigravity.internal/fhir/StructureDefinition/clinician-audit",
                    "valueString": json.dumps(audit_record)
                }
            ]

        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": now_iso,
            "entry": [
                {"fullUrl": f"urn:uuid:{diagnostic_report['id']}", "resource": diagnostic_report}
            ] + [{"fullUrl": f"urn:uuid:{obs['id']}", "resource": obs} for obs in observations]
        }
        return bundle


class HL7v2Exporter:
    """Exports simple HL7 v2.5.1 ORU^R01 observation result message."""

    @staticmethod
    def generate_oru_message(case: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        case_id = case["id"]
        mrn = case["mrn"]
        age = case.get("age", "")
        sex = case.get("sex", "U")
        finding = evaluation.get("primary_finding", "Normal")
        tier = evaluation.get("urgency_tier", "ROUTINE")
        conf = evaluation.get("confidence_percent", 0)

        lines = [
            f"MSH|^~\\&|CDS_TRIAGE|HOSPITAL_RAD|PACS|CENTRAL|{timestamp}||ORU^R01|MSG{case_id}|P|2.5.1",
            f"PID|1||{mrn}^^^HOSPITAL^MR||PATIENT^DEIDENTIFIED||19600101|{sex}",
            f"OBR|1||RAD-{case_id}|24648-8^CHEST XRAY AP/PA^LN|||{timestamp}||||||||||||||||||F",
            f"OBX|1|TX|FINDING^PRIMARY FINDING^LN|1|{finding}|ST|||||F",
            f"OBX|2|NM|CONFIDENCE^AI CONFIDENCE^LN|1|{conf}|%|||||F",
            f"OBX|3|ST|TRIAGE^PRIORITY TIER^LN|1|{tier}|ST|||||F"
        ]
        return "\r\n".join(lines)
