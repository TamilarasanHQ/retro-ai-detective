import os
import random
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '').strip()
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
TIME_LIMIT_HOURS = 48

SUSPECT_PROFILES = {
    'A': {
        'name': 'Victoria Ashford',
        'alias': 'The Widow',
        'title': 'Widow',
        'age': 42,
        'relation': 'Widow of the victim',
        'motive': 'inheritance and family secrets',
        'personality': 'calculated',
        'bio': 'Victoria is poised, elegant, and keeps a careful distance from the scandal. She claims loyalty to the family legacy but her eyes never leave the ledger.',
        'alibi': 'I was in the study reviewing estate papers when the incident happened.',
        'real_location': 'Study',
        'icon': '🕊️',
        'base_alibi': 'Study - reviewing estate documents'
    },
    'B': {
        'name': 'Marcus Chen',
        'alias': 'Business Partner',
        'title': 'Partner',
        'age': 39,
        'relation': 'Victim’s business partner',
        'motive': 'financial disputes and betrayal',
        'personality': 'anxious',
        'bio': 'Marcus is restless and focused on the numbers. He says he was working late to protect the company, but the pressure of money makes him defensive.',
        'alibi': 'I was in my office handling a crisis call with an investor.',
        'real_location': 'Office',
        'icon': '💼',
        'base_alibi': 'Office - handling investor calls'
    },
    'C': {
        'name': 'Elena Reyes',
        'alias': 'Housekeeper',
        'title': 'Housekeeper',
        'age': 29,
        'relation': 'Housekeeper and occasional confidante',
        'motive': 'heard too much, wants freedom',
        'personality': 'observant',
        'bio': 'Elena knows the estate better than most. She seems nervous but precise, and she heard conversations no one else did.',
        'alibi': 'I was tidying the east wing and then took a break in the servant quarters.',
        'real_location': 'Servant Quarters',
        'icon': '🧹',
        'base_alibi': 'Servant quarters - taking a break'
    },
}

# ============================================
# CASE FILES DATABASE
# ============================================
# Structure: Each case is a dictionary with the following keys:
# - id: unique string identifier
# - title: case title
# - difficulty: 'Easy', 'Medium', 'Hard'
# - victim: dict with name, age, role, background
# - crime_scene: dict with location, time_of_death, weapon, description
# - suspects_involved: list of suspect IDs relevant to this case (default ['A','B','C'])
# - connections: dict mapping suspect_id to their relationship with victim
# - key_evidence: list of discovered clues at scene
# - case_summary: short text shown to player at start

