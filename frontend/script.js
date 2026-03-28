let state = {
    sessionId: null,
    selectedTask: 'support-easy-v1',
    currentAction: 'classify',
    cumulativeReward: 0,
    steps: 0,
    maxSteps: 5,
    totalSessions: 0,
    ended: false,
  };

  const BASE = () => document.getElementById('baseUrlInput').value.replace(/\/$/, '');
  const API_KEY = () => document.getElementById('apiKeyInput').value;
  const headers = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY()}`
  });

  /* ─── Health check ─── */
  async function checkHealth() {
    try {
      const r = await fetch(`${BASE()}/health`);
      const ok = r.ok;
      document.getElementById('statusDot').className = `status-dot ${ok ? 'online' : ''}`;
      document.getElementById('statusText').textContent = ok ? 'Server Online' : 'Offline';
    } catch { 
      document.getElementById('statusDot').className = 'status-dot';
      document.getElementById('statusText').textContent = 'Offline';
    }
  }
  checkHealth();
  setInterval(checkHealth, 10000);

  /* ─── Task selection ─── */
  function selectTask(el) {
    document.querySelectorAll('.task-card').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    state.selectedTask = el.dataset.task;
    const steps = { 'support-easy-v1': 5, 'support-medium-v1': 10, 'support-hard-v1': 20 };
    state.maxSteps = steps[state.selectedTask] || 5;
  }

  function selectAction(action, el) {
    state.currentAction = action;
    document.querySelectorAll('.action-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    const needsContent = el.dataset.needsContent === 'true';
    const inp = document.getElementById('actionInput');
    inp.disabled = !needsContent;
    inp.placeholder = needsContent
      ? {classify:'e.g. I need a refund for order #1234', retrieve:'e.g. refund policy', respond:'Type your response to the customer...', clarify:'e.g. Could you provide your order number?'}[action] || 'Type content...'
      : `No content needed for "${action}" — just click Send`;
    if (needsContent) inp.focus();
  }

  /* ─── Start Session ─── */
  async function startSession() {
    setLoading(true);
    try {
      const r = await fetch(`${BASE()}/env/reset`, { method:'POST', headers:headers(), body: JSON.stringify({task_id: state.selectedTask}) });
      if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
      const data = await r.json();
      state.sessionId = data.session_id;
      state.cumulativeReward = 0;
      state.steps = 0;
      state.ended = false;
      state.totalSessions++;

      document.getElementById('sessionBadge').textContent = state.sessionId?.slice(0,20) + '…';
      document.getElementById('welcomeMsg').style.display = 'none';
      document.getElementById('chatArea').style.display = 'flex';
      document.getElementById('actionPanel').style.display = 'block';
      document.getElementById('chatArea').innerHTML = '';

      document.getElementById('resetBtn').disabled = false;
      document.getElementById('gradeBtn').disabled = false;
      document.getElementById('startBtn').textContent = '↺ New Session';

      updateStats();
      toast('Session started!', 'success');

      // Show ticket from observation
      if(data.observation) {
      // Parse observation cleanly
      const obs = data.observation || {};
      let ticketText = obs.ticket_text || obs.observation_text || obs.message || '';
      // If it's still an object, try JSON fields
      if (!ticketText && typeof obs === 'object') {
        ticketText = obs.text || obs.content || '';
      }
      // Extract ticket text from observation_text if it contains "Ticket:"
      if (obs.observation_text && obs.observation_text.includes('Ticket:')) {
        const match = obs.observation_text.match(/Ticket:\s*([\s\S]*?)(?:\n\nPlease|$)/);
        if (match) ticketText = match[1].trim();
        else ticketText = obs.observation_text;
      }
      if (ticketText) appendMsg('ai', '🎟 Customer Ticket', ticketText, null);
      }
      // First action hint
      selectAction('classify', document.querySelector('.action-tab'));

    } catch(e) { toast(e.message, 'error'); }
    setLoading(false);
  }

  /* ─── Submit Action ─── */
  async function submitAction() {
    if(!state.sessionId) { toast('Start a session first!', 'error'); return; }
    if(state.ended) { toast('Session ended. Start a new one.', 'info'); return; }
    const inp = document.getElementById('actionInput');
    const needsContent = document.querySelector('.action-tab.active').dataset.needsContent === 'true';
    const content = inp.value.trim();
    if(needsContent && !content) { inp.focus(); return; }

    setLoading(true);
    const actionPayload = { type: state.currentAction };
    if(needsContent && content) actionPayload.content = content;

    // Show user message
    const label = {classify:'🏷 Classify',retrieve:'🔍 Retrieve KB',respond:'💬 Respond',clarify:'❓ Clarify',resolve:'✅ Resolve',escalate:'🚨 Escalate'}[state.currentAction];
    appendMsg('user', label, content || `(${state.currentAction})`, null);
    inp.value = '';

    try {
      const r = await fetch(`${BASE()}/env/step`, {
        method:'POST', headers:headers(),
        body: JSON.stringify({ session_id: state.sessionId, action: actionPayload })
      });
      if(!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
      const data = await r.json();

      state.steps++;
      const rwd = data.reward ?? 0;
      state.cumulativeReward += rwd;
      const done = data.done ?? false;

      // KB results display
      let extra = '';
      if(state.currentAction === 'retrieve' && data.observation?.kb_results?.length) {
        extra = data.observation.kb_results.map(r => 
          `<div class="kb-item"><strong>[${(r.doc_id||'').slice(0,8)}]</strong> ${r.snippet||r.content||''}</div>`
        ).join('');
        extra = `<div class="kb-results">${extra}</div>`;
      }
      const obsMsg = data.observation?.message || data.message || (done ? 'Session ended.' : '');
      appendMsg('ai', '🤖 Agent Response', obsMsg + extra, rwd, done);

      if(done) {
        state.ended = true;
        appendSystemMsg('Session complete! Click 📊 Grade to see your final score.');
      }
      updateStats();
    } catch(e) { toast(e.message, 'error'); }
    setLoading(false);
  }

  /* ─── Grade ─── */
  async function gradeSession() {
    if(!state.sessionId) return;
    setLoading(true);
    try {
      const r = await fetch(`${BASE()}/grader`, { method:'POST', headers:headers(), body: JSON.stringify({session_id:state.sessionId}) });
      if(!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
      const data = await r.json();
      const score = data.score ?? 0;
      const passed = data.passed ?? false;
      const chat = document.getElementById('chatArea');
      const card = document.createElement('div');
      card.innerHTML = `
        <div class="score-card">
          <p style="color:var(--muted);font-size:13px;margin-bottom:4px;">Final Score</p>
          <h2>${score}</h2>
          <span class="passed-badge ${passed?'pass':'fail'}">${passed?'✅ PASSED':'❌ FAILED'}</span>
          ${data.breakdown ? `<div style="margin-top:12px;font-size:12px;color:var(--muted);">${Object.entries(data.breakdown).map(([k,v])=>`<span style="margin:0 6px;">${k}: <strong style="color:var(--text)">${v}</strong></span>`).join('')}</div>` : ''}
        </div>`;
      chat.appendChild(card);
      chat.scrollTop = chat.scrollHeight;
    } catch(e) { toast(e.message, 'error'); }
    setLoading(false);
  }

  /* ─── Reset ─── */
  async function resetSession() {
    state.sessionId = null; state.cumulativeReward = 0; state.steps = 0; state.ended = false;
    document.getElementById('sessionBadge').textContent = 'No active session';
    document.getElementById('chatArea').innerHTML = '';
    document.getElementById('chatArea').style.display = 'none';
    document.getElementById('actionPanel').style.display = 'none';
    document.getElementById('welcomeMsg').style.display = 'flex';
    document.getElementById('cumulativeReward').textContent = '—';
    document.getElementById('cumulativeReward').className = 'reward-val';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('resetBtn').disabled = true;
    document.getElementById('gradeBtn').disabled = true;
    document.getElementById('startBtn').textContent = '▶ Start Session';
    updateStats();
    toast('Session reset.', 'info');
  }

  /* ─── Helpers ─── */
  function appendMsg(role, label, content, reward, done=false) {
    const chat = document.getElementById('chatArea');
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    const chip = reward!=null ? `<div class="reward-chip ${reward>=0?'pos':'neg'}">${reward>=0?'▲':'▼'} ${reward>=0?'+':''}${reward.toFixed(2)}</div>` : '';
    const doneTag = done ? `<div style="margin-top:6px;font-size:11px;color:var(--muted);">🏁 Episode ended</div>` : '';
    div.innerHTML = `
      <div class="avatar ${role}-av">${role==='ai'?'🤖':'👤'}</div>
      <div class="bubble">
        <div class="role-label">${label}</div>
        <div>${content}</div>
        ${chip}${doneTag}
      </div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function appendSystemMsg(msg) {
    const chat = document.getElementById('chatArea');
    const div = document.createElement('div');
    div.className = 'msg system';
    div.innerHTML = `<div class="bubble">${msg}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }

  function updateStats() {
    document.getElementById('statSteps').textContent = state.steps;
    const r = state.cumulativeReward;
    document.getElementById('statReward').textContent = r.toFixed(2);
    document.getElementById('statReward').style.color = r >= 0 ? 'var(--success)' : 'var(--danger)';
    document.getElementById('statStatus').textContent = state.ended ? 'Done' : (state.sessionId ? 'Active' : '—');
    document.getElementById('statTasks').textContent = state.totalSessions;

    const el = document.getElementById('cumulativeReward');
    el.textContent = r.toFixed(2);
    el.className = `reward-val ${r > 0 ? 'positive' : r < 0 ? 'negative' : ''}`;

    const pct = Math.min(100, (state.steps / state.maxSteps) * 100);
    document.getElementById('progressFill').style.width = `${pct}%`;
  }

  function setLoading(on) {
    document.getElementById('submitBtn').disabled = on;
    document.getElementById('submitBtn').innerHTML = on ? '<span class="spinner"></span>' : 'Send →';
    document.getElementById('startBtn').disabled = on;
  }

  let toastTimer;
  function toast(msg, type='info') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = `show ${type}`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.className = type, 3000);
  }

  // Auto-select first task
  selectTask(document.querySelector('.task-card'));