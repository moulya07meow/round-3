"""
Clinical Decision Support (CDS) Triage & Case Prioritization HTTP Server
-----------------------------------------------------------------------
Standard library Python HTTP Server providing REST APIs for:
- Patient worklist with dynamic priority queuing (STAT, URGENT, EXPEDITED, ROUTINE)
- Medical image analysis & Grad-CAM saliency estimation
- Tabular clinical cohort risk stratification (NEWS2, qSOFA, Shock Index)
- Human-in-the-loop physician sign-off and audit logging
- FHIR R4 and HL7 interoperability export
- Serving the interactive Clinical Web Workstation
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from typing import Dict, Any, List

# Ensure cds_engine is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from cds_engine.triage_models import ClinicalIndices, MedicalImagingTriageEngine, CasePrioritizer
from cds_engine.data_loader import get_default_clinical_cases, get_tabular_clinical_dataset
from cds_engine.fhir_exporter import FHIRExporter, HL7v2Exporter


# In-memory storage for active session
CASES_DB: Dict[str, Dict[str, Any]] = {}
AUDIT_LOG: List[Dict[str, Any]] = []


def initialize_database():
    """Populates the database with initial verified clinical cases."""
    raw_cases = get_default_clinical_cases()
    for item in raw_cases:
        cid = item["id"]
        v = item["vitals"]
        # Calculate NEWS2
        news = ClinicalIndices.calculate_news2(
            respiratory_rate=v["respiratory_rate"],
            spo2=v["spo2"],
            supplemental_o2=v["supplemental_o2"],
            systolic_bp=v["systolic_bp"],
            heart_rate=v["heart_rate"],
            consciousness=v["consciousness"],
            temperature=v["temperature"]
        )
        # Calculate qSOFA
        qsofa = ClinicalIndices.calculate_qsofa(
            respiratory_rate=v["respiratory_rate"],
            systolic_bp=v["systolic_bp"],
            gcs_or_altered_mentation=(v["consciousness"] != "A")
        )
        # Calculate Shock Index
        shock = ClinicalIndices.calculate_shock_index(
            heart_rate=v["heart_rate"],
            systolic_bp=v["systolic_bp"]
        )
        # Evaluate Imaging
        img = item["imaging"]
        eval_result = MedicalImagingTriageEngine.evaluate_case(
            primary_finding_key=img["finding_key"],
            confidence=img["confidence"],
            ctr_ratio=img["ctr_ratio"]
        )
        # Composite Prioritization
        prio = CasePrioritizer.calculate_composite_urgency(
            imaging_urgency=eval_result["base_urgency"],
            news2_score=news["total_score"],
            qsofa_positive=qsofa["positive"],
            wait_time_minutes=item["wait_time_minutes"],
            has_critical_flag=item.get("critical_flag", False)
        )

        item["calculated_news2"] = news
        item["calculated_qsofa"] = qsofa
        item["calculated_shock"] = shock
        item["imaging_evaluation"] = eval_result
        item["triage_priority"] = prio
        item["review_audit"] = None

        CASES_DB[cid] = item


initialize_database()


class CDSTriageHTTPHandler(BaseHTTPRequestHandler):
    """Handles REST API requests and serves static web workstation assets."""

    def log_message(self, format, *args):
        # Override to reduce spam in terminal, output standard format
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} -> {args[2]}\n")

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: List Prioritized Worklist
        if path == "/api/cases":
            cases_list = list(CASES_DB.values())
            # Re-sort dynamically by composite urgency descending
            cases_list.sort(key=lambda c: c["triage_priority"]["composite_urgency"], reverse=True)
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "success",
                "total_cases": len(cases_list),
                "summary": {
                    "stat": sum(1 for c in cases_list if c["triage_priority"]["priority_tier"] == "STAT"),
                    "urgent": sum(1 for c in cases_list if c["triage_priority"]["priority_tier"] == "URGENT"),
                    "expedited": sum(1 for c in cases_list if c["triage_priority"]["priority_tier"] == "EXPEDITED"),
                    "routine": sum(1 for c in cases_list if c["triage_priority"]["priority_tier"] == "ROUTINE"),
                    "pending_review": sum(1 for c in cases_list if c.get("physician_status") == "PENDING_REVIEW")
                },
                "cases": cases_list
            }).encode("utf-8"))
            return

        # 2. API: Single Case Detail
        if path.startswith("/api/cases/"):
            case_id = path.replace("/api/cases/", "").strip()
            if case_id in CASES_DB:
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "status": "success",
                    "case": CASES_DB[case_id]
                }).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Case {case_id} not found"}).encode("utf-8"))
            return

        # 3. API: Tabular Benchmark Cohort
        if path == "/api/cohort":
            cohort = get_tabular_clinical_dataset()
            # Analyze each cohort entry
            analyzed = []
            for pt in cohort:
                news = ClinicalIndices.calculate_news2(
                    respiratory_rate=pt["respiratory_rate"],
                    spo2=pt["spo2"],
                    supplemental_o2=pt["supplemental_o2"],
                    systolic_bp=pt["systolic_bp"],
                    heart_rate=pt["heart_rate"],
                    consciousness="V" if pt["altered_mentation"] else "A",
                    temperature=pt["temperature"]
                )
                qsofa = ClinicalIndices.calculate_qsofa(
                    respiratory_rate=pt["respiratory_rate"],
                    systolic_bp=pt["systolic_bp"],
                    gcs_or_altered_mentation=pt["altered_mentation"]
                )
                si = ClinicalIndices.calculate_shock_index(pt["heart_rate"], pt["systolic_bp"])
                analyzed.append({
                    **pt,
                    "calculated_news2": news,
                    "calculated_qsofa": qsofa,
                    "calculated_shock": si
                })
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success", "cohort": analyzed}).encode("utf-8"))
            return

        # 4. API: FHIR R4 Bundle Export
        if path.startswith("/api/export-fhir/"):
            case_id = path.replace("/api/export-fhir/", "").strip()
            if case_id in CASES_DB:
                c = CASES_DB[case_id]
                fhir_bundle = FHIRExporter.export_case_to_fhir_bundle(c, c["imaging_evaluation"], c.get("review_audit"))
                self._set_headers(200, "application/json")
                self.wfile.write(json.dumps(fhir_bundle, indent=2).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Case not found"}).encode("utf-8"))
            return

        # 5. API: HL7 v2.5.1 Export
        if path.startswith("/api/export-hl7/"):
            case_id = path.replace("/api/export-hl7/", "").strip()
            if case_id in CASES_DB:
                c = CASES_DB[case_id]
                hl7_msg = HL7v2Exporter.generate_oru_message(c, c["imaging_evaluation"])
                self._set_headers(200, "text/plain")
                self.wfile.write(hl7_msg.encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Case not found"}).encode("utf-8"))
            return

        # 6. API: Audit Log
        if path == "/api/audit-log":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "success",
                "count": len(AUDIT_LOG),
                "log": AUDIT_LOG
            }).encode("utf-8"))
            return

        # 7. Static Web File Serving
        web_dir = os.path.join(CURRENT_DIR, "web")
        req_file = path.lstrip("/")
        if not req_file or req_file == "":
            req_file = "index.html"

        file_path = os.path.join(web_dir, req_file)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type = "text/plain"
            if file_path.endswith(".html"):
                content_type = "text/html"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            elif file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".json"):
                content_type = "application/json"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"

            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. API: Clinician Sign-off / Review Workflow (Human-in-the-Loop)
        if path == "/api/clinician-review":
            case_id = payload.get("case_id")
            decision = payload.get("decision", "APPROVED")  # APPROVED, MODIFIED, OVERRIDDEN, REJECTED
            clinician_id = payload.get("clinician_name", "Dr. A. Vance, MD (Board Certified Radiologist)")
            rationale = payload.get("rationale", "Findings verified and concordant with clinical presentation.")
            modified_finding = payload.get("modified_finding")

            if not case_id or case_id not in CASES_DB:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": f"Invalid case ID {case_id}"}).encode("utf-8"))
                return

            case = CASES_DB[case_id]
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "case_id": case_id,
                "mrn": case["mrn"],
                "decision": decision,
                "clinician": clinician_id,
                "rationale": rationale,
                "initial_ai_finding": case["imaging_evaluation"]["primary_finding"],
                "final_signed_finding": modified_finding or case["imaging_evaluation"]["primary_finding"],
                "status": "APPROVED" if decision in ("APPROVED", "MODIFIED") else "OVERRIDDEN"
            }
            AUDIT_LOG.append(audit_entry)
            case["physician_status"] = audit_entry["status"]
            case["review_audit"] = audit_entry
            if modified_finding:
                case["imaging_evaluation"]["clinician_override_finding"] = modified_finding

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "success",
                "message": f"Case {case_id} successfully signed and audit logged.",
                "audit": audit_entry
            }).encode("utf-8"))
            return

        # 2. API: Image Analysis (Simulated / Custom Upload)
        if path == "/api/analyze-image":
            pathology_choice = payload.get("pathology_type", "pneumothorax")
            confidence = float(payload.get("confidence", 0.92))
            ctr = float(payload.get("ctr_ratio", 0.50))
            custom_id = payload.get("case_id", f"CUSTOM-{int(datetime.now().timestamp())}")

            eval_res = MedicalImagingTriageEngine.evaluate_case(
                primary_finding_key=pathology_choice,
                confidence=confidence,
                ctr_ratio=ctr
            )
            # Default normal vitals for ad-hoc image upload
            news = ClinicalIndices.calculate_news2(16, 96, False, 120, 75, "A", 36.8)
            prio = CasePrioritizer.calculate_composite_urgency(
                imaging_urgency=eval_res["base_urgency"],
                news2_score=news["total_score"],
                qsofa_positive=False,
                wait_time_minutes=5,
                has_critical_flag=(eval_res["urgency_tier"] == "STAT")
            )

            new_case = {
                "id": custom_id,
                "mrn": payload.get("mrn", f"UP-{int(datetime.now().timestamp()) % 100000}"),
                "patient_name": payload.get("patient_name", "Uploaded Custom Study"),
                "age": payload.get("age", 55),
                "sex": payload.get("sex", "M"),
                "encounter_type": "Ad-Hoc CDS Imaging Intake",
                "admit_time": datetime.now(timezone.utc).isoformat(),
                "wait_time_minutes": 5,
                "clinical_history": payload.get("clinical_history", "Screened via Direct Medical Image Upload"),
                "vitals": {
                    "heart_rate": 75,
                    "systolic_bp": 120,
                    "diastolic_bp": 80,
                    "respiratory_rate": 16,
                    "spo2": 96.0,
                    "supplemental_o2": False,
                    "temperature": 36.8,
                    "consciousness": "A"
                },
                "labs": {"wbc": 7.5, "lactate": 1.0, "creatinine": 0.9, "troponin": 0.01},
                "imaging": {
                    "modality": "CXR (Direct Upload)",
                    "finding_key": pathology_choice,
                    "confidence": confidence,
                    "ctr_ratio": ctr,
                    "description": f"AI Detected {eval_res['primary_finding']} with {int(confidence*100)}% confidence.",
                    "pathology_type": pathology_choice
                },
                "critical_flag": eval_res["urgency_tier"] == "STAT",
                "physician_status": "PENDING_REVIEW",
                "calculated_news2": news,
                "calculated_qsofa": {"score": 0, "positive": False, "criteria_met": []},
                "calculated_shock": {"shock_index": 0.62, "elevated": False, "status": "Normal"},
                "imaging_evaluation": eval_res,
                "triage_priority": prio,
                "review_audit": None
            }
            CASES_DB[custom_id] = new_case

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "success",
                "case": new_case
            }).encode("utf-8"))
            return

        # 3. API: Batch Tabular Dataset Prioritization
        if path == "/api/analyze-dataset":
            patients = payload.get("patients", [])
            if not patients:
                patients = get_tabular_clinical_dataset()

            results = []
            for p in patients:
                news = ClinicalIndices.calculate_news2(
                    respiratory_rate=int(p.get("respiratory_rate", 16)),
                    spo2=float(p.get("spo2", 97)),
                    supplemental_o2=bool(p.get("supplemental_o2", False)),
                    systolic_bp=int(p.get("systolic_bp", 120)),
                    heart_rate=int(p.get("heart_rate", 75)),
                    consciousness="V" if p.get("altered_mentation") else "A",
                    temperature=float(p.get("temperature", 37.0))
                )
                qsofa = ClinicalIndices.calculate_qsofa(
                    respiratory_rate=int(p.get("respiratory_rate", 16)),
                    systolic_bp=int(p.get("systolic_bp", 120)),
                    gcs_or_altered_mentation=bool(p.get("altered_mentation", False))
                )
                shock = ClinicalIndices.calculate_shock_index(
                    heart_rate=int(p.get("heart_rate", 75)),
                    systolic_bp=int(p.get("systolic_bp", 120))
                )
                # Feature attribution (SHAP-like risk driver identification)
                drivers = []
                if news["subscores"]["respiratory_rate"] > 0:
                    drivers.append(f"Tachypnea RR={p.get('respiratory_rate')} (+{news['subscores']['respiratory_rate']})")
                if news["subscores"]["spo2"] > 0:
                    drivers.append(f"Hypoxemia SpO2={p.get('spo2')}% (+{news['subscores']['spo2']})")
                if news["subscores"]["systolic_bp"] > 0:
                    drivers.append(f"Hypotension SBP={p.get('systolic_bp')} (+{news['subscores']['systolic_bp']})")
                if float(p.get("lactate", 1.0)) >= 2.0:
                    drivers.append(f"Hyperlactatemia Lactate={p.get('lactate')} mmol/L")
                if float(p.get("wbc", 8.0)) >= 14.0:
                    drivers.append(f"Leukocytosis WBC={p.get('wbc')} x10^9/L")

                results.append({
                    "patient_id": p.get("patient_id", "PT-X"),
                    "age": p.get("age"),
                    "sex": p.get("sex"),
                    "news2": news["total_score"],
                    "news2_risk": news["risk_level"],
                    "qsofa_score": qsofa["score"],
                    "qsofa_positive": qsofa["positive"],
                    "shock_index": shock["shock_index"],
                    "triage_recommendation": news["risk_level"].split()[0].upper(),
                    "top_risk_drivers": drivers
                })

            # Sort by NEWS2 descending
            results.sort(key=lambda x: x["news2"], reverse=True)

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "success",
                "cohort_size": len(results),
                "analyzed_patients": results
            }).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(b"Not Found")


def run(port=8080):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, CDSTriageHTTPHandler)
    print(f"CDS Triage Decision Support Server listening at http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
