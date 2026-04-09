const BACKEND_URL = '';

let gameId = null;
let activeSuspect = null;
let currentCase = null;
let isTyping = false;
let isGameOver = false;

const terminalOutput = document.getElementById('terminal-output');
const questionInput = document.getElementById('question-input');
const questionForm = document.getElementById('question-form');
const restartButtonTop = document.getElementById('restart-button-top');
const restartButton = document.getElementById('restart-button');
const accuseButton = document.getElementById('accuse-button');
const caseFileBtn = document.getElementById('case-file-btn');
const caseModal = document.getElementById('case-modal');
const closeModalBtn = document.getElementById('close-modal');

let suspectCards = {};
let meterFills = {};

async function startGame() {
  appendSystemLine('INITIALIZING SECURE LINK TO PRECINCT MAINFRAME...');
  try {
    const response = await fetch(`${BACKEND_URL}/start`);
    const data = await response.json();
    if (response.ok) {
      gameId = data.game_id;
      isGameOver = false;
      renderMeters(data.tension_scores);
      if (data.time_remaining !== undefined) {
        document.getElementById('time-remaining-val').textContent = data.time_remaining;
      }
      appendSystemLine(data.message);
      appendSystemLine('Awaiting investigator input...');
      
      if (data.case) {
        currentCase = data.case;
        updateSuspectInfo(data.suspects);
        populateCaseFile(data.case);
      }
    } else {
      appendSystemLine(`ERROR: ${data.error || 'Connection refused.'}`);
    }
  } catch (error) {
    appendSystemLine(`SYS_ERR: ${error.message}`);
  }
}

function updateSuspectInfo(suspects) {
  if (!suspects) return;
  const container = document.getElementById('suspect-panel-container');
  // Remove existing generated cards
  document.querySelectorAll('.suspect-card').forEach(el => el.remove());
  suspectCards = {};
  meterFills = {};
  
  if (suspects.length > 0) {
    activeSuspect = suspects[0].id;
  }

  suspects.forEach(suspect => {
    const card = document.createElement('div');
    card.className = 'suspect-card';
    card.id = `card-${suspect.id}`;
    card.onclick = () => selectSuspect(suspect.id);
    
    const portrait = document.createElement('div');
    portrait.className = 'suspect-portrait';
    portrait.textContent = suspect.icon || '👤';
    
    const name = document.createElement('div');
    name.className = 'suspect-name';
    name.textContent = suspect.name || `Suspect ${suspect.id}`;
    
    const meterWrapper = document.createElement('div');
    meterWrapper.className = 'meter-wrapper';
    
    const meterFill = document.createElement('div');
    meterFill.className = 'meter-fill';
    meterFill.id = `meter-${suspect.id}`;
    meterFill.style.width = '0%';
    
    meterWrapper.appendChild(meterFill);
    card.appendChild(portrait);
    card.appendChild(name);
    card.appendChild(meterWrapper);
    
    const actionsOverlay = container.querySelector('.actions-overlay');
    container.insertBefore(card, actionsOverlay);
    
    suspectCards[suspect.id] = card;
    meterFills[suspect.id] = meterFill;
  });
  
  updateSuspectSelection();
}

function populateCaseFile(caseData) {
  const contentEl = document.getElementById('case-summary-content');
  if (!caseData || !caseData.title) {
    contentEl.innerHTML = '<p>No case data assigned.</p>';
    return;
  }
  
  let evidenceHtml = '<ul>';
  if (caseData.key_evidence && caseData.key_evidence.length > 0) {
    caseData.key_evidence.forEach(ev => evidenceHtml += `<li>${ev}</li>`);
  } else {
    evidenceHtml += '<li>No key evidence gathered yet.</li>';
  }
  evidenceHtml += '</ul>';

  const victimName = caseData.victim ? caseData.victim.name : 'Unknown';
  const victimAge = caseData.victim ? caseData.victim.age : 'Unknown';
  const victimRole = caseData.victim ? caseData.victim.role : 'Unknown';

  const sceneLoc = caseData.crime_scene ? caseData.crime_scene.location : 'Unknown';
  const sceneTime = caseData.crime_scene ? caseData.crime_scene.time_of_death : 'Unknown';
  const sceneWeapon = caseData.crime_scene ? caseData.crime_scene.weapon : 'Unknown';

  contentEl.innerHTML = `
    <div class="case-section">
      <h3>CASE TITLE</h3>
      <p><strong>${caseData.title.toUpperCase()}</strong></p>
      <p>${caseData.case_summary}</p>
    </div>
    <div class="case-section">
      <h3>VICTIM DOSSIER</h3>
      <ul>
        <li><strong>Name:</strong> ${victimName} (Age: ${victimAge})</li>
        <li><strong>Role:</strong> ${victimRole}</li>
      </ul>
    </div>
    <div class="case-section">
      <h3>CRIME SCENE</h3>
      <ul>
        <li><strong>Location:</strong> ${sceneLoc}</li>
        <li><strong>Time of Incident:</strong> ${sceneTime}</li>
        <li><strong>Suspected Weapon:</strong> ${sceneWeapon}</li>
      </ul>
    </div>
    <div class="case-section">
      <h3>KEY EVIDENCE</h3>
      ${evidenceHtml}
    </div>
  `;
}

window.selectSuspect = function(suspectId) {
  if (isTyping || isGameOver) return;
  activeSuspect = suspectId;
  updateSuspectSelection();
  appendSystemLine(`Audio feed tuned to Suspect ${suspectId}.`);
};

