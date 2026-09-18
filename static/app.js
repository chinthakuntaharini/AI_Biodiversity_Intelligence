/**
 * Darukaa.Earth Environmental Intelligence Platform
 * Scientific Dashboard Controller — v2.0
 * 
 * Not a chatbot. A scientific assessment interface.
 */

'use strict';

// ──────────────────────────────────────────────────────────────────────────────
// State
// ──────────────────────────────────────────────────────────────────────────────
let currentSessionId       = generateSessionId();
let lastAnalysis           = null;
let activeDomainFilter     = '';
let currentPanel           = 'intake';
let sessionAccumulatedState = {};

// ──────────────────────────────────────────────────────────────────────────────
// Initialization
// ──────────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    updateSessionDisplay();
    loadCorpusStats();
    resolveSpatial();         // pre-load default spatial result
    searchKB();               // pre-load default knowledge results
});

function generateSessionId() {
    return 'DS-' + Math.random().toString(36).substring(2, 6).toUpperCase() + '-' + Date.now().toString(36).toUpperCase().slice(-4);
}

function updateSessionDisplay() {
    const el = document.getElementById('session-display');
    if (el) el.textContent = `Session: ${currentSessionId}`;
}

// ──────────────────────────────────────────────────────────────────────────────
// Panel Navigation
// ──────────────────────────────────────────────────────────────────────────────
const PANEL_META = {
    intake:    { title: 'Ecological Parameter Intake',         subtitle: 'Multi-turn natural language environmental assessment — describe your ecosystem in any format' },
    matrix:    { title: 'Multi-Variable Diagnostic Matrix',    subtitle: 'Coupled analysis across ≥3 simultaneous environmental dimensions: Soil · Hydrology · Biodiversity · Land Use · Climate' },
    spatial:   { title: 'Geo-Spatial Biome & Climate Resolver', subtitle: 'Geographic coordinates → ecoregion, Köppen-Geiger classification, and baseline environmental metrics' },
    knowledge: { title: 'Peer-Reviewed Knowledge Vault',       subtitle: 'BM25 retrieval over indexed FAO, IPCC AR6, IPBES, and USDA-NRCS literature across 5 ecological domains' },
};

function switchPanel(panelId) {
    // Update panels
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(`panel-${panelId}`);
    if (target) target.classList.add('active');

    // Update nav
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    const navBtn = document.getElementById(`nav-${panelId}-btn`);
    if (navBtn) navBtn.classList.add('active');

    // Update topbar
    const meta = PANEL_META[panelId] || {};
    const titleEl    = document.getElementById('view-title');
    const subtitleEl = document.getElementById('view-subtitle');
    if (titleEl)    titleEl.textContent    = meta.title    || '';
    if (subtitleEl) subtitleEl.textContent = meta.subtitle || '';

    currentPanel = panelId;
}

// ──────────────────────────────────────────────────────────────────────────────
// Corpus Stats
// ──────────────────────────────────────────────────────────────────────────────
async function loadCorpusStats() {
    try {
        const res  = await fetch('/health');
        const data = await res.json();
        const kb   = data.knowledge_base || {};
        const sp   = data.spatial_resolver || {};

        animateCount('stat-docs',    kb.indexed_documents || 0);
        animateCount('stat-domains', (kb.indexed_domains || []).length);
        animateCount('stat-cites',   kb.total_citations || 0);
        animateCount('stat-biomes',  sp.biome_profiles || 0);
    } catch (err) {
        console.warn('Could not load corpus stats:', err.message);
    }
}

function animateCount(id, targetVal) {
    const el = document.getElementById(id);
    if (!el) return;
    let current = 0;
    const step  = Math.max(1, Math.ceil(targetVal / 25));
    const timer = setInterval(() => {
        current = Math.min(current + step, targetVal);
        el.textContent = current;
        if (current >= targetVal) clearInterval(timer);
    }, 30);
}