CASE_FILES = [
    {
        'id': 'museum_murder',
        'title': 'The Midnight Museum Murder',
        'difficulty': 'Medium',
        'victim': {
            'name': 'Dr. Eleanor Voss',
            'age': 58,
            'role': 'Head Curator of Ancient Artifacts',
            'background': 'Renowned archaeologist with 30 years experience. Recently uncovered a major forgery ring operating within the museum.'
        },
        'crime_scene': {
            'location': 'Grand Exhibition Hall, Egyptian Wing - 3rd Floor',
            'time_of_death': 'Between 11:30 PM and 12:15 AM',
            'weapon': 'Antique Egyptian letter opener (taken from victim\'s desk)',
            'description': '''
                Dr. Voss was found lying near the newly acquired Amun-Re sarcophagus display.
                The display case was open but nothing appeared stolen.
                A single wound suggests a quick, deliberate attack.
                Security footage from the hall was erased between 11:45 PM and 12:05 AM.
                Footprints in restoration dust lead toward the server room.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Alex frequently assisted Dr. Voss with technical issues in the exhibition hall and knew the security system well.',
            'B': 'Brooke was helping Dr. Voss authenticate suspicious manuscripts found in the library archives.',
            'C': 'Casey delivered packages to Dr. Voss weekly, often after museum hours.'
        },
        'key_evidence': [
            'Security footage erased using a valid access code',
            'Footprints leading to the server bay',
            'A torn shipping label from a recent courier delivery',
            'The murder weapon came from the victim\'s own desk'
        ],
        'case_summary': '''
            Dr. Eleanor Voss was murdered last night in the museum's Egyptian Wing.
            Three people had after-hours access: the nightshift technician (Alex),
            a librarian cataloging late (Brooke), and a courier making a special delivery (Casey).
            All three claim innocence, but one is lying.
        '''
    },
    {
    'id': 'university_murder',
    'title': 'The Silent Lecture Hall',
    'difficulty': 'Medium',
    'victim': {
        'name': 'Prof. Daniel Wright',
        'age': 54,
        'role': 'Physics Professor',
        'background': 'Known for strict grading and recent plagiarism accusations.'
    },
    'crime_scene': {
        'location': 'Lecture Hall B',
        'time_of_death': 'Between 7:00 PM and 8:00 PM',
        'weapon': 'Blunt force (trophy)',
        'description': '''
            Found near the podium after evening lecture.
            Lights were turned off deliberately.
            A broken trophy was found nearby.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex was a failing student recently warned by the professor.',
        'B': 'Brooke was accused of plagiarism.',
        'C': 'Casey worked as lab assistant and had keys to the hall.'
    },
    'key_evidence': [
        'Broken trophy',
        'Lights manually switched off',
        'No forced entry',
        'Recent conflicts'
    ],
    'case_summary': 'Academic pressure turns deadly.'
},
{
    'id': 'restaurant_murder',
    'title': 'Dinner to Die For',
    'difficulty': 'Easy',
    'victim': {
        'name': 'Marco Bellini',
        'age': 47,
        'role': 'Restaurant Owner',
        'background': 'Had disputes with staff over unpaid wages.'
    },
    'crime_scene': {
        'location': 'Kitchen Area',
        'time_of_death': '10:30 PM',
        'weapon': 'Chef knife',
        'description': '''
            Found near prep table after closing.
            Kitchen door was unlocked.
            Signs of struggle present.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex was head chef recently arguing with victim.',
        'B': 'Brooke was a waiter fired last week.',
        'C': 'Casey was a delivery worker present late night.'
    },
    'key_evidence': [
        'Knife from kitchen',
        'Signs of struggle',
        'Witness argument',
        'Open back door'
    ],
    'case_summary': 'A heated workplace conflict escalates.'
},
{
    'id': 'library_murder',
    'title': 'Whispers in the Stacks',
    'difficulty': 'Medium',
    'victim': {
        'name': 'Helen Moore',
        'age': 63,
        'role': 'Chief Librarian',
        'background': 'Discovered rare manuscript theft.'
    },
    'crime_scene': {
        'location': 'Archive Section',
        'time_of_death': 'Between 6:00 PM and 7:00 PM',
        'weapon': 'Paper cutter blade',
        'description': '''
            Body found between shelves.
            Several rare books missing.
            Lights flickering due to maintenance.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex handled archive security.',
        'B': 'Brooke studied rare manuscripts.',
        'C': 'Casey was seen near restricted section.'
    },
    'key_evidence': [
        'Missing books',
        'Restricted access logs',
        'Maintenance blackout',
        'Sharp blade weapon'
    ],
    'case_summary': 'Knowledge comes at a deadly price.'
},
{
    'id': 'factory_murder',
    'title': 'The Night Shift Secret',
    'difficulty': 'Hard',
    'victim': {
        'name': 'Robert Kane',
        'age': 50,
        'role': 'Factory Supervisor',
        'background': 'Reported illegal activities inside factory.'
    },
    'crime_scene': {
        'location': 'Assembly Line 3',
        'time_of_death': 'Between 2:00 AM and 3:00 AM',
        'weapon': 'Industrial wrench',
        'description': '''
            Found near machinery.
            CCTV malfunctioned during incident.
            Oil spill nearby.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex worked night shift regularly.',
        'B': 'Brooke handled machine maintenance.',
        'C': 'Casey transported materials.'
    },
    'key_evidence': [
        'CCTV failure',
        'Oil spill',
        'Heavy tool weapon',
        'Illegal activity report'
    ],
    'case_summary': 'A whistleblower silenced.'
},
{
    'id': 'beach_murder',
    'title': 'Shadows by the Shore',
    'difficulty': 'Easy',
    'victim': {
        'name': 'Olivia Hart',
        'age': 29,
        'role': 'Travel Blogger',
        'background': 'Recently exposed a smuggling network.'
    },
    'crime_scene': {
        'location': 'Private Beach Area',
        'time_of_death': '11:45 PM',
        'weapon': 'Blunt object',
        'description': '''
            Found near rocks by shoreline.
            Phone missing.
            Footprints washed partially.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex was last seen talking to victim.',
        'B': 'Brooke runs local tour services.',
        'C': 'Casey operates boat transport.'
    },
    'key_evidence': [
        'Missing phone',
        'Partial footprints',
        'Late night meeting',
        'Smuggling exposure'
    ],
    'case_summary': 'A dangerous secret beneath the waves.'
},
{
    'id': 'office_murder',
    'title': 'Deadline Killer',
    'difficulty': 'Medium',
    'victim': {
        'name': 'Kevin Brooks',
        'age': 41,
        'role': 'Project Manager',
        'background': 'Was about to fire multiple employees.'
    },
    'crime_scene': {
        'location': 'Corporate Office - Floor 12',
        'time_of_death': 'Between 8:00 PM and 9:00 PM',
        'weapon': 'Paperweight',
        'description': '''
            Found at desk after hours.
            Computer still on.
            Email draft about layoffs open.
        '''
    },
    'suspects_involved': ['A', 'B', 'C'],
    'connections': {
        'A': 'Alex was facing termination.',
        'B': 'Brooke had conflicts with victim.',
        'C': 'Casey worked IT support.'
    },
    'key_evidence': [
        'Layoff email draft',
        'Blunt weapon',
        'Access logs',
        'No forced entry'
    ],
    'case_summary': 'Corporate tension reaches a breaking point.'
},
    # You can add more cases here following the same structure
    # {
    #     'id': 'library_silence',
    #     'title': 'Silence in the Stacks',
    #     ...
    # },
]

