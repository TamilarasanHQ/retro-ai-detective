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

function displayCaseFile(caseData) {
  if (!caseData) return;
  
  document.getElementById('case-title').textContent = caseData.title || 'Case File';
  document.getElementById('victim-name').textContent = caseData.victim || 'Unknown';
  document.getElementById('location-name').textContent = caseData.crime_scene || 'Unknown Location';
  document.getElementById('case-description').textContent = caseData.case_summary || '';
  
  const evidenceList = document.getElementById('evidence-list');
  evidenceList.innerHTML = '';
  
  const evidence = caseData.key_evidence || [];
  if (Array.isArray(evidence)) {
    evidence.forEach(item => {
      const div = document.createElement('div');
      div.className = 'evidence-item';
      div.textContent = '🔗 ' + item;
      evidenceList.appendChild(div);
    });
  }
}

function displaySuspectProfile(suspect) {
  if (!suspect) return;
  
  document.getElementById('suspect-name').textContent = suspect.name || 'Unknown';
  document.getElementById('alias-text').textContent = suspect.alias || 'N/A';
  document.getElementById('title-text').textContent = suspect.title || 'N/A';
  document.getElementById('bio-text').textContent = suspect.bio || 'No information available';
  
  const moodDisplay = document.getElementById('suspect-mood-display');
  const mood = suspect.mood || 'Unknown';
  const moodIcon = suspect.mood_icon || '❓';
  moodDisplay.innerHTML = `<div>${moodIcon} <strong>Current Mood:</strong> ${mood}</div><div>📊 <strong>Tension Level:</strong> ${suspect.score}%</div>`;
}

async function startGame() {
  appendSystemLine('Initializing new investigation...');
  try {
    const response = await fetch(`${BACKEND_URL}/start`);
    const data = await response.json();
    if (response.ok) {
      gameId = data.game_id;
      gameData = data;
      activeSuspect = 'A';
      
      // Display case file
      displayCaseFile(data.case);
      
      // Display initial suspect profile
      const suspects = data.suspects || [];
      const suspectMap = {};
      suspects.forEach(s => {
        suspectMap[s.id] = s;
      });
      if (suspectMap['A']) {
        displaySuspectProfile(suspectMap['A']);
      }
      
      updateSuspectSelection();
      renderMeters(data.suspicion_scores);
      appendSystemLine(data.message);
      appendSystemLine('Choose a suspect and ask a question.');
      terminalOutput.scrollTop = terminalOutput.scrollHeight;
    } else {
      appendSystemLine(`Error: ${data.error || 'Unable to start game.'}`);
    }
  } catch (error) {
    appendSystemLine(`Network error: ${error.message}`);
  }
}


function updateSuspectSelection() {
  Object.entries(suspectButtons).forEach(([key, button]) => {
    button.classList.toggle('active', key === activeSuspect);
  });
}

function selectSuspect(suspectId) {
  activeSuspect = suspectId;
  updateSuspectSelection();
  
  // Update profile display
  if (gameData && gameData.suspects) {
    const suspect = gameData.suspects.find(s => s.id === suspectId);
    if (suspect) {
      displaySuspectProfile(suspect);
    }
  }
  
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

function parseActionCues(text) {
  // Action cues are no longer used
  return text;
}

function appendLine(text, type = 'line-system') {
  const line = document.createElement('div');
  line.className = `terminal-line ${type}`;
  const formattedText = text;
  line.innerHTML = `<span class="label">${type === 'line-player' ? 'You ask' : type === 'line-ai' ? 'Answer' : 'System'}</span><span>${formattedText}</span>`;
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
      
      // Update gameData with new suspect info
      if (data.suspects) {
        gameData.suspects = data.suspects;
        const activeSuspectData = data.suspects.find(s => s.id === activeSuspect);
        if (activeSuspectData) {
          displaySuspectProfile(activeSuspectData);
        }
      }
      
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
      if (data.outcome_rank) {
        appendSystemLine(`=== OUTCOME: ${data.outcome_rank.toUpperCase()} ===`);
      }
      appendSystemLine(data.message);
      if (data.correct) appendSystemLine('Investigation complete. Restart to play again.');
      else appendSystemLine('Case closed in failure. Restart to try again.');
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



window.addEventListener('load', startGame);