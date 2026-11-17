/**
 * TriageVision CDS™ — Clinical Decision Support & PACS Triage Workstation
 * Client-Side Application Logic & Interactive Canvas Engine
 */

// Application State
const state = {
  cases: [],
  activeCaseId: null,
  activeFilter: 'ALL',
  searchQuery: '',
  viewMode: 'split', // 'imaging', 'clinical', 'split'
  cohortData: [],
  auditLog: [],
  canvasOptions: {
    windowLevel: 'standard',
    heatmapOpacity: 0.65,
    showROI: true,
    showCTR: false,
    inverted: false
  }
};

// DOM Elements
const elements = {
  worklistContainer: document.getElementById('worklist-container'),
  totalCasesBadge: document.getElementById('total-cases-badge'),
  worklistSearch: document.getElementById('worklist-search'),
  filterTabs: document.querySelectorAll('.filter-tab'),
  
  // Header counters
  counterStat: document.querySelector('#counter-stat .count-val'),
  counterUrgent: document.querySelector('#counter-urgent .count-val'),
  counterExpedited: document.querySelector('#counter-expedited .count-val'),
  counterRoutine: document.querySelector('#counter-routine .count-val'),
  auditCount: document.getElementById('audit-count'),
  
  // Patient Banner
  bannerMrn: document.getElementById('banner-mrn'),
  bannerName: document.getElementById('banner-name'),
  bannerDemog: document.getElementById('banner-demog'),
  bannerUrgencyBadge: document.getElementById('banner-urgency-badge'),

  // Viewer modes
  tabImaging: document.getElementById('tab-imaging'),
  tabClinical: document.getElementById('tab-clinical'),
  tabSplit: document.getElementById('tab-split'),
  viewerBody: document.querySelector('.viewer-body-container'),
  imagingBox: document.getElementById('imaging-box'),
  clinicalBox: document.getElementById('clinical-box'),

  // Canvas & Tools
  canvas: document.getElementById('dicomCanvas'),
  wlPreset: document.getElementById('wl-preset'),
  heatmapSlider: document.getElementById('heatmap-slider'),
  heatmapVal: document.getElementById('heatmap-val'),
  btnToggleROI: document.getElementById('btn-toggle-roi'),
  btnToggleCTR: document.getElementById('btn-toggle-ctr'),
  btnToggleInvert: document.getElementById('btn-toggle-invert'),
  btnResetView: document.getElementById('btn-reset-view'),
  overlayFindingTag: document.getElementById('overlay-finding-tag'),
  overlayCtrTag: document.getElementById('overlay-ctr-tag'),

  // Clinical EHR Elements
  news2BadgeLarge: document.getElementById('news2-large-badge'),
  valHr: document.getElementById('val-hr'),
  statusHr: document.getElementById('status-hr'),
  valBp: document.getElementById('val-bp'),
  statusBp: document.getElementById('status-bp'),
  valRr: document.getElementById('val-rr'),
  statusRr: document.getElementById('status-rr'),
  valSpo2: document.getElementById('val-spo2'),
  statusSpo2: document.getElementById('status-spo2'),
  valTemp: document.getElementById('val-temp'),
  statusTemp: document.getElementById('status-temp'),
  valAcvpu: document.getElementById('val-acvpu'),
  statusAcvpu: document.getElementById('status-acvpu'),
  valQsofa: document.getElementById('val-qsofa'),
  valShock: document.getElementById('val-shock'),
  xaiDriversList: document.getElementById('xai-drivers-list'),
  labsChipsContainer: document.getElementById('labs-chips-container'),

  // Decision Panel Elements
  activeSignPill: document.getElementById('active-sign-pill'),
  aiConfBadge: document.getElementById('ai-conf-badge'),
  aiFindingTitle: document.getElementById('ai-finding-title'),
  aiFindingDesc: document.getElementById('ai-finding-desc'),
  diffBarsContainer: document.getElementById('diff-bars-container'),
  guidelineText: document.getElementById('guideline-text'),
  reviewDecision: document.getElementById('review-decision'),
  overrideGroup: document.getElementById('override-finding-group'),
  overrideFindingInput: document.getElementById('override-finding-input'),
  clinicianNotes: document.getElementById('clinician-notes'),
  clinicianSig: document.getElementById('clinician-sig'),
  btnSignCase: document.getElementById('btn-sign-case'),
  btnEscalateStat: document.getElementById('btn-escalate-stat'),
  btnViewFhir: document.getElementById('btn-view-fhir'),
  btnViewHl7: document.getElementById('btn-view-hl7'),
  btnDownloadPdf: document.getElementById('btn-download-pdf'),

  // Modals
  modalBatch: document.getElementById('modal-batch'),
  btnBatchModal: document.getElementById('btn-batch-modal'),
  btnCloseBatch: document.getElementById('btn-close-batch'),
  btnCloseBatch2: document.getElementById('btn-close-batch-2'),
  cohortTbody: document.getElementById('cohort-tbody'),
  btnExportCohortCsv: document.getElementById('btn-export-cohort-csv'),

  modalUpload: document.getElementById('modal-upload'),
  btnUploadModal: document.getElementById('btn-upload-modal'),
  btnCloseUpload: document.getElementById('btn-close-upload'),
  btnCancelUpload: document.getElementById('btn-cancel-upload'),
  btnSubmitUpload: document.getElementById('btn-submit-upload'),
  uploadPresetSelect: document.getElementById('upload-preset-select'),
  uploadMrn: document.getElementById('upload-mrn'),
  uploadAge: document.getElementById('upload-age'),
  uploadSex: document.getElementById('upload-sex'),
  uploadHistory: document.getElementById('upload-history'),

  modalFhir: document.getElementById('modal-fhir'),
  modalFhirTitle: document.getElementById('modal-fhir-title'),
  fhirJsonCode: document.getElementById('fhir-json-code'),
  btnCloseFhir: document.getElementById('btn-close-fhir'),
  btnDoneFhir: document.getElementById('btn-done-fhir'),
  btnCopyFhir: document.getElementById('btn-copy-fhir'),

  // Audit Drawer
  auditDrawer: document.getElementById('audit-drawer'),
  drawerBackdrop: document.getElementById('drawer-backdrop'),
  btnAuditDrawer: document.getElementById('btn-audit-drawer'),
  btnCloseDrawer: document.getElementById('btn-close-drawer'),
  auditLogItems: document.getElementById('audit-log-items'),

  // Toast
  toast: document.getElementById('toast')
};

// Initializer
document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  fetchCases();
  fetchAuditLog();
  // Set default view mode to Split
  setViewMode('split');
});

