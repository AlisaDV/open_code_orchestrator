const state = {
  runs: [],
  selectedRun: null,
  timelineEvents: [],
  timelineTypeFilter: 'all',
  timelineStatusFilter: 'all',
};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function fetchJsonOptional(url) {
  const response = await fetch(url)
  if (response.status === 404) return null
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json()
}

function fmt(value) {
  if (!value) return '-';
  return new Date(value).toLocaleString();
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function toFileUrl(filePath) {
  if (!filePath) return null;
  const normalized = String(filePath).replaceAll('\\', '/');
  return `file:///${normalized}`;
}

function renderRuns() {
  const host = document.getElementById('runs-list');
  document.getElementById('run-count').textContent = String(state.runs.length);
  if (!state.runs.length) {
    host.innerHTML = '<div class="empty">No runs recorded yet.</div>';
    return;
  }

  host.innerHTML = state.runs.map((run) => `
    <article class="item run-item ${state.selectedRun?.run_id === run.run_id ? 'selected' : ''}">
      <div class="kv">
        <strong>${escapeHtml(run.objective)}</strong>
        <span class="small muted">${run.run_id}</span>
        <span class="small">status: ${escapeHtml(run.status)} | events: ${run.event_count} | files: ${run.file_count}</span>
        <span class="small muted">started: ${fmt(run.started_at)}</span>
      </div>
      <div class="run-chip-row">
        <span class="pill">approvals ${run.approval_count}</span>
        <span class="pill">verification ${run.verification_count}</span>
      </div>
      <div style="margin-top: 12px;">
        <button class="button primary" data-run-id="${run.run_id}">Open</button>
      </div>
    </article>
  `).join('');
}

function renderBrowserSmoke(report) {
  const host = document.getElementById('browser-smoke-summary')
  if (!report) {
    host.innerHTML = '<div class="empty">No browser smoke report imported yet.</div>'
    return
  }

  host.innerHTML = `
    <article class="item">
      <div class="kv">
        <strong>${escapeHtml(report.target_url)}</strong>
        <span class="small muted">started: ${fmt(report.started_at)} | finished: ${fmt(report.finished_at)}</span>
        <span class="small">total: ${report.total} | passed: ${report.passed} | failed: ${report.failed}</span>
      </div>
      <div class="run-chip-row">
        ${(report.scenarios || []).map((scenario) => `<span class="pill">${escapeHtml(scenario.scenario_name)}: ${escapeHtml(scenario.status)}</span>`).join('')}
      </div>
      <div class="list" style="margin-top: 12px;">
        ${(report.scenarios || []).map((scenario) => {
          const screenshot = toFileUrl(scenario.artifacts?.successScreenshot || scenario.artifacts?.screenshotPath)
          const consoleLink = toFileUrl(scenario.artifacts?.console || scenario.artifacts?.consolePath)
          const networkLink = toFileUrl(scenario.artifacts?.network || scenario.artifacts?.networkPath)
          return `
            <article class="item">
              <div class="kv">
                <strong>${escapeHtml(scenario.scenario_name)}</strong>
                <span class="small">status: ${escapeHtml(scenario.status)}</span>
                <span class="small muted">started: ${fmt(scenario.started_at)} | finished: ${fmt(scenario.finished_at)}</span>
                ${scenario.error ? `<pre>${escapeHtml(scenario.error)}</pre>` : ''}
              </div>
              <div class="artifact-links">
                ${screenshot ? `<a href="${screenshot}" target="_blank" rel="noreferrer">screenshot</a>` : ''}
                ${consoleLink ? `<a href="${consoleLink}" target="_blank" rel="noreferrer">console</a>` : ''}
                ${networkLink ? `<a href="${networkLink}" target="_blank" rel="noreferrer">network</a>` : ''}
              </div>
            </article>
          `
        }).join('')}
      </div>
    </article>
  `
}

function renderRunSummary(run, events, files, approvals, verification) {
  document.getElementById('run-status').textContent = run.status;
  document.getElementById('summary-objective').textContent = run.objective;
  document.getElementById('summary-started').textContent = fmt(run.started_at);
  document.getElementById('summary-finished').textContent = fmt(run.finished_at);
  document.getElementById('summary-workspace').textContent = run.workspace || '-';
  document.getElementById('metric-events').textContent = String(events.length);
  document.getElementById('metric-files').textContent = String(files.length);
  document.getElementById('metric-approvals').textContent = String(approvals.length);
  document.getElementById('metric-verification').textContent = String(verification.length);
  document.getElementById('metric-passed').textContent = String(verification.filter((item) => item.status === 'passed').length);
  document.getElementById('metric-failed').textContent = String(verification.filter((item) => item.status === 'failed').length);
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('detail-content').classList.remove('hidden');
}

function populateTimelineFilters(events) {
  const typeSelect = document.getElementById('timeline-type-filter');
  const statusSelect = document.getElementById('timeline-status-filter');
  const currentType = state.timelineTypeFilter;
  const currentStatus = state.timelineStatusFilter;

  const types = [...new Set(events.map((event) => event.event_type).filter(Boolean))].sort();
  const statuses = [...new Set(events.map((event) => event.status).filter(Boolean))].sort();

  typeSelect.innerHTML = `<option value="all">All Types</option>${types.map((value) => `<option value="${value}">${value}</option>`).join('')}`;
  statusSelect.innerHTML = `<option value="all">All Statuses</option>${statuses.map((value) => `<option value="${value}">${value}</option>`).join('')}`;
  typeSelect.value = types.includes(currentType) ? currentType : 'all';
  statusSelect.value = statuses.includes(currentStatus) ? currentStatus : 'all';
}

function renderTimeline(events) {
  const host = document.getElementById('timeline');
  populateTimelineFilters(events);

  const filtered = events.filter((event) => {
    const typeOk = state.timelineTypeFilter === 'all' || event.event_type === state.timelineTypeFilter;
    const statusOk = state.timelineStatusFilter === 'all' || event.status === state.timelineStatusFilter;
    return typeOk && statusOk;
  });

  if (!filtered.length) {
    host.innerHTML = '<div class="empty">No timeline events.</div>';
    return;
  }

  const groups = new Map();
  for (const event of filtered) {
    const key = event.phase || 'no-phase';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(event);
  }

  host.innerHTML = [...groups.entries()].map(([phase, items]) => `
    <section class="phase-group">
      <div class="phase-header">${escapeHtml(phase === 'no-phase' ? 'Global Events' : phase)}</div>
      ${items.map((event) => `
        <article class="item">
          <div class="kv">
            <strong>${escapeHtml(event.title || event.event_type)}</strong>
            <span class="small">${escapeHtml(event.event_type)} | ${escapeHtml(event.agent || '-')} | ${escapeHtml(event.status || '-')}</span>
            <span class="small muted">${fmt(event.ts)}</span>
          </div>
          <pre>${escapeHtml(JSON.stringify(event.payload || {}, null, 2))}</pre>
        </article>
      `).join('')}
    </section>
  `).join('');
}

function renderFiles(files) {
  const host = document.getElementById('files');
  if (!files.length) {
    host.innerHTML = '<div class="empty">No file impact records.</div>';
    return;
  }
  host.innerHTML = files.map((file) => `
    <article class="item">
      <div class="kv">
        <strong>${escapeHtml(file.path)}</strong>
        <span class="small">changes: ${file.change_count} | type: ${escapeHtml(file.last_change_type || '-')}</span>
        <span class="small muted">agents: ${escapeHtml((file.agents || []).join(', ') || '-')}</span>
        <span class="small muted">phases: ${escapeHtml((file.phases || []).join(', ') || '-')}</span>
        <span class="small">${escapeHtml(file.last_summary || '')}</span>
      </div>
    </article>
  `).join('');
}

function renderApprovals(items) {
  const host = document.getElementById('approvals');
  if (!items.length) {
    host.innerHTML = '<div class="empty">No approvals.</div>';
    return;
  }
  host.innerHTML = items.map((item) => `
    <article class="item">
      <div class="kv">
        <strong>${escapeHtml(item.tool_name)}</strong>
        <span class="small">status: ${escapeHtml(item.status)}</span>
        <span class="small muted">requested: ${fmt(item.requested_at)}</span>
        <span class="small muted">resolved: ${fmt(item.resolved_at)}</span>
      </div>
      <pre>${escapeHtml(JSON.stringify(item.arguments || {}, null, 2))}</pre>
    </article>
  `).join('');
}

function renderVerification(items) {
  const host = document.getElementById('verification');
  if (!items.length) {
    host.innerHTML = '<div class="empty">No verification results.</div>';
    return;
  }
  host.innerHTML = items.map((item) => `
    <article class="item">
      <div class="kv">
        <strong>${escapeHtml(item.kind)}</strong>
        <span class="small ${item.status === 'passed' ? 'status-passed' : item.status === 'failed' ? 'status-failed' : ''}">status: ${escapeHtml(item.status)}</span>
        <span class="small muted">command: ${escapeHtml(item.command || '-')}</span>
        <span class="small muted">duration: ${item.duration_ms ?? '-'} ms</span>
      </div>
      <pre>${escapeHtml(JSON.stringify(item.details || {}, null, 2))}</pre>
    </article>
  `).join('');
}

function buildGraph(run, events, files, approvals, verification) {
  const nodes = [];
  const edges = [];
  const seenNodes = new Set();

  const addNode = (id, label, type) => {
    if (seenNodes.has(id)) return;
    seenNodes.add(id);
    nodes.push({ id, label, type });
  };

  addNode(`run:${run.run_id}`, run.objective, 'run');

  for (const event of events) {
    const eventId = `event:${event.event_id}`;
    addNode(eventId, event.title || event.event_type, 'event');
    edges.push({ from: `run:${run.run_id}`, to: eventId, label: event.event_type });

    if (event.agent) {
      const agentId = `agent:${event.agent}`;
      addNode(agentId, event.agent, 'agent');
      edges.push({ from: eventId, to: agentId, label: 'agent' });
    }
  }

  for (const file of files) {
    const fileId = `file:${file.path}`;
    addNode(fileId, file.path, 'file');
    edges.push({ from: `run:${run.run_id}`, to: fileId, label: file.last_change_type || 'file' });
    for (const agent of file.agents || []) {
      const agentId = `agent:${agent}`;
      addNode(agentId, agent, 'agent');
      edges.push({ from: agentId, to: fileId, label: 'changed' });
    }
  }

  for (const approval of approvals) {
    const approvalId = `approval:${approval.approval_id}`;
    addNode(approvalId, approval.tool_name, 'approval');
    edges.push({ from: `run:${run.run_id}`, to: approvalId, label: approval.status });
  }

  for (const item of verification) {
    const verificationId = `verification:${item.kind}:${item.command || 'none'}`;
    addNode(verificationId, `${item.kind} ${item.status}`, 'verification');
    edges.push({ from: `run:${run.run_id}`, to: verificationId, label: item.status });
  }

  return { nodes, edges };
}

function renderGraph(run, events, files, approvals, verification) {
  const nodeHost = document.getElementById('graph-nodes');
  const edgeHost = document.getElementById('graph-edges');
  const graph = buildGraph(run, events, files, approvals, verification);

  nodeHost.innerHTML = graph.nodes.map((node) => `
    <article class="item graph-node">
      <div class="node-type">${escapeHtml(node.type)}</div>
      <strong>${escapeHtml(node.label)}</strong>
      <div class="small muted">${escapeHtml(node.id)}</div>
    </article>
  `).join('');

  edgeHost.innerHTML = graph.edges.map((edge) => `
    <article class="item graph-edge">
      <div class="small muted">${escapeHtml(edge.from)}</div>
      <strong>${escapeHtml(edge.label)}</strong>
      <div class="small muted">${escapeHtml(edge.to)}</div>
    </article>
  `).join('');
}

async function loadRuns() {
  state.runs = await fetchJson('/runs');
  renderRuns();
}

async function loadBrowserSmoke() {
  const report = await fetchJsonOptional('/browser-smoke/latest')
  renderBrowserSmoke(report)
}

async function loadRunDetails(runId) {
  const [run, events, files, approvals, verification] = await Promise.all([
    fetchJson(`/runs/${runId}`),
    fetchJson(`/runs/${runId}/events`),
    fetchJson(`/runs/${runId}/files`),
    fetchJson(`/runs/${runId}/approvals`),
    fetchJson(`/runs/${runId}/verification`),
  ]);
  state.selectedRun = run;
  state.timelineEvents = events;
  renderRuns();
  renderRunSummary(run, events, files, approvals, verification);
  renderTimeline(events);
  renderFiles(files);
  renderApprovals(approvals);
  renderVerification(verification);
  renderGraph(run, events, files, approvals, verification);
}

document.body.addEventListener('click', async (event) => {
  const target = event.target;
  if (target.dataset.runId) {
    await loadRunDetails(target.dataset.runId);
  }
});

document.getElementById('refresh-button').addEventListener('click', async () => {
  await loadRuns();
  await loadBrowserSmoke();
  if (state.selectedRun?.run_id) {
    await loadRunDetails(state.selectedRun.run_id);
  }
});

document.getElementById('timeline-type-filter').addEventListener('change', (event) => {
  state.timelineTypeFilter = event.target.value;
  renderTimeline(state.timelineEvents);
});

document.getElementById('timeline-status-filter').addEventListener('change', (event) => {
  state.timelineStatusFilter = event.target.value;
  renderTimeline(state.timelineEvents);
});

(async function init() {
  await loadRuns();
  await loadBrowserSmoke();
  if (state.runs[0]) {
    await loadRunDetails(state.runs[0].run_id);
  }
})();
