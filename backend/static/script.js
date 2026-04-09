const BACKEND_URL = '';

let gameId = null;
let activeSuspect = 'A';
let gameData = null;

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
const caseFileContent = document.getElementById('case-file-content');
const caseFileButton = document.getElementById('toggle-case-btn');
const feedbackBox = document.getElementById('question-feedback');
const timeDisplay = document.getElementById('time-remaining');
const moodLabel = document.getElementById('detective-style');
const suspectProfile = document.getElementById('suspect-profile');

function appendLine(text, type = 'system') {
  const line = document.createElement('div');
  line.className = `terminal-line ${type}`;
  if (type === 'player') {
    line.innerHTML = `<span class="label">You</span><span>${text}</span>`;
  } else if (type === 'suspect') {
    line.innerHTML = `<span class="label">Suspect</span><span>${text}</span>`;
  } else {
    line.innerHTML = `<span class="label">System</span><span>${text}</span>`;
  }
  terminalOutput.appendChild(line);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function appendFeedback(text) {
  feedbackBox.textContent = text;
}

function clearTerminal() {
  terminalOutput.innerHTML = '';
}

function renderProfile() {
  if (!gameData) {
    suspectProfile.innerHTML = '<div class="profile-card"><div class="profile-badge">Select a suspect to view details</div></div>';
    return;
  }

  const suspect = gameData.suspects.find((item) => item.id === activeSuspect);
  if (!suspect) {
    suspectProfile.innerHTML = '<div class="profile-card"><div class="profile-badge">Suspect not found.</div></div>';
    return;
  }

  suspectProfile.innerHTML = `
    <div class="profile-card">
      <div class="profile-icon">${suspect.icon || '🕵️'}</div>
      <div class="profile-body">
        <h3>${suspect.name}</h3>
        <p><strong>Alias:</strong> ${suspect.alias || 'Unknown'}</p>
        <p><strong>Relation:</strong> ${suspect.relation}</p>
        <p><strong>Motive:</strong> ${suspect.motive}</p>
        <p><strong>Tension:</strong> ${suspect.score ?? 'N/A'}/100</p>
        <p><strong>Mood:</strong> ${suspect.mood || 'Neutral'}</p>
      </div>
    </div>
  `;
}

function renderMeters(scores) {
  meterContainer.innerHTML = '';
  Object.entries(scores).forEach(([suspectId, value]) => {
    const item = document.createElement('div');
    item.className = 'meter-item';
    item.innerHTML = `
      <div class="meter-label"><strong>${suspectId}</strong><span>${value}/100</span></div>
      <div class="meter-track"><div class="meter-fill" style="width: ${Math.min(value, 100)}%"></div></div>
    `;
    meterContainer.appendChild(item);
  });
}

function updateHeader(timeRemaining, mood) {
  timeDisplay.textContent = timeRemaining || '--';
  moodLabel.textContent = mood || 'Focused';
}

function updateSuspectSelection() {
  Object.entries(suspectButtons).forEach(([key, button]) => {
    button.classList.toggle('active', key === activeSuspect);
  });
  renderProfile();
}

function renderCaseFile(caseData) {
  if (!caseData) return;
  caseFileContent.innerHTML = `
    <div class="case-file-summary">
      <div class="case-section">
        <h3>📋 ${caseData.title}</h3>
        <p><strong>Difficulty:</strong> ${caseData.difficulty}</p>
      </div>
      <div class="case-grid">
        <div class="case-card">
          <span class="card-label">Victim</span>
          <strong>${caseData.victim.name}</strong>
          <p>${caseData.victim.role}</p>
        </div>
        <div class="case-card">
          <span class="card-label">Scene</span>
          <strong>${caseData.crime_scene.location}</strong>
          <p>${caseData.crime_scene.time_of_death}</p>
        </div>
        <div class="case-card">
          <span class="card-label">Weapon</span>
          <strong>${caseData.crime_scene.weapon}</strong>
        </div>
      </div>
      <div class="case-section">
        <h4>📝 Brief</h4>
        <p>${caseData.case_summary.trim()}</p>
      </div>
      <div class="case-section">
        <h4>🧩 Evidence</h4>
        <ul class="evidence-list">
          ${caseData.key_evidence.map((item) => `<li>${item}</li>`).join('')}
        </ul>
      </div>
      <button id="case-detail-toggle" class="action-button small">Show full case details</button>
      <div id="case-file-full-details" class="case-file-details hidden">
        <div class="case-section">
          <h4>👤 Victim Background</h4>
          <p>${caseData.victim.background.replace(/\n/g, '<br>')}</p>
        </div>
        <div class="case-section">
          <h4>🔍 Crime Scene Details</h4>
          <p>${caseData.crime_scene.description.replace(/\n/g, '<br>')}</p>
        </div>
      </div>
    </div>
  `;

  caseFileContent.classList.remove('hidden');
  const toggleBtn = document.getElementById('case-detail-toggle');
  const details = document.getElementById('case-file-full-details');
  if (toggleBtn && details) {
    toggleBtn.addEventListener('click', () => {
      const hidden = details.classList.toggle('hidden');
      toggleBtn.textContent = hidden ? 'Show full case details' : 'Hide full case details';
    });
  }
}

function toggleCaseFile() {
  caseFileContent.classList.toggle('hidden');
  caseFileButton.textContent = caseFileContent.classList.contains('hidden') ? '📁 View Case File' : '📁 Hide Case File';
}

async function startGame() {
  clearTerminal();
  appendLine('Opening the case file...', 'system');
  appendFeedback('');

  try {
    const response = await fetch(`${BACKEND_URL}/start`, { method: 'POST' });
    const data = await response.json();
    if (!response.ok) {
      appendLine(`Error: ${data.error || 'Unable to start game.'}`, 'system');
      return;
    }

    gameId = data.game_id;
    gameData = data;
    activeSuspect = gameData.suspects?.[0]?.id || 'A';
    updateSuspectSelection();
    renderMeters(gameData.tension_scores || {});
    const startingMood = gameData.suspects?.find((item) => item.id === activeSuspect)?.mood || 'Focused';
    updateHeader(gameData.time_remaining, startingMood);
    renderCaseFile(gameData.case);
    appendLine('Investigation started. Question the suspects and track tension.', 'system');
    appendFeedback('Select a suspect card and ask a question.');
  } catch (error) {
    appendLine(`Network error: ${error.message}`, 'system');
  }
}

async function interrogate(event) {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    appendFeedback('Ask a specific question before interrogating.');
    return;
  }

  if (!gameId) {
    appendLine('No active investigation. Restart to begin.', 'system');
    return;
  }

  appendLine(question, 'player');
  questionInput.value = '';
  appendFeedback('Interrogating suspect...');

  try {
    const response = await fetch(`${BACKEND_URL}/interrogate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect, question }),
    });
    const data = await response.json();
    if (!response.ok) {
      appendLine(`Error: ${data.error || 'Interrogation failed.'}`, 'system');
      appendFeedback('');
      return;
    }

    gameData = { ...gameData, ...data };
    if (gameData.suspects) {
      gameData.suspects = gameData.suspects.map((item) => {
        if (item.id !== activeSuspect) return item;
        return {
          ...item,
          score: data.suspect?.score ?? item.score,
          mood: data.suspect?.mood ?? item.mood,
          mood_icon: data.suspect?.mood_icon ?? item.mood_icon,
        };
      });
    }
    renderMeters(data.tension_scores || {});
    const responseMood = data.suspect?.mood || gameData.suspects?.find((item) => item.id === activeSuspect)?.mood || 'Focused';
    updateHeader(data.time_remaining, responseMood);
    renderProfile();

    appendLine(data.answer || 'No answer returned.', 'suspect');
    if (data.reason) {
      appendLine(`Reason: ${Array.isArray(data.reason) ? data.reason.join(', ') : data.reason}`, 'system');
    }
    appendFeedback(`Suspect mood: ${responseMood}. Time left: ${data.time_remaining}.`);
  } catch (error) {
    appendLine(`Network error: ${error.message}`, 'system');
    appendFeedback('');
  }
}

async function accuseSuspect() {
  if (!gameId) {
    appendLine('Start an investigation before accusing a suspect.', 'system');
    return;
  }

  appendLine(`You accuse suspect ${activeSuspect}.`, 'player');
  try {
    const response = await fetch(`${BACKEND_URL}/accuse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect }),
    });
    const data = await response.json();
    if (!response.ok) {
      appendLine(`Error: ${data.error || 'Accusation failed.'}`, 'system');
      return;
    }

    appendLine(data.message, 'system');
    appendFeedback(data.correct ? 'Correct! Case closed.' : 'Wrong accusation. Keep investigating.');
  } catch (error) {
    appendLine(`Network error: ${error.message}`, 'system');
  }
}

Object.entries(suspectButtons).forEach(([id, button]) => {
  button.addEventListener('click', () => {
    activeSuspect = id;
    updateSuspectSelection();
    appendLine(`Now interrogating ${id}.`, 'system');
  });
});

questionForm.addEventListener('submit', interrogate);
restartButton.addEventListener('click', () => {
  clearTerminal();
  startGame();
});
accuseButton.addEventListener('click', accuseSuspect);
caseFileButton.addEventListener('click', toggleCaseFile);

window.addEventListener('load', startGame);