# Add this after the SUSPECT_PROFILES definition
conversation_memory = {}  # Global memory for conversation history

def store_answer(game_id, suspect_id, question, answer, mode):
    """Store conversation history for a specific game and suspect"""
    if game_id not in conversation_memory:
        conversation_memory[game_id] = {}
    if suspect_id not in conversation_memory[game_id]:
        conversation_memory[game_id][suspect_id] = []
    
    conversation_memory[game_id][suspect_id].append({
        "question": question,
        "answer": answer,
        "mode": mode
    })
    
    # Keep only last 5 interactions
    if len(conversation_memory[game_id][suspect_id]) > 5:
        conversation_memory[game_id][suspect_id].pop(0)

def get_emotion(game_id, suspect_id, suspect):
    """Determine suspect's current emotional state"""
    if game_id not in conversation_memory:
        return suspect['personality']
    
    history = conversation_memory[game_id].get(suspect_id, [])
    
    # Killer gets more nervous as they're questioned more
    if suspect['role'] == 'killer' and len(history) > 3:
        return 'increasingly nervous'
    elif suspect['role'] == 'killer' and len(history) > 2:
        return 'defensive'
    elif suspect['role'] == 'killer':
        return 'trying to stay calm'
    
    # Innocent suspects remain consistent
    return suspect['personality']



def generate_logical_answer(suspect, question):
    """Generate a logical answer based on truth/lie detection"""
    question_lower = question.lower()
    
    # Location questions
    if any(word in question_lower for word in ['where', 'location', 'place', 'area']):
        if suspect['role'] == 'killer':
            # Killer lies 80% of time, slips 20%
            if random.random() < 0.8:
                base_answer = suspect['alibi']
                mode = 'lying'
            else:
                # Small slip - might mention real location
                base_answer = f"I was... well, mostly in the {suspect['real_location']}. I mean, {suspect['alibi'].lower()}"
                mode = 'slip'
        else:
            base_answer = f"I was in the {suspect['real_location']}, {suspect['alibi'].lower()}"
            mode = 'truth'
    
    # Time questions
    elif any(word in question_lower for word in ['when', 'time', 'clock', 'hour']):
        if suspect['role'] == 'killer':
            base_answer = suspect['alibi']
            mode = 'lying'
        else:
            base_answer = suspect['alibi']
            mode = 'truth'
    
    # Alibi questions
    elif any(word in question_lower for word in ['alibi', 'prove', 'witness', 'see']):
        if suspect['role'] == 'killer':
            if random.random() < 0.7:
                base_answer = "I was alone. No one can confirm where I was."
                mode = 'defensive'
            else:
                base_answer = "Look, I already told you where I was. Why don't you ask someone else?"
                mode = 'deflecting'
        else:
            base_answer = f"I was where I said I was. You can check with others if you want."
            mode = 'truth'
    
    # Suspicion/accusation questions
    elif any(word in question_lower for word in ['suspect', 'think', 'who', 'killer', 'guilty']):
        if suspect['role'] == 'killer':
            if random.random() < 0.6:
                base_answer = "I don't know who did it. Maybe look at the others."
                mode = 'deflecting'
            else:
                base_answer = "Why are you asking me? I've been nothing but cooperative."
                mode = 'defensive'
        else:
            base_answer = "I don't know who the killer is, but I'm sure the evidence will point to them."
            mode = 'truth'
    
    # Why questions (motive)
    elif any(word in question_lower for word in ['why', 'motive', 'reason']):
        if suspect['role'] == 'killer':
            base_answer = "I had no reason to hurt anyone. This is ridiculous."
            mode = 'lying'
        else:
            base_answer = "I barely knew the victim. I have no reason to be involved."
            mode = 'truth'
    
    # Default response
    else:
        if suspect['role'] == 'killer':
            base_answer = suspect['alibi']
            mode = 'lying'
        else:
            base_answer = suspect['alibi']
            mode = 'truth'
    
    return base_answer, mode