function updateSuspectSelection() {
  Object.entries(suspectCards).forEach(([key, card]) => {
    if (key === activeSuspect) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });
}

function renderMeters(scores) {
  if (!scores) return;
  let hasHighTension = false;
  
  Object.entries(scores).forEach(([suspectId, score]) => {
    const fill = meterFills[suspectId];
    if (fill) {
      fill.style.width = `${score}%`;
      // High tension threshold
      if (score > 75) {
        fill.classList.add('high-tension');
        hasHighTension = true;
      } else {
        fill.classList.remove('high-tension');
      }
    }
  });
  
  // Screen shake on contradiction detected! 
  if (hasHighTension) {
    document.querySelector('.ui-layer').classList.add('shake');
    setTimeout(() => {
      document.querySelector('.ui-layer').classList.remove('shake');
    }, 400);
  }
}

function parseActionCues(text) {
  if (!text) return '';
  return text; 
}

function appendSystemLine(text) {
  const line = document.createElement('div');
  line.className = 'terminal-line line-system';
  line.textContent = text;
  terminalOutput.appendChild(line);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function appendPlayerLine(text) {
  const line = document.createElement('div');
  line.className = 'terminal-line line-player';
  line.textContent = text;
  terminalOutput.appendChild(line);
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

async function typeWriterEffect(element, text, speed = 25) {
  isTyping = true;
  element.textContent = '';
  
  // Disable inputs while typing
  questionInput.disabled = true;
  document.querySelector('.btn.primary').disabled = true;
  
  // Adjust speed randomly for retro feel
  for (let i = 0; i < text.length; i++) {
    element.textContent += text.charAt(i);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
    
    // Quick random await for typing variance
    await new Promise(r => setTimeout(r, speed + Math.random() * 20));
  }
  
  questionInput.disabled = false;
  document.querySelector('.btn.primary').disabled = false;
  questionInput.focus();
  isTyping = false;
}

async function appendAILine(text) {
  const line = document.createElement('div');
  line.className = 'terminal-line line-ai';
  terminalOutput.appendChild(line);
  await typeWriterEffect(line, parseActionCues(text), 15);
}

async function interrogate(event) {
  if (event) event.preventDefault();
  if (isTyping || isGameOver) return;
  
  const question = questionInput.value.trim();
  if (!question) return;
  if (!gameId) { appendSystemLine('Initialize system before interrogation.'); return; }
  
  appendPlayerLine(question);
  questionInput.value = '';
  
  try {
    const response = await fetch(`${BACKEND_URL}/interrogate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect, question }),
    });
    const data = await response.json();
    
    if (response.ok) {
      await appendAILine(data.answer);
      
      if (data.tension_scores) {
        renderMeters(data.tension_scores);
      }
      if (data.time_remaining !== undefined) {
        document.getElementById('time-remaining-val').textContent = data.time_remaining;
      }
      if (data.message) {
        appendSystemLine(data.message);
      }
      if (data.game_over) {
        isGameOver = true;
        appendSystemLine('SYSTEM LOCKDOWN: INVESTIGATION OVER. USE RESTART BUTTON.');
      }
    } else {
      appendSystemLine(`ERROR: ${data.error || 'Input corrupted.'}`);
    }
  } catch (error) {
    appendSystemLine(`SYS_ERR: ${error.message}`);
  }
}

async function accuseSuspect() {
  if (isTyping || isGameOver) return;
  if (!gameId) { appendSystemLine('Initialize system first.'); return; }
  
  appendSystemLine(`WARRANT ISSUED: Accusing Suspect ${activeSuspect}...`);
  try {
    const response = await fetch(`${BACKEND_URL}/accuse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, suspect_id: activeSuspect }),
    });
    const data = await response.json();
    if (response.ok) {
      if (data.outcome_rank) {
        appendSystemLine(`===== FINAL VERDICT: ${data.outcome_rank.toUpperCase()} =====`);
      }
      await appendAILine(data.message);
      appendSystemLine(`Total Queries: ${data.questions_asked}`);
      if (data.correct) {
        appendSystemLine('CASE CLOSED: Suspect remanded to custody.');
      } else {
        appendSystemLine('CASE FAILED: Suspect cleared. Internal affairs investigation pending.');
      }
      isGameOver = true;
      appendSystemLine('Use the RESTART button to open a new case.');
    } else {
      appendSystemLine(`ERROR: ${data.error || 'Server rejected warrant.'}`);
    }
  } catch (error) {
    appendSystemLine(`SYS_ERR: ${error.message}`);
  }
}

// Event Listeners
questionForm.addEventListener('submit', interrogate);

const handleRestart = () => {
  if (isTyping) return;
  terminalOutput.innerHTML = '';
  startGame();
};
if (restartButton) restartButton.addEventListener('click', handleRestart);
if (restartButtonTop) restartButtonTop.addEventListener('click', handleRestart);

accuseButton.addEventListener('click', accuseSuspect);

// Modal Controls
if (caseFileBtn) {
  caseFileBtn.addEventListener('click', () => {
    caseModal.classList.remove('hidden');
  });
}
if (closeModalBtn) {
  closeModalBtn.addEventListener('click', () => {
    caseModal.classList.add('hidden');
  });
}

document.querySelectorAll('.quick-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (isTyping || isGameOver) return;
    questionInput.value = btn.dataset.question;
    interrogate();
  });
});

window.addEventListener('load', startGame);