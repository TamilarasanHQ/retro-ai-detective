const BACKEND_URL = '';

let gameId = null;
let activeSuspect = 'A';
let currentCase = null;

const terminalOutput = document.getElementById('terminal-output');
const questionInput = document.getElementById('question-input');
const suspectButtons = {
  A: document.getElementById('suspect-A'),
  B: document.getElementById('suspect-B'),
  C: document.getElementById('suspect-C'),
};
const meterContainer = document.getElementById('meter-container');
const restartButton = document.getElementById('restart-button');
const accuseButton = document.getElementById('accuse-button');
const questionForm = document.getElementById('question-form');

async function startGame() {
  appendSystemLine('Initializing new investigation...');
  try {
    const response = await fetch(`${BACKEND_URL}/start`);
    const data = await response.json();
    if (response.ok) {
      gameId = data.game_id;
      activeSuspect = 'A';
      updateSuspectSelection();
      renderMeters(data.suspicion_scores);
      appendSystemLine(data.message);
      appendSystemLine('Choose a suspect and ask a question.');
      terminalOutput.scrollTop = terminalOutput.scrollHeight;
      loadCaseFile();
    } else {
      appendSystemLine(`Error: ${data.error || 'Unable to start game.'}`);
    }
  } catch (error) {
    appendSystemLine(`Network error: ${error.message}`);
  }
}

async function loadCaseFile() {
  if (!gameId) return;
  try {
    const response = await fetch(`${BACKEND_URL}/case/${gameId}`);
    const data = await response.json();
    if (response.ok) {
      currentCase = data.case;
      displayCaseFile(currentCase);
    }
  } catch (error) {
    console.error('Failed to load case file:', error);
  }
}

function displayCaseFile(caseData) {
  const container = document.getElementById('case-file-content');
  if (!container) return;
  
  const difficultyClass = caseData.difficulty.toLowerCase();
  
  container.innerHTML = `
    <div class="case-quickfacts">
      <div class="quickfact">
        <span class="icon">👤</span>
        <div><div class="label">Victim</div><div class="value">${caseData.victim.name.split(' ')[0]}</div></div>
      </div>
      <div class="quickfact">
        <span class="icon">📍</span>
        <div><div class="label">Location</div><div class="value">${caseData.crime_scene.location.split(',')[0]}</div></div>
      </div>
      <div class="quickfact">
        <span class="icon">⏰</span>
        <div><div class="label">Time</div><div class="value">${caseData.crime_scene.time_of_death.split(' ').slice(0,3).join(' ')}</div></div>
      </div>
    </div>
    <div class="case-sections">
      <div class="case-section">
        <div class="section-header" onclick="toggleSection(this)"><span class="icon">👤</span><h4>Victim Profile</h4><span class="arrow">▼</span></div>
        <div class="section-content"><strong>${caseData.victim.name}</strong>, ${caseData.victim.age}<br><span style="color:var(--muted);">${caseData.victim.role}</span><br><br>${caseData.victim.background}</div>
      </div>
      <div class="case-section">
        <div class="section-header" onclick="toggleSection(this)"><span class="icon">🔍</span><h4>Crime Scene</h4><span class="arrow">▼</span></div>
        <div class="section-content"><strong>📍</strong> ${caseData.crime_scene.location}<br><strong>⏰</strong> ${caseData.crime_scene.time_of_death}<br><strong>🗡️</strong> ${caseData.crime_scene.weapon}<br><br>${caseData.crime_scene.description.replace(/\n/g,'<br>')}</div>
      </div>
      <div class="case-section">
        <div class="section-header" onclick="toggleSection(this)"><span class="icon">👥</span><h4>Suspect Connections</h4><span class="arrow">▼</span></div>
        <div class="section-content">
          <div class="suspect-connections">
            <div class="connection-card" data-suspect="A"><span class="suspect-badge">🔴 Alex (A)</span><span class="connection-text">${caseData.connections?.A || 'Alex frequently assisted Dr. Voss with technical issues.'}</span></div>
            <div class="connection-card" data-suspect="B"><span class="suspect-badge">🔵 Brooke (B)</span><span class="connection-text">${caseData.connections?.B || 'Brooke was helping Dr. Voss authenticate manuscripts.'}</span></div>
            <div class="connection-card" data-suspect="C"><span class="suspect-badge">🟡 Casey (C)</span><span class="connection-text">${caseData.connections?.C || 'Casey delivered packages to Dr. Voss weekly.'}</span></div>
          </div>
        </div>
      </div>
      <div class="case-section">
        <div class="section-header" onclick="toggleSection(this)"><span class="icon">🧩</span><h4>Key Evidence</h4><span class="arrow">▼</span></div>
        <div class="section-content"><div class="evidence-tags">${caseData.key_evidence.map(item => `<span class="evidence-tag">${item}</span>`).join('')}</div></div>
      </div>
      <div class="case-section">
        <div class="section-header" onclick="toggleSection(this)"><span class="icon">📝</span><h4>Case Brief</h4><span class="arrow">▶</span></div>
        <div class="section-content collapsed"><span class="difficulty-badge ${difficultyClass}">${caseData.difficulty}</span><p style="margin-top:10px;">${caseData.case_summary.replace(/\n/g,'<br>')}</p></div>
      </div>
    </div>
  `;
}