def format_history(history):
    """Format conversation history for the prompt"""
    if not history:
        return "No previous questions asked yet."
    
    formatted = []
    for i, entry in enumerate(history, 1):
        formatted.append(f"Q{i}: {entry['question']}")
        formatted.append(f"A{i}: {entry['answer']}")
    
    return "\n".join(formatted)

ACCUSATION_KEYWORDS = [
    'murder',
    'did it',
    'kill',
    'guilty',
    'accuse',
    'responsible',
    'blood on your hands',
]
CONTRADICTION_KEYWORDS = [
    "i didn't",
    'i never',
    'not me',
    'actually',
    "that wasn't",
    'contradict',
    'lied',
    'liar',
    'no one',
    'different',
    'except',
    'however',
    'but',
    'false',
    'wrong',
    'maybe',
    'not sure',
]
AGGRESSIVE_KEYWORDS = [
    'shut up',
    'listen to me',
    'prove it',
    'lie',
    'bullshit',
    'you think',
]
CALMING_KEYWORDS = [
    'i understand',
    'sorry',
    'that must be hard',
    'take it easy',
    'relax',
    'calm down',
    'please',
]

def get_mood(score):
    if score >= 100:
        return 'refusing', '🚫'
    if score >= 81:
        return 'angry', '😠'
    if score >= 61:
        return 'nervous', '😰'
    if score >= 40:
        return 'defensive', '😤'
    return 'relaxed', '😌'


def evaluate_question_effect(game, suspect_id, question):
    question_lower = question.lower()
    delta = 0
    reasons = []

    if any(keyword in question_lower for keyword in ACCUSATION_KEYWORDS):
        delta += 25
        reasons.append('direct accusation')

    if any(keyword in question_lower for keyword in CONTRADICTION_KEYWORDS):
        delta += 15
        reasons.append('contradiction')

    if any(keyword in question_lower for keyword in AGGRESSIVE_KEYWORDS):
        delta += 10
        reasons.append('aggressive tone')

    if any(keyword in question_lower for keyword in CALMING_KEYWORDS):
        delta -= 5
        reasons.append('calming approach')

    history = game['question_history'].get(suspect_id, [])
    if question_lower in history:
        delta += 5
        reasons.append('repeated question')

    history.append(question_lower)
    game['question_history'][suspect_id] = history

    delta += random.randint(-2, 2)
    return delta, reasons


games = {}


def make_game():
    game_id = str(uuid.uuid4())
    killer_id = random.choice(list(SUSPECT_PROFILES.keys()))
    suspects = {}
    for suspect_id, profile in SUSPECT_PROFILES.items():
        mood, mood_icon = get_mood(20)
        suspects[suspect_id] = {
            'id': suspect_id,
            'name': profile['name'],
            'alias': profile['alias'],
            'title': profile['title'],
            'age': profile['age'],
            'relation': profile['relation'],
            'motive': profile['motive'],
            'bio': profile['bio'],
            'icon': profile['icon'],
            'role': 'killer' if suspect_id == killer_id else 'innocent',
            'history': [],
            'score': 20,
            'mood': mood,
            'mood_icon': mood_icon,
            'alibi': profile['alibi'],
            'real_location': profile['real_location'],
            'personality': profile['personality'],
            'base_alibi': profile['base_alibi']
        }
    
    selected_case = random.choice(CASE_FILES).copy()
    if killer_id not in selected_case['suspects_involved']:
        selected_case['suspects_involved'].append(killer_id)
    
    game = {
        'game_id': game_id,
        'killer_id': killer_id,
        'suspects': suspects,
        'question_count': 0,
        'questions_asked': 0,
        'time_remaining': TIME_LIMIT_HOURS,
        'question_history': {sid: [] for sid in SUSPECT_PROFILES.keys()},
        'created': True,
        'case': selected_case
    }
    games[game_id] = game
    return game