// ──────────────────────────────────────────────────────────────────────────────
// PANEL 1: INTAKE — Scientific Parameter Intake
// ──────────────────────────────────────────────────────────────────────────────
function handleIntakeKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submitIntake();
    }
}

async function submitIntake(overrideText = null) {
    const input   = document.getElementById('intake-input');
    const message = (overrideText || input.value).trim();
    if (!message) return;

    if (!overrideText) input.value = '';

    const stream = document.getElementById('intake-stream');

    // Append user query card
    appendStreamCard('user', `<div class="query-text">${escapeHtml(message)}</div>`, stream);

    // Loading indicator
    const loadingId = 'loading-' + Date.now();
    appendStreamCard('loading', `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <span>Querying scientific knowledge base and evaluating multi-metric transfer functions…</span>
        </div>
    `, stream, loadingId);

    // Disable submit
    const submitBtn = document.getElementById('intake-submit-btn');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Analysing…'; }

    try {
        const res = await fetch('/api/scientist/intake', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ message, session_id: currentSessionId }),
        });
        const data = await res.json();

        // Remove loading card
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.remove();

        // Update session
        currentSessionId = data.session_id || currentSessionId;
        updateSessionDisplay();

        // Update accumulated state display
        if (data.accumulated_state) {
            sessionAccumulatedState = data.accumulated_state;
            updateSessionStatePanel(data.accumulated_state, data.missing_dimensions || []);
        }

        // Render response
        if (data.status === 'analysis_complete' && data.analysis) {
            lastAnalysis = data.analysis;
            appendAnalysisCard(data.analysis, stream);
        } else {
            appendClarificationCard(data, stream);
        }
    } catch (err) {
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.remove();
        appendStreamCard('system', `
            <div class="clarification-heading" style="color: var(--rose);">Engine Error</div>
            <p class="clarification-questions">${escapeHtml(err.message)}</p>
        `, stream);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                <span>Analyse</span>
            `;
        }
    }
}

function appendStreamCard(role, innerHtml, container, cardId = null) {
    const div = document.createElement('div');
    div.className = `assessment-card ${role === 'user' ? 'user-query' : role === 'loading' ? '' : 'scientist-response'}`;
    if (cardId) div.id = cardId;

    const roleLabel = { user: 'Field Investigator', scientist: 'Environmental Scientist', system: 'System Note', loading: '' }[role] || role;
    const roleDot   = role !== 'loading' ? `
        <div class="card-role ${role}">
            <span class="card-role-dot"></span>
            ${roleLabel}
        </div>` : '';

    div.innerHTML = roleDot + innerHtml;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function appendClarificationCard(data, container) {
    const missingDims   = data.missing_dimensions || [];
    const questions     = data.intake_questions   || [];

    const missingTags = missingDims.map(d =>
        `<span class="missing-dim-tag">${capitalize(d)}</span>`
    ).join('');

    const quickFills = [
        ['Semi-Arid Wheat Benchmark',   "SOC: 0.3%, rainfall: low, crop: monoculture wheat, region: semi-arid"],
        ['Rangeland Degradation',        "degraded rangeland, bare soil >40%, high compaction, rainfall 350mm"],
        ['Thar Coordinates',             "26.28, 73.02 — rainfed pearl millet, depleted topsoil"],
    ];

    const div = document.createElement('div');
    div.className = 'assessment-card clarification-card';
    div.innerHTML = `
        <div class="card-role system">
            <span class="card-role-dot"></span>
            Intake Clarification Required
        </div>
        <div class="clarification-heading">Additional Environmental Parameters Needed</div>
        <div class="clarification-missing">${missingTags}</div>
        <ul class="clarification-questions">
            ${questions.map(q => `<li>${escapeHtml(q)}</li>`).join('')}
        </ul>
        <div class="clarification-quick-fills">
            <span style="font-size:0.7rem;color:var(--text-muted);align-self:center;">Quick fills:</span>
            ${quickFills.map(([label, val]) =>
                `<button class="quick-fill-btn" onclick="submitIntake(${JSON.stringify(val)})">${escapeHtml(label)}</button>`
            ).join('')}
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function appendAnalysisCard(analysis, container) {
    const vars  = analysis.variables_evaluated || [];
    const risk  = analysis.risk_profile         || {};
    const nexus = analysis.multi_metric_nexus   || {};
    const recs  = analysis.recommendations      || [];

    const div = document.createElement('div');
    div.className = 'assessment-card scientist-response analysis-result-card';
    div.innerHTML = `
        <div class="card-role scientist">
            <span class="card-role-dot"></span>
            Ecological Assessment Report
        </div>

        <!-- Variables -->
        <div class="vars-bar">
            ${vars.map(v => `<span class="var-pill">${escapeHtml(v)}</span>`).join('')}
            <span class="vars-count-badge">${vars.length} Dimensions Evaluated</span>
        </div>

        <!-- Risk Profile -->
        <div class="risk-section">
            <div class="section-label">Risk & Degradation Profile</div>
            <div class="risk-grid">
                ${Object.entries(risk).map(([dim, level]) => `
                    <div class="risk-item ${level}">
                        <span class="risk-dim">${capitalize(dim.replace(/_/g, ' '))}</span>
                        <span class="risk-level">${level}</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Nexus -->
        <div class="nexus-section">
            <div class="nexus-title-row">
                <span class="nexus-title-text">Multi-Metric Ecological Nexus</span>
                <span class="trajectory-badge ${trajectoryClass(nexus.system_trajectory || '')}">${escapeHtml(nexus.system_trajectory || '')}</span>
            </div>
            <div class="nexus-stressor"><strong>Primary Stressor:</strong> ${escapeHtml(nexus.primary_stressor || '')}</div>
            <ul class="nexus-chains-list">
                ${(nexus.interaction_chains || []).map(c => `<li>${escapeHtml(c)}</li>`).join('')}
            </ul>
        </div>

        <!-- Prescriptions -->
        <div class="section-label" style="margin-bottom:10px;">Evidence-Backed Intervention Prescriptions</div>
        <div class="prescriptions-list">
            ${recs.map((rec, i) => buildPrescriptionCard(rec, i + 1)).join('')}
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function buildPrescriptionCard(rec, num) {
    const impacts = (rec.multi_metric_impacts || []).map(imp => `
        <div class="impact-tile">
            <span class="impact-tile-dim">${escapeHtml(imp.dimension)}</span>
            <span class="impact-tile-metric">${escapeHtml(imp.metric)}</span>
            <span class="impact-tile-value">${escapeHtml(imp.projected_change)}</span>
        </div>
    `).join('');

    const citeId = `cites-rx-${num}-${Date.now()}`;
    const cites  = (rec.citations || []).map(c => `<li>${escapeHtml(c)}</li>`).join('');

    return `
        <div class="prescription-card">
            <div class="rx-header">
                <div class="rx-title">${escapeHtml(rec.title)}</div>
                <span class="rx-num">${num}</span>
            </div>
            <div class="rx-priority">${escapeHtml(rec.priority || '')}</div>
            <div class="rx-action-box">${escapeHtml(rec.action)}</div>
            <div class="rx-mechanism"><em>Mechanism: ${escapeHtml(rec.scientific_mechanism)}</em></div>
            <div class="impact-tiles">${impacts}</div>
            <div class="rx-footer">
                <span class="rx-horizon-tag">${escapeHtml(rec.time_horizon)}</span>
                <span class="rx-confidence-tag">${escapeHtml(rec.confidence_level)}</span>
                <button class="rx-cites-toggle" onclick="toggleCites('${citeId}', this)">
                    Show ${(rec.citations || []).length} citations
                </button>
            </div>
            <ul class="rx-cites-list" id="${citeId}" style="display:none;">${cites}</ul>
        </div>
    `;
}

function toggleCites(id, btn) {
    const el = document.getElementById(id);
    if (!el) return;
    const hidden = el.style.display === 'none';
    el.style.display = hidden ? 'block' : 'none';
    btn.textContent = hidden ? 'Hide citations' : `Show ${el.children.length} citations`;
}

function trajectoryClass(t) {
    const lower = (t || '').toLowerCase();
    if (lower.includes('accelerating')) return 'accelerating';
    if (lower.includes('degrading'))    return 'degrading';
    if (lower.includes('at risk'))      return 'at-risk';
    return 'stable';
}

// ──────────────────────────────────────────────────────────────────────────────
// Session State Panel Updater
// ──────────────────────────────────────────────────────────────────────────────
function updateSessionStatePanel(state, missingDims) {
    const content = document.getElementById('ssp-content');
    if (!content) return;

    const displayKeys = {
        soil_organic_carbon: 'SOC',
        rainfall_mm:         'Rainfall mm',
        rainfall:            'Moisture regime',
        crop:                'Crop/Land use',
        region:              'Region',
        ph:                  'Soil pH',
        bulk_density:        'Bulk density',
        erosion_rate:        'Erosion rate',
        species_richness:    'Species richness',
        coordinates:         'Coordinates',
    };

    let html = '';
    for (const [key, label] of Object.entries(displayKeys)) {
        const val = state[key];
        if (val !== undefined && val !== null && val !== '') {
            const displayVal = (typeof val === 'object')
                ? `${val.lat?.toFixed(2)}°, ${val.lon?.toFixed(2)}°`
                : String(val);
            html += `
                <div class="ssp-param-row">
                    <span class="ssp-param-key">${label}</span>
                    <span class="ssp-param-value">${escapeHtml(displayVal)}</span>
                </div>
            `;
        }
    }

    content.innerHTML = html || '<p class="ssp-empty">No parameters extracted yet.</p>';

    // Update coverage dims
    const hasKey = (keys) => keys.some(k => state[k] !== undefined && state[k] !== null);

    updateDimRow('dim-soil',    hasKey(['soil_organic_carbon', 'soc', 'ph', 'bulk_density', 'soil_type']));
    updateDimRow('dim-hydro',   hasKey(['rainfall', 'rainfall_mm', 'rainfall_pattern']));
    updateDimRow('dim-veg',     hasKey(['crop', 'land_use', 'ndvi', 'species_richness']));
    updateDimRow('dim-spatial', hasKey(['coordinates', 'region']));
}

function updateDimRow(rowId, isPresent) {
    const row  = document.getElementById(rowId);
    if (!row) return;
    const dot    = row.querySelector('.dim-dot');
    const status = row.querySelector('.dim-status');
    if (!dot || !status) return;

    dot.className    = 'dim-dot ' + (isPresent ? 'present' : 'missing');
    status.textContent = isPresent ? '✓ Present' : '✗ Missing';
    status.style.color = isPresent ? 'var(--green)' : 'var(--amber)';
}

// ──────────────────────────────────────────────────────────────────────────────
// PANEL 2: DIAGNOSTIC MATRIX
// ──────────────────────────────────────────────────────────────────────────────
async function runMatrixAnalysis() {
    const payload = buildMatrixPayload();
    const container = document.getElementById('matrix-results');

    container.innerHTML = `
        <div class="loading-spinner" style="padding:40px;justify-content:center;">
            <div class="spinner"></div>
            <span>Executing multi-metric ecological diagnosis…</span>
        </div>
    `;

    try {
        const res  = await fetch('/api/scientist/analyze', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload),
        });
        const data = await res.json();
        lastAnalysis = data;
        renderMatrixResults(container, data);
    } catch (err) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <h3>Analysis Error</h3>
                <p>${escapeHtml(err.message)}</p>
            </div>
        `;
    }
}

function buildMatrixPayload() {
    const soc      = parseFloat(document.getElementById('m-soc')?.value)    || null;
    const ph       = parseFloat(document.getElementById('m-ph')?.value)     || null;
    const bulk     = parseFloat(document.getElementById('m-bulk')?.value)   || null;
    const erosion  = parseFloat(document.getElementById('m-erosion')?.value)|| null;
    const rainMm   = parseFloat(document.getElementById('m-rain-mm')?.value)|| null;
    const rainCat  = document.getElementById('m-rain-cat')?.value;
    const region   = document.getElementById('m-region')?.value;
    const crop     = document.getElementById('m-crop')?.value;
    const species  = parseFloat(document.getElementById('m-species')?.value) || null;
    const coordsRaw= document.getElementById('m-coords')?.value?.trim();

    let coordinates = null;
    if (coordsRaw && coordsRaw.includes(',')) {
        const parts = coordsRaw.split(',');
        const lat   = parseFloat(parts[0]);
        const lon   = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lon)) coordinates = { lat, lon };
    }

    return {
        soil_organic_carbon: soc,
        ph,
        bulk_density:  bulk,
        erosion_rate:  erosion,
        rainfall_mm:   rainMm,
        rainfall:      rainCat || null,
        region:        region  || null,
        crop:          crop    || null,
        species_richness: species,
        coordinates,
    };
}

function renderMatrixResults(container, analysis) {
    const vars  = analysis.variables_evaluated || [];
    const risk  = analysis.risk_profile         || {};
    const nexus = analysis.multi_metric_nexus   || {};
    const recs  = analysis.recommendations      || [];

    container.innerHTML = `
        <!-- Risk Profile -->
        <div style="margin-bottom:20px;">
            <div class="section-label" style="margin-bottom:10px;">Coupled Diagnosis — ${vars.length} Dimensions Evaluated</div>
            <div class="risk-grid" style="margin-bottom:14px;">
                ${Object.entries(risk).map(([dim, level]) => `
                    <div class="risk-item ${level}">
                        <span class="risk-dim">${capitalize(dim.replace(/_/g, ' '))}</span>
                        <span class="risk-level">${level}</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <!-- Nexus -->
        <div class="nexus-section" style="margin-bottom:20px;">
            <div class="nexus-title-row">
                <span class="nexus-title-text">Multi-Metric Ecological Nexus</span>
                <span class="trajectory-badge ${trajectoryClass(nexus.system_trajectory || '')}">${escapeHtml(nexus.system_trajectory || '')}</span>
            </div>
            <div class="nexus-stressor"><strong>Primary Stressor:</strong> ${escapeHtml(nexus.primary_stressor || '')}</div>
            <ul class="nexus-chains-list">
                ${(nexus.interaction_chains || []).map(c => `<li>${escapeHtml(c)}</li>`).join('')}
            </ul>
        </div>

        <!-- Prescriptions -->
        <div class="section-label" style="margin-bottom:10px;">Evidence-Backed Intervention Prescriptions</div>
        <div class="prescriptions-list">
            ${recs.map((rec, i) => buildPrescriptionCard(rec, i + 1)).join('')}
        </div>
    `;
}

function loadBenchmarkToMatrix() {
    document.getElementById('m-soc').value       = '0.30';
    document.getElementById('m-ph').value        = '7.4';
    document.getElementById('m-rain-mm').value   = '350';
    document.getElementById('m-rain-cat').value  = 'low';
    document.getElementById('m-region').value    = 'semi-arid';
    document.getElementById('m-crop').value      = 'monoculture wheat';
    document.getElementById('m-coords').value    = '26.28, 73.02';
    document.getElementById('m-species').value   = '3';
}

// ──────────────────────────────────────────────────────────────────────────────
// PANEL 3: SPATIAL RESOLVER
// ──────────────────────────────────────────────────────────────────────────────
async function resolveSpatial() {
    const lat = parseFloat(document.getElementById('sp-lat')?.value);
    const lon = parseFloat(document.getElementById('sp-lon')?.value);

    if (isNaN(lat) || isNaN(lon)) return;

    const panel = document.getElementById('spatial-result');
    if (panel) panel.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <span>Resolving [${lat.toFixed(2)}, ${lon.toFixed(2)}] against global biome profiles…</span>
        </div>
    `;

    try {
        const res  = await fetch('/api/spatial/lookup', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ latitude: lat, longitude: lon }),
        });
        const data = await res.json();
        renderSpatialResult(data, lat, lon);
    } catch (err) {
        if (panel) panel.innerHTML = `<p style="color:var(--rose);padding:14px;">Spatial resolution failed: ${escapeHtml(err.message)}</p>`;
    }
}

function renderSpatialResult(data, lat, lon) {
    const panel = document.getElementById('spatial-result');
    if (!panel) return;

    const base   = data.baseline_metrics || {};
    const koppen = (data.koppen_classes || []).join(', ');
    const threats = (base.primary_threats || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');
    const taxa    = (base.recommended_native_taxa || []).map(t => `<li><em>${escapeHtml(t)}</em></li>`).join('');
    const soilTypes = (base.dominant_soil_types || []).join(', ');
    const rainRange = (base.annual_rainfall_range_mm || []).join('–');
    const socRange  = (base.typical_soc_range_pct  || []).join('–');

    panel.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr auto;align-items:flex-start;gap:16px;margin-bottom:16px;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span class="domain-filter active" style="cursor:default;">${escapeHtml(data.matched_by || 'geo-match')}</span>
                </div>
                <h3 style="font-family:var(--font-head);font-size:1.15rem;font-weight:700;margin-bottom:4px;">${escapeHtml(data.biome_name || 'N/A')}</h3>
                <p style="font-size:0.8rem;color:var(--blue);">${escapeHtml(data.zone_name || '')} · ${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E</p>
            </div>
            <div style="text-align:right;">
                <span style="font-size:0.68rem;color:var(--text-muted);display:block;margin-bottom:3px;">Köppen Classes</span>
                <strong style="font-family:var(--font-mono);font-size:1rem;color:var(--green);">${koppen}</strong>
            </div>
        </div>

        <div class="impact-tiles" style="margin-bottom:16px;">
            <div class="impact-tile">
                <span class="impact-tile-dim">Hydrological Baseline</span>
                <span class="impact-tile-metric">Annual Precipitation</span>
                <span class="impact-tile-value">${rainRange} mm / yr</span>
            </div>
            <div class="impact-tile">
                <span class="impact-tile-dim">Edaphic Baseline</span>
                <span class="impact-tile-metric">Soil Organic Carbon</span>
                <span class="impact-tile-value">${socRange} % SOC</span>
            </div>
            <div class="impact-tile">
                <span class="impact-tile-dim">Soil Taxonomy</span>
                <span class="impact-tile-metric">Dominant Orders</span>
                <span class="impact-tile-value">${escapeHtml(soilTypes)}</span>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
            <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border-subtle);border-radius:var(--radius-sm);padding:12px;">
                <strong style="font-size:0.72rem;color:var(--amber);text-transform:uppercase;letter-spacing:0.07em;display:block;margin-bottom:6px;">Primary Ecological Threats</strong>
                <ul style="padding-left:18px;font-size:0.78rem;color:var(--text-secondary);line-height:1.6;">${threats}</ul>
            </div>
            <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border-subtle);border-radius:var(--radius-sm);padding:12px;">
                <strong style="font-size:0.72rem;color:var(--green);text-transform:uppercase;letter-spacing:0.07em;display:block;margin-bottom:6px;">Recommended Native Taxa</strong>
                <ul style="padding-left:18px;font-size:0.78rem;color:var(--text-secondary);line-height:1.6;">${taxa}</ul>
            </div>
        </div>
    `;
}

function selectEcoPreset(lat, lon, cardIdx) {
    document.getElementById('sp-lat').value = lat;
    document.getElementById('sp-lon').value = lon;

    document.querySelectorAll('.ecoregion-card').forEach((c, i) => {
        c.classList.toggle('active', i === cardIdx);
    });

    resolveSpatial();
}

// ──────────────────────────────────────────────────────────────────────────────
// PANEL 4: KNOWLEDGE VAULT
// ──────────────────────────────────────────────────────────────────────────────
async function searchKB() {
    const rawQuery = document.getElementById('kb-query')?.value?.trim();
    const query    = rawQuery || 'soil organic carbon agroforestry pollinators drought restoration';

    const container = document.getElementById('kb-results');
    if (container) container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <span>Querying RAG knowledge index for "${escapeHtml(query)}"…</span>
        </div>
    `;

    try {
        const res  = await fetch('/api/knowledge/query', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                query,
                domain: activeDomainFilter || null,
                top_k:  5,
            }),
        });
        const data = await res.json();
        renderKBResults(data.results || []);
    } catch (err) {
        if (container) container.innerHTML = `<p style="color:var(--rose);padding:14px;">Query error: ${escapeHtml(err.message)}</p>`;
    }
}

function filterDomain(domain, btn) {
    activeDomainFilter = domain;
    document.querySelectorAll('.domain-filter').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    searchKB();
}

function renderKBResults(chunks) {
    const container = document.getElementById('kb-results');
    if (!container) return;

    if (!chunks || chunks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <h3>No Matches Found</h3>
                <p>Adjust your search query or domain filter to explore the scientific corpus.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = chunks.map(chunk => `
        <div class="kb-chunk-card">
            <div class="kb-chunk-header">
                <div>
                    <div class="kb-chunk-domain">${escapeHtml(chunk.domain || '')}</div>
                    <div class="kb-chunk-topic">${escapeHtml(chunk.topic || '')}</div>
                </div>
                <span class="kb-score">BM25: ${chunk.score}</span>
            </div>

            <div class="kb-vars-row">
                <strong>Key Variables:</strong>
                ${(chunk.key_variables || []).map(v => `<span class="var-pill" style="margin-left:4px;font-size:0.65rem;padding:2px 7px;">${escapeHtml(v)}</span>`).join('')}
            </div>

            <div class="kb-interventions">
                ${(chunk.interventions || []).map(i => `
                    <div class="kb-intervention-item">
                        <strong>${escapeHtml(i.name)}:</strong> ${escapeHtml(i.mechanism)}
                    </div>
                `).join('')}
            </div>

            <div class="kb-cites">
                <strong>Sources:</strong>
                ${(chunk.citations || []).map(c => `<span style="margin-left:6px;font-size:0.69rem;">${escapeHtml(c)}</span>`).join(' ·')}
            </div>
        </div>
    `).join('');
}

// ──────────────────────────────────────────────────────────────────────────────
// FIELD SCENARIOS
// ──────────────────────────────────────────────────────────────────────────────
const SCENARIOS = [
    "Soil organic carbon: 0.3%, rainfall: low, crop: monoculture wheat, region: semi-arid",
    "Biodiversity is declining on my land",
    "26.28, 73.02 — evaluate ecological recovery for rainfed pearl millet with depleted topsoil",
    "Degraded rangeland with bare soil >40%, high soil compaction (bulk density 1.65 g/cm³), and declining perennial grass richness (3 species remaining)",
];

function loadScenario(idx) {
    const text = SCENARIOS[idx - 1];
    if (!text) return;

    switchPanel('intake');

    const input = document.getElementById('intake-input');
    if (input) input.value = text;

    setTimeout(() => submitIntake(), 100);
}

// ──────────────────────────────────────────────────────────────────────────────
// SESSION MANAGEMENT
// ──────────────────────────────────────────────────────────────────────────────
function newSession() {
    currentSessionId        = generateSessionId();
    sessionAccumulatedState = {};
    lastAnalysis            = null;
    updateSessionDisplay();

    // Reset intake stream
    const stream = document.getElementById('intake-stream');
    if (stream) {
        stream.innerHTML = `
            <div class="assessment-card">
                <div class="card-role scientist">
                    <span class="card-role-dot"></span>
                    New Session Initialised
                </div>
                <p style="font-size:0.82rem;color:var(--text-secondary);">
                    Session <code style="font-family:var(--font-mono);color:var(--green);">${currentSessionId}</code> ready.
                    Describe your ecosystem or select a field scenario from the sidebar.
                </p>
            </div>
        `;
    }

    // Reset state panel
    updateSessionStatePanel({}, []);
}

// ──────────────────────────────────────────────────────────────────────────────
// EXPORT
// ──────────────────────────────────────────────────────────────────────────────
function exportReport() {
    const modal = document.getElementById('export-modal-backdrop');
    const textarea = document.getElementById('export-textarea');
    if (!modal || !textarea) return;

    if (!lastAnalysis) {
        textarea.value = `DARUKAA.EARTH ENVIRONMENTAL INTELLIGENCE REPORT\nSession: ${currentSessionId}\n\nNo analysis has been run in this session.\nRun an assessment via Parameter Intake or Diagnostic Matrix first.`;
    } else {
        const state = lastAnalysis.environmental_state || {};
        const nexus = lastAnalysis.multi_metric_nexus  || {};
        const recs  = lastAnalysis.recommendations     || {};

        let report = `DARUKAA.EARTH ENVIRONMENTAL INTELLIGENCE REPORT\n`;
        report    += `Generated: ${new Date().toISOString()}\n`;
        report    += `Session Reference: ${currentSessionId}\n\n`;

        report += `════════════════════════════════════════\nSECTION 1 — ENVIRONMENTAL BASELINE\n════════════════════════════════════════\n`;
        for (const [k, v] of Object.entries(state)) {
            if (v !== null && v !== undefined && typeof v !== 'object') {
                report += `${k}: ${v}\n`;
            }
        }

        report += `\n════════════════════════════════════════\nSECTION 2 — MULTI-METRIC NEXUS\n════════════════════════════════════════\n`;
        report += `${nexus.summary || ''}\n\n`;
        report += `Primary Stressor: ${nexus.primary_stressor || ''}\n`;
        report += `System Trajectory: ${nexus.system_trajectory || ''}\n\n`;
        (nexus.interaction_chains || []).forEach(c => { report += `↳ ${c}\n\n`; });

        report += `\n════════════════════════════════════════\nSECTION 3 — INTERVENTION PRESCRIPTIONS\n════════════════════════════════════════\n\n`;
        (Array.isArray(recs) ? recs : []).forEach((r, i) => {
            report += `[${i + 1}] ${r.title}\n`;
            report += `    Priority   : ${r.priority}\n`;
            report += `    Action     : ${r.action}\n`;
            report += `    Mechanism  : ${r.scientific_mechanism}\n`;
            report += `    Time Horizon: ${r.time_horizon}\n`;
            report += `    Confidence : ${r.confidence_level}\n`;
            report += `    Projected Impacts:\n`;
            (r.multi_metric_impacts || []).forEach(m => {
                report += `      • [${m.dimension}] ${m.metric}: ${m.projected_change}\n`;
            });
            report += `    Scientific Sources:\n`;
            (r.citations || []).forEach(c => { report += `      — ${c}\n`; });
            report += '\n';
        });

        textarea.value = report;
    }

    modal.classList.add('active');
}

function closeExportModal(e) {
    if (!e || e.target.id === 'export-modal-backdrop') {
        document.getElementById('export-modal-backdrop')?.classList.remove('active');
    }
}

function copyReport() {
    const textarea = document.getElementById('export-textarea');
    if (!textarea) return;
    textarea.select();
    navigator.clipboard.writeText(textarea.value).then(() => {
        alert('Scientific report copied to clipboard.');
    }).catch(() => {
        // Fallback
        document.execCommand('copy');
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// Utility
// ──────────────────────────────────────────────────────────────────────────────
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}