function initEventListeners() {
  // Search and Filter
  elements.worklistSearch.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.toLowerCase();
    renderWorklist();
  });

  elements.filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      elements.filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.activeFilter = tab.dataset.filter;
      renderWorklist();
    });
  });

  // View Mode Tabs
  elements.tabImaging.addEventListener('click', () => setViewMode('imaging'));
  elements.tabClinical.addEventListener('click', () => setViewMode('clinical'));
  elements.tabSplit.addEventListener('click', () => setViewMode('split'));

  // Canvas Controls
  elements.wlPreset.addEventListener('change', (e) => {
    state.canvasOptions.windowLevel = e.target.value;
    renderRadiologyCanvas();
  });

  elements.heatmapSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value, 10);
    state.canvasOptions.heatmapOpacity = val / 100.0;
    elements.heatmapVal.textContent = `${val}%`;
    renderRadiologyCanvas();
  });

  elements.btnToggleROI.addEventListener('click', () => {
    state.canvasOptions.showROI = !state.canvasOptions.showROI;
    elements.btnToggleROI.classList.toggle('active', state.canvasOptions.showROI);
    renderRadiologyCanvas();
  });

  elements.btnToggleCTR.addEventListener('click', () => {
    state.canvasOptions.showCTR = !state.canvasOptions.showCTR;
    elements.btnToggleCTR.classList.toggle('active', state.canvasOptions.showCTR);
    renderRadiologyCanvas();
  });

  elements.btnToggleInvert.addEventListener('click', () => {
    state.canvasOptions.inverted = !state.canvasOptions.inverted;
    elements.btnToggleInvert.classList.toggle('active', state.canvasOptions.inverted);
    renderRadiologyCanvas();
  });

  elements.btnResetView.addEventListener('click', () => {
    state.canvasOptions.windowLevel = 'standard';
    elements.wlPreset.value = 'standard';
    state.canvasOptions.heatmapOpacity = 0.65;
    elements.heatmapSlider.value = 65;
    elements.heatmapVal.textContent = '65%';
    state.canvasOptions.showROI = true;
    elements.btnToggleROI.classList.add('active');
    state.canvasOptions.showCTR = false;
    elements.btnToggleCTR.classList.remove('active');
    state.canvasOptions.inverted = false;
    elements.btnToggleInvert.classList.remove('active');
    renderRadiologyCanvas();
  });

  // Review Decision change
  elements.reviewDecision.addEventListener('change', (e) => {
    if (e.target.value === 'MODIFIED' || e.target.value === 'OVERRIDDEN') {
      elements.overrideGroup.style.display = 'block';
    } else {
      elements.overrideGroup.style.display = 'none';
    }
  });

  // Physician Sign-off
  elements.btnSignCase.addEventListener('click', commitPhysicianReview);
  elements.btnEscalateStat.addEventListener('click', () => {
    elements.reviewDecision.value = 'ESCALATED';
    elements.clinicianNotes.value = 'CRITICAL ALERT: Immediate interventional radiology / surgical consult summoned.';
    commitPhysicianReview();
  });

  // FHIR / HL7 / PDF
  elements.btnViewFhir.addEventListener('click', openFhirModal);
  elements.btnViewHl7.addEventListener('click', openHl7Modal);
  elements.btnDownloadPdf.addEventListener('click', exportClinicalReport);

  // Modals & Drawers
  elements.btnBatchModal.addEventListener('click', openBatchModal);
  elements.btnCloseBatch.addEventListener('click', () => elements.modalBatch.classList.remove('open'));
  elements.btnCloseBatch2.addEventListener('click', () => elements.modalBatch.classList.remove('open'));
  elements.btnExportCohortCsv.addEventListener('click', exportCohortCsv);

  elements.btnUploadModal.addEventListener('click', () => elements.modalUpload.classList.add('open'));
  elements.btnCloseUpload.addEventListener('click', () => elements.modalUpload.classList.remove('open'));
  elements.btnCancelUpload.addEventListener('click', () => elements.modalUpload.classList.remove('open'));
  elements.btnSubmitUpload.addEventListener('click', submitImageUpload);

  elements.btnCloseFhir.addEventListener('click', () => elements.modalFhir.classList.remove('open'));
  elements.btnDoneFhir.addEventListener('click', () => elements.modalFhir.classList.remove('open'));
  elements.btnCopyFhir.addEventListener('click', () => {
    navigator.clipboard.writeText(elements.fhirJsonCode.textContent);
    showToast('Copied FHIR/HL7 payload to clipboard');
  });

  elements.btnAuditDrawer.addEventListener('click', () => {
    elements.auditDrawer.classList.add('open');
    elements.drawerBackdrop.classList.add('open');
    renderAuditDrawer();
  });
  elements.btnCloseDrawer.addEventListener('click', closeDrawer);
  elements.drawerBackdrop.addEventListener('click', closeDrawer);
}

function closeDrawer() {
  elements.auditDrawer.classList.remove('open');
  elements.drawerBackdrop.classList.remove('open');
}

function showToast(msg) {
  elements.toast.textContent = msg;
  elements.toast.classList.add('show');
  setTimeout(() => elements.toast.classList.remove('show'), 3500);
}

function setViewMode(mode) {
  state.viewMode = mode;
  elements.tabImaging.classList.toggle('active', mode === 'imaging');
  elements.tabClinical.classList.toggle('active', mode === 'clinical');
  elements.tabSplit.classList.toggle('active', mode === 'split');

  if (mode === 'imaging') {
    elements.viewerBody.classList.remove('split-mode');
    elements.imagingBox.style.display = 'flex';
    elements.clinicalBox.style.display = 'none';
  } else if (mode === 'clinical') {
    elements.viewerBody.classList.remove('split-mode');
    elements.imagingBox.style.display = 'none';
    elements.clinicalBox.style.display = 'flex';
  } else {
    // Split
    elements.viewerBody.classList.add('split-mode');
    elements.imagingBox.style.display = 'flex';
    elements.clinicalBox.style.display = 'flex';
  }

  // Redraw canvas if visible
  if (mode !== 'clinical') {
    renderRadiologyCanvas();
  }
}

// ---------------------------------------------------------------------------
// DATA FETCHING & WORKLIST
// ---------------------------------------------------------------------------

async function fetchCases() {
  try {
    const res = await fetch('/api/cases');
    const data = await res.json();
    if (data.status === 'success') {
      state.cases = data.cases;
      updateHeaderCounters(data.summary);
      if (!state.activeCaseId && state.cases.length > 0) {
        state.activeCaseId = state.cases[0].id;
      }
      renderWorklist();
      loadActiveCase();
    }
  } catch (err) {
    console.error('Failed to fetch cases:', err);
  }
}