function toggleSection(header) {
  const content = header.nextElementSibling;
  const arrow = header.querySelector('.arrow');
  if (content.classList.contains('collapsed')) {
    content.classList.remove('collapsed');
    arrow.textContent = '▼';
  } else {
    content.classList.add('collapsed');
    arrow.textContent = '▶';
  }
}
window.toggleSection = toggleSection;

function updateSuspectSelection() {
  Object.entries(suspectButtons).forEach(([key, button]) => {
    button.classList.toggle('active', key === activeSuspect);
  });
}

function selectSuspect(suspectId) {
  activeSuspect = suspectId;
  updateSuspectSelection();
  appendSystemLine(`Selected suspect ${suspectId}.`);
}

function renderMeters(scores) {
  meterContainer.innerHTML = '';
  Object.entries(scores).forEach(([suspectId, score]) => {
    const item = document.createElement('div');
    item.className = 'meter-item';
    item.innerHTML = `<div class="meter-label"><strong>Suspect ${suspectId}</strong><span>${score}%</span></div><div class="meter-track"><div class="meter-fill" style="width:${score}%"></div></div>`;
    meterContainer.appendChild(item);
  });
}

function appendLine(text, type = 'line-system') {
  const line = document.createElement('div');
  line.className = `terminal-line ${type}`;
  line.innerHTML = `<span class="label">${type === 'line-player' ? 'You ask' : type === 'line-ai' ? 'Answer' : 'System'}</span><span>${text}</span>`;
  terminalOutput.appendChild(line);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function appendSystemLine(text) {
  appendLine(text, 'line-system');
}

async function interrogate(event) {
  if (event) event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) { appendSystemLine('Enter a question before interrogating.'); return; }
  if (!gameId) { appendSystemLine('Game not started yet.'); return; }
  appendLine(question, 'line-player');
  questionInput.value = '';
  try {
    const response = await fetch(`${BACKEND_URL}/interrogate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect, question }),
    });
    const data = await response.json();
    if (response.ok) {
      appendLine(data.answer, 'line-ai');
      renderMeters(data.suspicion_scores);
      appendSystemLine(data.message);
    } else {
      appendSystemLine(`Error: ${data.error || 'Unable to interrogate.'}`);
    }
  } catch (error) {
    appendSystemLine(`Network error: ${error.message}`);
  }
}

async function accuseSuspect() {
  if (!gameId) { appendSystemLine('Start a game before accusing.'); return; }
  appendSystemLine(`Accusing suspect ${activeSuspect}...`);
  try {
    const response = await fetch(`${BACKEND_URL}/accuse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect }),
    });
    const data = await response.json();
    if (response.ok) {
      appendSystemLine(data.message);
      if (data.correct) appendSystemLine('Investigation complete. Restart to play again.');
      else appendSystemLine('Keep questioning the other suspects.');
    } else {
      appendSystemLine(`Error: ${data.error || 'Unable to accuse.'}`);
    }
  } catch (error) {
    appendSystemLine(`Network error: ${error.message}`);
  }
}

suspectButtons.A.addEventListener('click', () => selectSuspect('A'));
suspectButtons.B.addEventListener('click', () => selectSuspect('B'));
suspectButtons.C.addEventListener('click', () => selectSuspect('C'));
questionForm.addEventListener('submit', interrogate);
restartButton.addEventListener('click', () => {
  terminalOutput.innerHTML = '';
  startGame();
});
accuseButton.addEventListener('click', accuseSuspect);

document.querySelectorAll('.quick-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    questionInput.value = btn.dataset.question;
    interrogate();
  });
});

document.getElementById('toggle-case-btn')?.addEventListener('click', async () => {
  const content = document.getElementById('case-file-content');
  const btn = document.getElementById('toggle-case-btn');
  if (content.classList.contains('hidden')) {
    await loadCaseFile();
    content.classList.remove('hidden');
    btn.textContent = '📋 Hide Case File';
  } else {
    content.classList.add('hidden');
    btn.textContent = '📋 Case File';
  }
});

window.addEventListener('load', startGame);