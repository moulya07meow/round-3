# TriageVision CDS™ — Clinical Decision Support & Prioritization System

[![Regulatory](https://img.shields.io/badge/Regulatory-SaMD%20Class%20IIa-blue.svg)](https://www.fda.gov)
[![Standards](https://img.shields.io/badge/Standards-HL7%20FHIR%20R4%20%7C%20NEWS2-emerald.svg)](https://hl7.org/fhir)
[![Python](https://img.shields.io/badge/Python-3.9%2B-informational.svg)](https://www.python.org/)

**TriageVision CDS™** is an intelligent Clinical Decision Support (CDS) and dynamic case-prioritization platform. It analyzes approved medical images (Chest Radiographs) and clinical EHR datasets (vitals and laboratory biomarkers) to detect potential signs of disease, quantify severity, and dynamically prioritize cases for healthcare professionals.

---

## Key Features

1. **Medical Imaging Triage Engine (Chest Radiographs)**:
   - Automated detection of critical pathologies: *Tension Pneumothorax, Pneumothorax, Massive Pleural Effusion, Cardiomegaly with Acute Edema, Lobar Pneumonia, Solitary Pulmonary Nodule, and Atelectasis*.
   - **Grad-CAM Attention Saliency**: 2D heatmaps highlighting neural network spatial focus.
   - **Cardiothoracic Ratio (CTR) Caliper**: Quantitative cardiomegaly assessment ($CTR = (A+B)/C$).
   - 95% Confidence Intervals & differential diagnostic rankings.

2. **Physiological Deterioration & EHR Triage**:
   - **NEWS2 (National Early Warning Score 2)**: Full compliance with Royal College of Physicians clinical scoring standard.
   - **qSOFA & Shock Index**: Immediate sepsis-3 deterioration alerts and hemodynamic collapse risk index ($HR / SBP$).
   - **Explainable AI (XAI)**: Identifies key physiological risk drivers (tachypnea, hyperlactatemia, hypoxemia, altered mental status).

3. **Dynamic Priority Queue**:
   - Stratifies reading worklists into 4 urgency tiers:
     - **STAT (&lt; 15 min turnaround)**: Life-threatening cardiopulmonary emergencies.
     - **URGENT (&lt; 60 min turnaround)**: High-acuity acute decompensations.
     - **EXPEDITED (&lt; 120 min turnaround)**: Significant findings / surveillance.
     - **ROUTINE (&lt; 480 min turnaround)**: Normal screenings and stable baseline cases.
   - Wait-time degradation algorithm prevents queue starvation.

4. **Human-in-the-Loop Governance & Interoperability**:
   - Mandatory physician review: Approve, Modify, or Override.
   - Digital audit trail logging compliant with FDA SaMD 21 CFR 820.
   - 1-Click export to **HL7 FHIR R4 `DiagnosticReport` / `Observation` JSON** and **HL7 v2.5.1 `ORU^R01`** messages.

---

## Project Structure

```
clinical-decision-support/
├── server.py                       # REST API Server & Web Server
├── cds_triage_cli.py               # Batch CLI Triage Utility with CSV export
├── cds_engine/
│   ├── triage_models.py            # NEWS2, qSOFA, Shock Index, and Prioritization algorithms
│   ├── data_loader.py              # Clinical benchmark cases & cohort generators
│   └── fhir_exporter.py            # HL7 FHIR R4 Bundle & HL7 v2.5.1 ORU exporters
├── sample_data/
│   ├── inpatient_cohort.csv        # Multi-parameter test cohort
│   └── prioritized_cohort.csv      # Stratified results from batch CLI run
├── tests/
│   └── test_triage.py              # Automated test suite
└── web/
    ├── index.html                  # Clinical workstation UI
    ├── styles.css                  # Dark radiology styling
    └── app.js                      # Canvas DICOM & Grad-CAM blending engine
```

---

## Quickstart

### 1. Launch the Web Workstation
```bash
python3 server.py 8080
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

### 2. Batch Clinical Cohort Triage via CLI
```bash
# Run benchmark validation (100% STAT sensitivity)
python3 cds_triage_cli.py --benchmark

# Batch process patient dataset CSV
python3 cds_triage_cli.py --file sample_data/inpatient_cohort.csv --output sample_data/prioritized_cohort.csv
```

### 3. Run Test Suite
```bash
python3 -m unittest discover -s tests
```

---

## Regulatory & Clinical Disclaimer
*TriageVision CDS™ is an investigational Clinical Decision Support aid (Class IIa SaMD). It is designed to assist prioritization and region highlighting, and does not replace independent diagnostic interpretation by a licensed board-certified medical professional.*