def format_prompt(suspect, question, game_id, base_answer, mode, emotion):
    """Create enhanced prompt with logical answer base and memory"""
    profile = SUSPECT_PROFILES[suspect['id']]
    
    history = []
    if game_id in conversation_memory and suspect['id'] in conversation_memory[game_id]:
        history = conversation_memory[game_id][suspect['id']][-3:]
    
    mood_text = {
        'refusing': 'refusing to cooperate',
        'angry': 'angry and hostile',
        'nervous': 'nervous and easily rattled',
        'defensive': 'defensive and guarded',
        'relaxed': 'relaxed and talkative',
    }.get(emotion, emotion)

    system_content = f"""You are {profile['name']} ({profile['alias']}), a suspect in a murder investigation.

Personality: {profile['personality']}
Current emotional state: {mood_text}
Your role: {suspect['role']} (keep this secret)
Truth/Lie mode: {mode}

CRITICAL RULES:
- Do NOT repeat the exact same sentence structure
- Speak naturally like a real human
- Vary your phrasing each time you're asked similar questions
- Keep answers concise if tension is high, more descriptive if relaxed
- Stay in character as {profile['name']}, the {profile['title']}
- Your core response should be based on: "{base_answer}"
- Add natural human variations, hesitations, or filler words
- Never break character or acknowledge you're an AI

Previous responses (DO NOT repeat these exactly):
{format_history(history)}

Convert the following core response into natural, varied human speech:
"{base_answer}"
"""
    
    return [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': question}
    ]


def call_openrouter(messages):
    if not OPENROUTER_API_KEY:
        return 'OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.'
    
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
        'temperature': 0.75,
        'max_tokens': 220,
    }
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'choices' in data and data['choices']:
            return data['choices'][0].get('message', {}).get('content', '').strip()
        return 'The AI failed to produce an answer.'
    except Exception as exc:
        return f'Error: {str(exc)}'



def count_keywords(answer, keywords):
    lower = answer.lower()
    return sum(1 for keyword in keywords if keyword in lower)


def update_tension(game, suspect_id, question):
    """Update tension scores based on question content and investigation pace"""
    suspect = game['suspects'][suspect_id]
    tension_delta, reasons = evaluate_question_effect(game, suspect_id, question)
    suspect['score'] = max(0, min(100, suspect['score'] + tension_delta))
    mood, mood_icon = get_mood(suspect['score'])
    suspect['mood'] = mood
    suspect['mood_icon'] = mood_icon

    hours_spent = random.randint(1, 2)
    game['time_remaining'] = max(0, game['time_remaining'] - hours_spent)
    game['question_count'] += 1
    game['questions_asked'] += 1

    return tension_delta, reasons, hours_spent, mood


def get_tension_summary(game):
    return {sid: suspect['score'] for sid, suspect in game['suspects'].items()}


def get_suspect_summary(game):
    return [
        {
            'id': suspect['id'],
            'name': suspect['name'],
            'alias': suspect.get('alias'),
            'title': suspect['title'],
            'bio': suspect['bio'],
            'icon': suspect['icon'],
            'score': suspect['score'],
            'mood': suspect.get('mood'),
            'mood_icon': suspect.get('mood_icon'),
        }
        for suspect in game['suspects'].values()
    ]


@app.route('/start', methods=['GET', 'POST'])
def start():
    game = make_game()
    case_data = game.get('case', {})
    safe_case = {
        'id': case_data.get('id'),
        'title': case_data.get('title'),
        'difficulty': case_data.get('difficulty'),
        'victim': case_data.get('victim'),
        'crime_scene': case_data.get('crime_scene'),
        'key_evidence': case_data.get('key_evidence'),
        'case_summary': case_data.get('case_summary'),
        'connections': case_data.get('connections', {}),
    }
    return jsonify(
        {
            'game_id': game['game_id'],
            'suspects': get_suspect_summary(game),
            'tension_scores': get_tension_summary(game),
            'time_remaining': game['time_remaining'],
            'case': safe_case,
            'message': 'New investigation started. Interrogate a suspect to reveal clues.',
        }
    )