function updateHeaderCounters(summary) {
  elements.counterStat.textContent = summary.stat;
  elements.counterUrgent.textContent = summary.urgent;
  elements.counterExpedited.textContent = summary.expedited;
  elements.counterRoutine.textContent = summary.routine;

  document.getElementById('f-all').textContent = state.cases.length;
  document.getElementById('f-stat').textContent = summary.stat;
  document.getElementById('f-urg').textContent = summary.urgent;
  document.getElementById('f-pend').textContent = summary.pending_review;
  document.getElementById('f-sign').textContent = state.cases.length - summary.pending_review;
}

function renderWorklist() {
  const container = elements.worklistContainer;
  container.innerHTML = '';

  const filtered = state.cases.filter(c => {
    // Filter tab
    if (state.activeFilter === 'STAT' && c.triage_priority.priority_tier !== 'STAT') return false;
    if (state.activeFilter === 'URGENT' && c.triage_priority.priority_tier !== 'URGENT') return false;
    if (state.activeFilter === 'PENDING' && c.physician_status !== 'PENDING_REVIEW') return false;
    if (state.activeFilter === 'SIGNED' && c.physician_status === 'PENDING_REVIEW') return false;

    // Search query
    if (state.searchQuery) {
      const q = state.searchQuery;
      const match = c.mrn.toLowerCase().includes(q) ||
                    c.patient_name.toLowerCase().includes(q) ||
                    c.imaging_evaluation.primary_finding.toLowerCase().includes(q) ||
                    c.encounter_type.toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });

  elements.totalCasesBadge.textContent = `${filtered.length} cases`;

  filtered.forEach(c => {
    const tier = c.triage_priority.priority_tier;
    const card = document.createElement('div');
    card.className = `case-card card-${tier.toLowerCase()} ${c.id === state.activeCaseId ? 'active' : ''}`;
    card.onclick = () => {
      state.activeCaseId = c.id;
      renderWorklist();
      loadActiveCase();
    };

    const isSigned = c.physician_status !== 'PENDING_REVIEW';
    const isOverdue = c.triage_priority.is_overdue;
    const waitTime = c.wait_time_minutes;
    const maxTat = c.triage_priority.target_tat_minutes;

    card.innerHTML = `
      <div class="card-top">
        <span class="badge-priority badge-${tier.toLowerCase()}">${tier}</span>
        <span class="urgency-score-mini">Score: <span>${c.triage_priority.composite_urgency}</span>/100</span>
      </div>
      <div class="card-mrn">${c.mrn} • ${c.patient_name}</div>
      <div class="card-demog">${c.age}yo ${c.sex} • ${c.encounter_type}</div>
      <div class="card-finding">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        ${c.imaging_evaluation.primary_finding} (${c.imaging_evaluation.confidence_percent}%)
      </div>
      <div class="card-bottom">
        <span class="wait-timer ${isOverdue ? 'overdue' : ''}">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          Wait: ${waitTime}m / ${maxTat}m ${isOverdue ? '⚠️ STAT OVERDUE' : ''}
        </span>
        <span class="news2-pill-mini ${c.calculated_news2.total_score >= 7 ? 'high' : ''}">NEWS2: ${c.calculated_news2.total_score}</span>
        <span>${isSigned ? '✅ Signed' : '⏳ Pending'}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function getActiveCase() {
  return state.cases.find(c => c.id === state.activeCaseId) || state.cases[0];
}

function loadActiveCase() {
  const c = getActiveCase();
  if (!c) return;

  // Banner
  elements.bannerMrn.textContent = `MRN: ${c.mrn}`;
  elements.bannerName.textContent = c.patient_name;
  elements.bannerDemog.textContent = `${c.age}yo ${c.sex} • ${c.encounter_type}`;
  
  const tier = c.triage_priority.priority_tier;
  elements.bannerUrgencyBadge.innerHTML = `
    <span class="badge-priority badge-${tier.toLowerCase()}">${tier} PRIORITY</span>
    <span class="urgency-score-pill">Urgency: ${c.triage_priority.composite_urgency}/100</span>
  `;

  // Canvas Overlays
  elements.overlayFindingTag.textContent = `${c.imaging_evaluation.primary_finding.toUpperCase()} (${c.imaging_evaluation.confidence_percent}%)`;
  elements.overlayCtrTag.textContent = `CTR: ${c.imaging_evaluation.cardiothoracic_ratio} (${c.imaging_evaluation.cardiomegaly_present ? 'Cardiomegaly' : 'Normal'})`;

  // Physiological Vitals & NEWS2
  const v = c.vitals;
  elements.valHr.textContent = v.heart_rate;
  elements.statusHr.textContent = v.heart_rate > 100 ? `Tachycardia (+${c.calculated_news2.subscores.heart_rate})` : 'Normal (+0)';
  elements.statusHr.className = `vital-status ${v.heart_rate > 100 ? 'status-alert' : 'status-ok'}`;

  elements.valBp.textContent = `${v.systolic_bp}/${v.diastolic_bp}`;
  elements.statusBp.textContent = v.systolic_bp <= 90 ? 'Hypotension (+3)' : (v.systolic_bp <= 100 ? 'Low SBP (+2)' : 'Normal (+0)');
  elements.statusBp.className = `vital-status ${v.systolic_bp <= 100 ? 'status-crit' : 'status-ok'}`;

  elements.valRr.textContent = v.respiratory_rate;
  elements.statusRr.textContent = v.respiratory_rate >= 25 ? 'Tachypnea (+3)' : (v.respiratory_rate >= 21 ? 'Elevated (+2)' : 'Normal (+0)');
  elements.statusRr.className = `vital-status ${v.respiratory_rate >= 21 ? 'status-crit' : 'status-ok'}`;

  elements.valSpo2.textContent = `${v.spo2}%`;
  elements.statusSpo2.textContent = v.supplemental_o2 ? 'on O2 (+2)' : 'Room Air (+0)';
  elements.statusSpo2.className = `vital-status ${v.spo2 < 92 ? 'status-crit' : (v.supplemental_o2 ? 'status-alert' : 'status-ok')}`;

  elements.valTemp.textContent = v.temperature;
  elements.statusTemp.textContent = v.temperature >= 39.1 ? 'High Pyrexia (+2)' : (v.temperature <= 35.0 ? 'Hypothermia (+3)' : 'Normal (+0)');
  elements.statusTemp.className = `vital-status ${v.temperature >= 38.1 || v.temperature <= 35.0 ? 'status-alert' : 'status-ok'}`;

  const acvpuMap = { 'A': 'Alert (A)', 'C': 'Confusion (C)', 'V': 'Voice (V)', 'P': 'Pain (P)', 'U': 'Unresponsive (U)' };
  elements.valAcvpu.textContent = acvpuMap[v.consciousness] || v.consciousness;
  elements.statusAcvpu.textContent = v.consciousness === 'A' ? 'Alert (+0)' : 'Altered Mentation (+3)';
  elements.statusAcvpu.className = `vital-status ${v.consciousness === 'A' ? 'status-ok' : 'status-crit'}`;

  // NEWS2 Badge
  const newsTotal = c.calculated_news2.total_score;
  elements.news2BadgeLarge.textContent = `NEWS2 Score: ${newsTotal} (${c.calculated_news2.risk_level.split('(')[0].trim()})`;
  elements.news2BadgeLarge.style.color = c.calculated_news2.color === 'red' ? '#F87171' : (c.calculated_news2.color === 'amber' ? '#FBBF24' : '#34D399');

  // qSOFA & Shock Index
  elements.valQsofa.textContent = `Score ${c.calculated_qsofa.score}/3 (${c.calculated_qsofa.positive ? 'Positive' : 'Low Risk'})`;
  elements.valQsofa.style.color = c.calculated_qsofa.positive ? '#EF4444' : '#10B981';

  elements.valShock.textContent = `${c.calculated_shock.shock_index} (${c.calculated_shock.status})`;
  elements.valShock.style.color = c.calculated_shock.elevated ? '#EF4444' : '#10B981';

  // Explainable AI (XAI) feature attributions
  renderExplainabilityBars(c);

  // Labs
  renderLabChips(c.labs);

  // Decision Panel
  const evalData = c.imaging_evaluation;
  elements.aiFindingTitle.textContent = evalData.primary_finding;
  elements.aiFindingDesc.textContent = c.imaging.description;
  elements.aiConfBadge.textContent = `${evalData.confidence_percent}% Conf (95% CI: ${Math.round(evalData.confidence_interval_95[0]*100)}-${Math.round(evalData.confidence_interval_95[1]*100)}%)`;
  elements.guidelineText.textContent = evalData.clinical_guidelines;

  // Differential Findings Bars
  renderDifferentialBars(evalData.differential_findings);

  // Sign Status
  const isSigned = c.physician_status !== 'PENDING_REVIEW';
  elements.activeSignPill.textContent = isSigned ? `Signed (${c.physician_status})` : 'Pending Sign-off';
  elements.activeSignPill.className = `sign-status-pill ${isSigned ? 'signed' : 'pending'}`;

  if (c.review_audit) {
    elements.clinicianNotes.value = c.review_audit.rationale || '';
  } else {
    elements.clinicianNotes.value = `Verified preliminary CDS findings. Clinical presentation concordant with ${evalData.primary_finding}.`;
  }

  // Draw Canvas
  renderRadiologyCanvas();
}

function renderExplainabilityBars(c) {
  const container = elements.xaiDriversList;
  container.innerHTML = '';

  const drivers = [];
  const sub = c.calculated_news2.subscores;

  if (sub.respiratory_rate > 0) {
    drivers.push({ name: `Tachypnea (RR ${c.vitals.respiratory_rate})`, weight: sub.respiratory_rate * 25, impact: `+${sub.respiratory_rate} NEWS2` });
  }
  if (sub.systolic_bp > 0) {
    drivers.push({ name: `Hypotension (SBP ${c.vitals.systolic_bp})`, weight: sub.systolic_bp * 30, impact: `+${sub.systolic_bp} NEWS2` });
  }
  if (sub.spo2 > 0) {
    drivers.push({ name: `Hypoxemia (SpO2 ${c.vitals.spo2}%)`, weight: sub.spo2 * 25, impact: `+${sub.spo2} NEWS2` });
  }
  if (c.labs && c.labs.lactate >= 2.0) {
    drivers.push({ name: `Hyperlactatemia (${c.labs.lactate} mmol/L)`, weight: 65, impact: 'Metabolic Distress' });
  }
  if (c.calculated_shock.elevated) {
    drivers.push({ name: `Shock Index Elevation (${c.calculated_shock.shock_index})`, weight: 70, impact: 'Hemodynamic Risk' });
  }
  if (drivers.length === 0) {
    drivers.push({ name: 'All Vitals Within Normal Baseline', weight: 10, impact: 'Stable Physiologic State' });
  }

  drivers.forEach(d => {
    const item = document.createElement('div');
    item.className = 'xai-item';
    item.innerHTML = `
      <div class="xai-label-row">
        <span>${d.name}</span>
        <strong style="color: #F87171;">${d.impact}</strong>
      </div>
      <div class="xai-bar-track">
        <div class="xai-bar-fill" style="width: ${d.weight}%"></div>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderLabChips(labs) {
  const container = elements.labsChipsContainer;
  container.innerHTML = '';
  if (!labs) return;

  const labMeta = {
    wbc: { name: 'WBC', unit: 'x10^9/L', normal: [4.0, 11.0] },
    lactate: { name: 'Lactate', unit: 'mmol/L', normal: [0.5, 2.0] },
    creatinine: { name: 'Creatinine', unit: 'mg/dL', normal: [0.6, 1.2] },
    troponin: { name: 'Troponin I', unit: 'ng/mL', normal: [0.0, 0.04] },
    pao2_fio2: { name: 'PaO2/FiO2', unit: 'mmHg', normal: [300, 500] },
    bnp: { name: 'BNP', unit: 'pg/mL', normal: [0, 100] },
    crp: { name: 'CRP', unit: 'mg/L', normal: [0, 10] },
    hemoglobin: { name: 'Hemoglobin', unit: 'g/dL', normal: [12.0, 16.0] }
  };

  Object.entries(labs).forEach(([k, val]) => {
    const m = labMeta[k] || { name: k.toUpperCase(), unit: '', normal: [0, 999] };
    const isAbnormal = val < m.normal[0] || val > m.normal[1];
    const chip = document.createElement('div');
    chip.className = `lab-chip ${isAbnormal ? 'abnormal' : ''}`;
    chip.innerHTML = `
      <span class="lab-n">${m.name} (${m.unit})</span>
      <span class="lab-v">${val} ${isAbnormal ? '⚠️' : ''}</span>
    `;
    container.appendChild(chip);
  });
}

function renderDifferentialBars(diffList) {
  const container = elements.diffBarsContainer;
  container.innerHTML = '';
  if (!diffList) return;

  diffList.forEach(item => {
    const pct = Math.round(item.probability * 100);
    const div = document.createElement('div');
    div.className = 'diff-item';
    div.innerHTML = `
      <span class="diff-name">${item.finding}</span>
      <span class="diff-pct">${pct}%</span>
    `;
    container.appendChild(div);
  });
}

// ---------------------------------------------------------------------------
// PROCEDURAL DICOM / RADIOLOGY & GRAD-CAM CANVAS ENGINE
// ---------------------------------------------------------------------------

function renderRadiologyCanvas() {
  const canvas = elements.canvas;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  const c = getActiveCase();
  if (!c) return;

  const pathology = c.imaging.finding_key;
  const roi = c.imaging_evaluation.region_of_interest;
  const ctrRatio = c.imaging_evaluation.cardiothoracic_ratio;

  // Clear background
  ctx.fillStyle = '#020617';
  ctx.fillRect(0, 0, w, h);

  // Contrast / Filter Presets
  let brightness = 1.0;
  let contrast = 1.0;
  const wl = state.canvasOptions.windowLevel;
  if (wl === 'lung') {
    contrast = 1.35;
    brightness = 0.95;
  } else if (wl === 'mediastinum') {
    contrast = 1.5;
    brightness = 1.15;
  } else if (wl === 'bone') {
    contrast = 1.7;
    brightness = 0.85;
  }

  // 1. Draw Anatomical Thorax Base (Subtle radiopacity)
  drawThoracicAnatomy(ctx, w, h, pathology, ctrRatio);

  // 2. Draw Pathology-Specific Findings (Pneumothorax, Effusion, Consolidation, etc.)
  drawPathologySignatures(ctx, w, h, pathology);

  // 3. Draw Grad-CAM Attention Heatmap
  if (state.canvasOptions.heatmapOpacity > 0.01) {
    drawGradCamHeatmap(ctx, w, h, roi, state.canvasOptions.heatmapOpacity);
  }

  // 4. Draw Region of Interest (ROI) Bounding Box
  if (state.canvasOptions.showROI && roi.w > 0.08) {
    drawRoiBoundingBox(ctx, w, h, roi, c.imaging_evaluation.primary_finding);
  }

  // 5. Draw Cardiothoracic Ratio (CTR) Caliper
  if (state.canvasOptions.showCTR) {
    drawCtrCaliper(ctx, w, h, ctrRatio);
  }

  // 6. Handle Invert Filter
  if (state.canvasOptions.inverted) {
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;
    for (let i = 0; i < data.length; i += 4) {
      data[i] = 255 - data[i];         // R
      data[i + 1] = 255 - data[i + 1]; // G
      data[i + 2] = 255 - data[i + 2]; // B
    }
    ctx.putImageData(imgData, 0, 0);
  }
}

function drawThoracicAnatomy(ctx, w, h, pathology, ctrRatio) {
  ctx.save();

  // Thoracic soft tissue contour
  const cx = w * 0.5;
  const cy = h * 0.52;

  // Lungs Silhouette (Translucent aerated lungs: darker gray in X-ray)
  // Left Lung (anatomical right, screen left)
  ctx.fillStyle = '#111827';
  ctx.beginPath();
  ctx.ellipse(w * 0.32, h * 0.50, w * 0.16, h * 0.34, -0.05, 0, Math.PI * 2);
  ctx.fill();

  // Right Lung (anatomical left, screen right)
  ctx.beginPath();
  ctx.ellipse(w * 0.68, h * 0.50, w * 0.16, h * 0.34, 0.05, 0, Math.PI * 2);
  ctx.fill();

  // Rib Cages (Horizontal curved translucent bands)
  ctx.strokeStyle = 'rgba(203, 213, 225, 0.15)';
  ctx.lineWidth = 9;
  for (let i = 0; i < 9; i++) {
    const ry = h * (0.24 + i * 0.065);
    // Left ribs
    ctx.beginPath();
    ctx.moveTo(w * 0.48, ry - 10);
    ctx.quadraticCurveTo(w * 0.30, ry + 12, w * 0.14, ry + 3);
    ctx.stroke();
    // Right ribs
    ctx.beginPath();
    ctx.moveTo(w * 0.52, ry - 10);
    ctx.quadraticCurveTo(w * 0.70, ry + 12, w * 0.86, ry + 3);
    ctx.stroke();
  }

  // Clavicles
  ctx.strokeStyle = 'rgba(241, 245, 249, 0.35)';
  ctx.lineWidth = 10;
  // Left clavicle
  ctx.beginPath();
  ctx.moveTo(w * 0.48, h * 0.22);
  ctx.quadraticCurveTo(w * 0.32, h * 0.18, w * 0.16, h * 0.20);
  ctx.stroke();
  // Right clavicle
  ctx.beginPath();
  ctx.moveTo(w * 0.52, h * 0.22);
  ctx.quadraticCurveTo(w * 0.68, h * 0.18, w * 0.84, h * 0.20);
  ctx.stroke();

  // Spinal Column / Vertebrae (Central vertical radiopaque density)
  ctx.fillStyle = 'rgba(148, 163, 184, 0.22)';
  for (let y = h * 0.15; y < h * 0.85; y += 18) {
    ctx.fillRect(w * 0.47, y, w * 0.06, 12);
  }

  // Diaphragm arches (bilateral domed hemidiaphragms)
  ctx.fillStyle = 'rgba(226, 232, 240, 0.25)';
  // Left hemidiaphragm
  ctx.beginPath();
  ctx.moveTo(w * 0.12, h * 0.88);
  ctx.quadraticCurveTo(w * 0.32, h * 0.72, w * 0.50, h * 0.80);
  ctx.lineTo(w * 0.50, h * 0.95);
  ctx.lineTo(w * 0.12, h * 0.95);
  ctx.closePath();
  ctx.fill();

  // Right hemidiaphragm
  ctx.beginPath();
  ctx.moveTo(w * 0.50, h * 0.80);
  ctx.quadraticCurveTo(w * 0.68, h * 0.70, w * 0.88, h * 0.88);
  ctx.lineTo(w * 0.88, h * 0.95);
  ctx.lineTo(w * 0.50, h * 0.95);
  ctx.closePath();
  ctx.fill();

  // Cardiac Silhouette (Central radiopaque shadow)
  // Mediastinum width depends on CTR
  const heartW = w * (ctrRatio * 0.48);
  const heartH = h * 0.28;
  const shiftLeft = (pathology === 'tension_pneumothorax') ? -25 : 0; // Mediastinal shift away from tension pneumo

  ctx.fillStyle = 'rgba(241, 245, 249, 0.42)';
  ctx.beginPath();
  ctx.ellipse(w * 0.48 + shiftLeft, h * 0.62, heartW, heartH, 0.2, 0, Math.PI * 2);
  ctx.fill();

  // Pulmonary vascular markings (bronchovascular tree arborization)
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.lineWidth = 2;
  // Left hilum vessels
  ctx.beginPath();
  ctx.moveTo(w * 0.42, h * 0.48);
  ctx.lineTo(w * 0.30, h * 0.42);
  ctx.moveTo(w * 0.42, h * 0.50);
  ctx.lineTo(w * 0.26, h * 0.56);
  ctx.stroke();
  // Right hilum vessels
  ctx.beginPath();
  ctx.moveTo(w * 0.58, h * 0.48);
  ctx.lineTo(w * 0.70, h * 0.42);
  ctx.moveTo(w * 0.58, h * 0.50);
  ctx.lineTo(w * 0.74, h * 0.56);
  ctx.stroke();

  ctx.restore();
}

function drawPathologySignatures(ctx, w, h, pathology) {
  ctx.save();

  if (pathology === 'tension_pneumothorax') {
    // Right Hemithorax (screen right): completely hyperlucent (black), absent markings,
    // sharp white visceral pleural edge line displaced inward, flattened diaphragm.
    ctx.fillStyle = '#000000';
    ctx.fillRect(w * 0.66, h * 0.24, w * 0.24, h * 0.55);

    // Collapsed lung edge (visceral pleural line)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(w * 0.65, h * 0.26);
    ctx.quadraticCurveTo(w * 0.63, h * 0.52, w * 0.66, h * 0.75);
    ctx.stroke();

    // Flattened right hemidiaphragm
    ctx.fillStyle = 'rgba(226, 232, 240, 0.35)';
    ctx.beginPath();
    ctx.moveTo(w * 0.60, h * 0.84);
    ctx.lineTo(w * 0.90, h * 0.84);
    ctx.lineTo(w * 0.90, h * 0.95);
    ctx.lineTo(w * 0.60, h * 0.95);
    ctx.closePath();
    ctx.fill();

  } else if (pathology === 'pneumothorax') {
    // Apical crescent pneumothorax
    ctx.fillStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo(w * 0.68, h * 0.20);
    ctx.quadraticCurveTo(w * 0.82, h * 0.22, w * 0.86, h * 0.35);
    ctx.lineTo(w * 0.86, h * 0.20);
    ctx.closePath();
    ctx.fill();

    // Pleural line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.68, h * 0.20);
    ctx.quadraticCurveTo(w * 0.78, h * 0.24, w * 0.84, h * 0.36);
    ctx.stroke();

  } else if (pathology === 'massive_pleural_effusion') {
    // Dense opaque white homogeneous meniscus in left hemithorax (screen left)
    const grad = ctx.createLinearGradient(0, h * 0.45, 0, h * 0.88);
    grad.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
    grad.addColorStop(0.3, 'rgba(255, 255, 255, 0.6)');
    grad.addColorStop(1, 'rgba(255, 255, 255, 0.9)');

    ctx.fillStyle = grad;
    ctx.beginPath();
    // Meniscus curve
    ctx.moveTo(w * 0.12, h * 0.48); // Axillary peak
    ctx.quadraticCurveTo(w * 0.30, h * 0.65, w * 0.48, h * 0.70);
    ctx.lineTo(w * 0.48, h * 0.92);
    ctx.lineTo(w * 0.12, h * 0.92);
    ctx.closePath();
    ctx.fill();

  } else if (pathology === 'cardiomegaly_pulmonary_edema') {
    // Batwing alveolar edema (perihilar fluffy haziness)
    const radialL = ctx.createRadialGradient(w * 0.38, h * 0.52, 10, w * 0.38, h * 0.52, w * 0.14);
    radialL.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
    radialL.addColorStop(1, 'rgba(255, 255, 255, 0.0)');
    ctx.fillStyle = radialL;
    ctx.fillRect(w * 0.20, h * 0.38, w * 0.30, h * 0.30);

    const radialR = ctx.createRadialGradient(w * 0.62, h * 0.52, 10, w * 0.62, h * 0.52, w * 0.14);
    radialR.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
    radialR.addColorStop(1, 'rgba(255, 255, 255, 0.0)');
    ctx.fillStyle = radialR;
    ctx.fillRect(w * 0.50, h * 0.38, w * 0.30, h * 0.30);

    // Kerley B lines (short horizontal lines at pleural bases)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.lineWidth = 1.5;
    for (let y = h * 0.70; y < h * 0.82; y += 8) {
      ctx.beginPath();
      ctx.moveTo(w * 0.14, y);
      ctx.lineTo(w * 0.18, y);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(w * 0.82, y);
      ctx.lineTo(w * 0.86, y);
      ctx.stroke();
    }

  } else if (pathology === 'lobar_consolidation_pneumonia') {
    // Dense consolidation in right lower/middle lobe (screen right)
    const pGrad = ctx.createRadialGradient(w * 0.74, h * 0.64, 15, w * 0.74, h * 0.64, w * 0.15);
    pGrad.addColorStop(0, 'rgba(255, 255, 255, 0.75)');
    pGrad.addColorStop(0.7, 'rgba(255, 255, 255, 0.45)');
    pGrad.addColorStop(1, 'rgba(255, 255, 255, 0.0)');
    ctx.fillStyle = pGrad;
    ctx.beginPath();
    ctx.ellipse(w * 0.74, h * 0.64, w * 0.14, h * 0.12, 0.1, 0, Math.PI * 2);
    ctx.fill();

    // Air bronchograms (dark branched air-filled tubes inside white consolidation)
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(w * 0.68, h * 0.58);
    ctx.lineTo(w * 0.73, h * 0.65);
    ctx.lineTo(w * 0.78, h * 0.70);
    ctx.stroke();

  } else if (pathology === 'solitary_pulmonary_nodule') {
    // Discrete circular soft-tissue nodule in left upper lobe (screen left)
    const nx = w * 0.32;
    const ny = h * 0.36;
    const nRad = 12;

    const nGrad = ctx.createRadialGradient(nx, ny, 2, nx, ny, nRad);
    nGrad.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    nGrad.addColorStop(0.8, 'rgba(255, 255, 255, 0.6)');
    nGrad.addColorStop(1, 'rgba(255, 255, 255, 0.0)');

    ctx.fillStyle = nGrad;
    ctx.beginPath();
    ctx.arc(nx, ny, nRad, 0, Math.PI * 2);
    ctx.fill();

  } else if (pathology === 'atelectasis') {
    // Linear plate-like basilar bands
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo(w * 0.22, h * 0.76);
    ctx.lineTo(w * 0.38, h * 0.74);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(w * 0.62, h * 0.75);
    ctx.lineTo(w * 0.78, h * 0.73);
    ctx.stroke();
  }

  ctx.restore();
}

function drawGradCamHeatmap(ctx, w, h, roi, opacity) {
  ctx.save();
  ctx.globalAlpha = opacity;

  // Center of activation from ROI
  const cx = (roi.x + roi.w * 0.5) * w;
  const cy = (roi.y + roi.h * 0.5) * h;
  const radius = Math.max(roi.w, roi.h) * w * 0.9;

  // Grad-CAM Colormap (Jet: Blue -> Cyan -> Yellow -> Red)
  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
  grad.addColorStop(0.0, 'rgba(239, 68, 68, 0.95)');   // Core Red
  grad.addColorStop(0.3, 'rgba(245, 158, 11, 0.85)');  // Orange/Amber
  grad.addColorStop(0.6, 'rgba(234, 179, 8, 0.65)');   // Yellow
  grad.addColorStop(0.8, 'rgba(6, 182, 212, 0.40)');   // Cyan
  grad.addColorStop(1.0, 'rgba(59, 130, 246, 0.0)');   // Transparent Blue edge

  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

function drawRoiBoundingBox(ctx, w, h, roi, label) {
  ctx.save();
  const bx = roi.x * w;
  const by = roi.y * h;
  const bw = roi.w * w;
  const bh = roi.h * h;

  // Pulsing dashed box
  ctx.strokeStyle = '#EF4444';
  ctx.lineWidth = 2;
  ctx.setLineDash([6, 4]);
  ctx.strokeRect(bx, by, bw, bh);

  // Label banner
  ctx.setLineDash([]);
  ctx.fillStyle = 'rgba(239, 68, 68, 0.85)';
  ctx.fillRect(bx, by - 20, bw, 20);

  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(`AI DETECT: ${label.toUpperCase()}`, bx + 6, by - 6);

  ctx.restore();
}

function drawCtrCaliper(ctx, w, h, ctrRatio) {
  ctx.save();
  // Caliper lines
  const thoracicY = h * 0.74;
  const cardiacY = h * 0.62;

  // Thoracic width line
  ctx.strokeStyle = '#06B6D4';
  ctx.lineWidth = 2;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(w * 0.16, thoracicY);
  ctx.lineTo(w * 0.84, thoracicY);
  ctx.stroke();

  // Cardiac width line
  const hw = (w * (ctrRatio * 0.48)) * 0.95;
  ctx.strokeStyle = '#F59E0B';
  ctx.beginPath();
  ctx.moveTo(w * 0.48 - hw, cardiacY);
  ctx.lineTo(w * 0.48 + hw, cardiacY);
  ctx.stroke();

  ctx.setLineDash([]);
  ctx.fillStyle = '#FFFFFF';
  ctx.font = '11px sans-serif';
  ctx.fillText(`Thoracic Diameter (C)`, w * 0.18, thoracicY - 6);
  ctx.fillText(`Cardiac Diameter (A+B): CTR = ${ctrRatio} ${ctrRatio > 0.50 ? '(Cardiomegaly)' : '(Normal)'}`, w * 0.28, cardiacY - 6);

  ctx.restore();
}

// ---------------------------------------------------------------------------
// CLINICIAN REVIEW & SIGN-OFF (HUMAN-IN-THE-LOOP)
// ---------------------------------------------------------------------------

async function commitPhysicianReview() {
  const c = getActiveCase();
  if (!c) return;

  const decision = elements.reviewDecision.value;
  const clinicianName = elements.clinicianSig.value.trim() || 'Dr. Alex Vance, MD';
  const notes = elements.clinicianNotes.value.trim();
  const modifiedFinding = elements.overrideFindingInput.value.trim();

  try {
    const res = await fetch('/api/clinician-review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        case_id: c.id,
        decision: decision,
        clinician_name: clinicianName,
        rationale: notes,
        modified_finding: modifiedFinding || undefined
      })
    });
    const result = await res.json();
    if (result.status === 'success') {
      showToast(`Case ${c.mrn} successfully signed & committed.`);
      await fetchCases();
      await fetchAuditLog();
    }
  } catch (err) {
    console.error('Sign-off error:', err);
    showToast('Failed to record physician sign-off.');
  }
}

async function fetchAuditLog() {
  try {
    const res = await fetch('/api/audit-log');
    const data = await res.json();
    if (data.status === 'success') {
      state.auditLog = data.log;
      elements.auditCount.textContent = data.count;
      renderAuditDrawer();
    }
  } catch (err) {
    console.error('Audit fetch failed:', err);
  }
}

function renderAuditDrawer() {
  const container = elements.auditLogItems;
  container.innerHTML = '';

  if (state.auditLog.length === 0) {
    container.innerHTML = '<p style="color: var(--text-dim); text-align: center; padding: 20px;">No reviews committed yet in this session.</p>';
    return;
  }

  // Reverse chronological
  [...state.auditLog].reverse().forEach(log => {
    const dateStr = new Date(log.timestamp).toLocaleTimeString();
    const card = document.createElement('div');
    card.className = 'audit-card';
    card.innerHTML = `
      <div class="audit-top">
        <span>${dateStr}</span>
        <span class="audit-action ${log.decision}">${log.decision}</span>
      </div>
      <div class="audit-case">MRN: ${log.mrn} • ${log.final_signed_finding}</div>
      <div style="color: #94A3B8; font-size: 10px; margin-bottom: 4px;">Signer: ${log.clinician}</div>
      <div class="audit-notes">"${log.rationale}"</div>
    `;
    container.appendChild(card);
  });
}

// ---------------------------------------------------------------------------
// MODALS & EXPORTS (FHIR R4, HL7, COHORT BATCH)
// ---------------------------------------------------------------------------

async function openFhirModal() {
  const c = getActiveCase();
  if (!c) return;
  try {
    const res = await fetch(`/api/export-fhir/${c.id}`);
    const bundle = await res.json();
    elements.modalFhirTitle.textContent = `HL7 FHIR R4 DiagnosticReport Bundle (${c.mrn})`;
    elements.fhirJsonCode.textContent = JSON.stringify(bundle, null, 2);
    elements.modalFhir.classList.add('open');
  } catch (err) {
    console.error('FHIR export failed:', err);
  }
}

async function openHl7Modal() {
  const c = getActiveCase();
  if (!c) return;
  try {
    const res = await fetch(`/api/export-hl7/${c.id}`);
    const hl7Text = await res.text();
    elements.modalFhirTitle.textContent = `HL7 v2.5.1 ORU^R01 Message (${c.mrn})`;
    elements.fhirJsonCode.textContent = hl7Text;
    elements.modalFhir.classList.add('open');
  } catch (err) {
    console.error('HL7 export failed:', err);
  }
}

function exportClinicalReport() {
  const c = getActiveCase();
  if (!c) return;
  const content = `========================================================================
TRIAGEVISION CDS™ CLINICAL DECISION SUPPORT REPORT
========================================================================
PATIENT MRN: ${c.mrn}
NAME: ${c.patient_name}
AGE / SEX: ${c.age}yo ${c.sex}
ENCOUNTER: ${c.encounter_type}
ADMIT TIME: ${c.admit_time}

TRIAGE STRATIFICATION:
- PRIORITY TIER: ${c.triage_priority.priority_tier}
- URGENCY SCORE: ${c.triage_priority.composite_urgency} / 100
- TARGET TURNAROUND TIME: < ${c.triage_priority.target_tat_minutes} min
- PHYSIOLOGICAL NEWS2 SCORE: ${c.calculated_news2.total_score} (${c.calculated_news2.risk_level})
- qSOFA CRITERIA: ${c.calculated_qsofa.score}/3 (${c.calculated_qsofa.positive ? 'High Risk' : 'Low Risk'})
- SHOCK INDEX (HR/SBP): ${c.calculated_shock.shock_index} (${c.calculated_shock.status})

RADIOLOGICAL AI PRELIMINARY FINDING:
- PRIMARY FINDING: ${c.imaging_evaluation.primary_finding}
- AI CONFIDENCE: ${c.imaging_evaluation.confidence_percent}%
- CARDIOTHORACIC RATIO (CTR): ${c.imaging_evaluation.cardiothoracic_ratio}
- CLINICAL GUIDELINES: ${c.imaging_evaluation.clinical_guidelines}

PHYSICIAN SIGN-OFF ADDENDUM:
- STATUS: ${c.physician_status}
- SIGNING CLINICIAN: ${c.review_audit ? c.review_audit.clinician : 'Pending Final Attestation'}
- IMPRESSION: ${elements.clinicianNotes.value}

REGULATORY SA-MD NOTICE:
Investigational Clinical Decision Support Tool (Class IIa).
========================================================================`;

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `CDS_Report_${c.mrn}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast(`Clinical summary report downloaded for ${c.mrn}`);
}

async function openBatchModal() {
  try {
    const res = await fetch('/api/cohort');
    const data = await res.json();
    if (data.status === 'success') {
      state.cohortData = data.cohort;
      renderCohortTable(data.cohort);
      elements.modalBatch.classList.add('open');
    }
  } catch (err) {
    console.error('Failed to fetch cohort:', err);
  }
}

function renderCohortTable(cohort) {
  const tbody = elements.cohortTbody;
  tbody.innerHTML = '';

  let statCnt = 0, urgCnt = 0, expCnt = 0, routCnt = 0;

  cohort.forEach(pt => {
    const news = pt.calculated_news2.total_score;
    let rec = 'ROUTINE';
    let badgeClass = 'badge-routine';

    if (news >= 7 || (pt.calculated_qsofa.positive && news >= 5)) {
      rec = 'STAT';
      badgeClass = 'badge-stat';
      statCnt++;
    } else if (news >= 5) {
      rec = 'URGENT';
      badgeClass = 'badge-urgent';
      urgCnt++;
    } else if (news >= 2) {
      rec = 'EXPEDITED';
      badgeClass = 'badge-expedited';
      expCnt++;
    } else {
      routCnt++;
    }

    // Drivers
    const drivers = [];
    if (pt.calculated_news2.subscores.respiratory_rate > 0) drivers.push(`RR=${pt.respiratory_rate}`);
    if (pt.calculated_news2.subscores.systolic_bp > 0) drivers.push(`SBP=${pt.systolic_bp}`);
    if (pt.lactate >= 2.0) drivers.push(`Lactate=${pt.lactate}`);
    if (pt.altered_mentation) drivers.push(`Altered Mentation`);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${pt.patient_id}</strong></td>
      <td>${pt.age}yo ${pt.sex}</td>
      <td>HR ${pt.heart_rate} • BP ${pt.systolic_bp} • RR ${pt.respiratory_rate} • SpO2 ${pt.spo2}%</td>
      <td><span class="news2-pill-mini ${news >= 7 ? 'high' : ''}">${news}</span></td>
      <td>${pt.calculated_qsofa.score}/3</td>
      <td>${pt.calculated_shock.shock_index}</td>
      <td><span class="badge-priority ${badgeClass}">${rec}</span></td>
      <td style="color: #FCA5A5;">${drivers.join(', ') || 'Normal baseline'}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('cohort-stat-count').textContent = statCnt;
  document.getElementById('cohort-urgent-count').textContent = urgCnt;
  document.getElementById('cohort-exp-count').textContent = expCnt;
  document.getElementById('cohort-rout-count').textContent = routCnt;
}

function exportCohortCsv() {
  if (!state.cohortData.length) return;
  const headers = ['PatientID', 'Age', 'Sex', 'HR', 'SBP', 'RR', 'SpO2', 'O2', 'Lactate', 'NEWS2', 'qSOFA', 'ShockIndex', 'TriageRec'];
  const rows = state.cohortData.map(p => [
    p.patient_id,
    p.age,
    p.sex,
    p.heart_rate,
    p.systolic_bp,
    p.respiratory_rate,
    p.spo2,
    p.supplemental_o2 ? '1' : '0',
    p.lactate,
    p.calculated_news2.total_score,
    p.calculated_qsofa.score,
    p.calculated_shock.shock_index,
    p.calculated_news2.total_score >= 7 ? 'STAT' : (p.calculated_news2.total_score >= 5 ? 'URGENT' : 'ROUTINE')
  ]);

  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'stratified_cohort_triage.csv';
  a.click();
  URL.revokeObjectURL(url);
  showToast('Stratified clinical cohort CSV exported.');
}

async function submitImageUpload() {
  const pathology = elements.uploadPresetSelect.value;
  const mrn = elements.uploadMrn.value.trim() || 'ANON-99412';
  const age = parseInt(elements.uploadAge.value, 10) || 55;
  const sex = elements.uploadSex.value;
  const history = elements.uploadHistory.value.trim() || 'Direct image intake screening';

  try {
    const res = await fetch('/api/analyze-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pathology_type: pathology,
        mrn: mrn,
        patient_name: `Patient (${mrn})`,
        age: age,
        sex: sex,
        clinical_history: history,
        confidence: 0.94,
        ctr_ratio: pathology === 'cardiomegaly_pulmonary_edema' ? 0.61 : 0.47
      })
    });
    const result = await res.json();
    if (result.status === 'success') {
      elements.modalUpload.classList.remove('open');
      state.activeCaseId = result.case.id;
      showToast(`Analyzed & prioritized new study ${mrn} (${result.case.triage_priority.priority_tier}).`);
      await fetchCases();
    }
  } catch (err) {
    console.error('Upload failed:', err);
    showToast('Failed to analyze uploaded study.');
  }
}