@app.route('/interrogate', methods=['POST'])
def interrogate():
    payload = request.get_json() or {}
    game_id = payload.get('game_id')
    suspect_id = payload.get('suspect_id')
    question = payload.get('question', '').strip()
    
    if not game_id or not suspect_id or not question:
        return jsonify({'error': 'game_id, suspect_id, and question are required.'}), 400
    
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found. Call /start to begin a new game.'}), 404
    
    suspect = game['suspects'].get(suspect_id)
    if not suspect:
        return jsonify({'error': 'Invalid suspect selected.'}), 400

    if game['time_remaining'] <= 0:
        return jsonify({'error': 'Time has run out. The investigation is over.'}), 400
    
    base_answer, mode = generate_logical_answer(suspect, question)
    emotion = get_emotion(game_id, suspect_id, suspect)
    prompt = format_prompt(suspect, question, game_id, base_answer, mode, emotion)
    answer = call_openrouter(prompt)
    store_answer(game_id, suspect_id, question, answer, mode)

    tension_change, reasons, hours_spent, mood = update_tension(game, suspect_id, question)
    
    entry = {
        'question': question,
        'answer': answer,
        'mode': mode,
        'tension_change': tension_change,
        'reason': reasons,
        'hours_spent': hours_spent,
    }
    suspect['history'].append(entry)

    if game['time_remaining'] <= 0:
        return jsonify({
            'game_id': game_id,
            'suspect_id': suspect_id,
            'answer': answer,
            'mode': mode,
            'history': suspect['history'],
            'tension_scores': get_tension_summary(game),
            'time_remaining': game['time_remaining'],
            'message': 'The clock has run out. The investigation has ended.',
            'game_over': True,
        })

    return jsonify({
        'game_id': game_id,
        'suspect_id': suspect_id,
        'answer': answer,
        'mode': mode,
        'history': suspect['history'],
        'suspect': {
            'id': suspect_id,
            'score': suspect['score'],
            'mood': suspect['mood'],
            'mood_icon': suspect['mood_icon'],
        },
        'tension_scores': get_tension_summary(game),
        'time_remaining': game['time_remaining'],
        'reason': reasons,
        'message': f'Suspect answered. Tension changed by {tension_change:+d}, time -{hours_spent}h.',
    })

@app.route('/accuse', methods=['POST'])
def accuse():
    payload = request.get_json() or {}
    game_id = payload.get('game_id')
    suspect_id = payload.get('suspect_id')
    if not game_id or not suspect_id:
        return jsonify({'error': 'game_id and suspect_id are required.'}), 400
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found. Call /start to begin.'}), 404
    if suspect_id not in game['suspects']:
        return jsonify({'error': 'Invalid suspect selected.'}), 400
    correct = suspect_id == game['killer_id']
    message = (
        'Correct! Your detective instincts were right. The killer has been unmasked.'
        if correct
        else 'Wrong suspect. The killer is still at large. Try another interrogation.'
    )
    return jsonify(
        {
            'game_id': game_id,
            'accused': suspect_id,
            'correct': correct,
            'killer_id': game['killer_id'] if correct else None,
            'message': message,
        }
    )


@app.route('/status', methods=['GET'])
def status():
    game_id = request.args.get('game_id')
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found.'}), 404
    return jsonify(
        {
            'game_id': game_id,
            'suspects': get_suspect_summary(game),
            'tension_scores': get_tension_summary(game),
            'time_remaining': game['time_remaining'],
        }
    )

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/case/<game_id>', methods=['GET'])
def get_case_details(game_id):
    """Return the case file for the current game"""
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found.'}), 404
    
    case_data = game.get('case', {})
    # Remove any internal fields we don't want to expose
    safe_case = {
        'id': case_data.get('id'),
        'title': case_data.get('title'),
        'difficulty': case_data.get('difficulty'),
        'victim': case_data.get('victim'),
        'crime_scene': case_data.get('crime_scene'),
        'key_evidence': case_data.get('key_evidence'),
        'case_summary': case_data.get('case_summary'),
        'connections': case_data.get('connections', {})
        # Connections are shown in suspect bios, not here
    }
    return jsonify({'case': safe_case})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
