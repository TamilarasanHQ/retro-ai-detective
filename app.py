import os
import random
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '').strip()
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
TIME_LIMIT_HOURS = 48
ANTI_GRAVITY_MODE = True

SUSPECT_PROFILES = {
    'A': {
        'name': 'Victoria Ashford',
        'alias': 'The Widow',
        'title': 'Widow',
        'age': 42,
        'relation': 'Widow of the victim',
        'motive': 'inheritance and family secrets',
        'personality': 'Calm: logical, precise, composed, keeps a careful distance, controlled tone, denies emotional involvement.',
        'archetype': 'Calm',
        'truthfulness_baseline': 80,
        'hidden_secrets': 'She knew about her husband changing his will two days ago.',
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
        'personality': 'Nervous: unstable, anxious, talks fast, sweats the details, over-explains, highly defensive under pressure, stutters.',
        'archetype': 'Nervous',
        'truthfulness_baseline': 60,
        'hidden_secrets': 'He was embezzling company funds and the victim found out.',
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
        'personality': 'Manipulative: observant, redirects questions, answers questions with questions, tries to cast doubt on others, selectively truthful.',
        'archetype': 'Manipulative',
        'truthfulness_baseline': 40,
        'hidden_secrets': 'She was secretly gathering blackmail material on the victim to pay off her brother\'s debts.',
        'bio': 'Elena knows the estate better than most. She seems nervous but precise, and she heard conversations no one else did.',
        'alibi': 'I was tidying the east wing and then took a break in the servant quarters.',
        'real_location': 'Servant Quarters',
        'icon': '🧹',
        'base_alibi': 'Servant quarters - taking a break'
    },
    'D': {
        'name': 'Dr. Samuel Reed',
        'alias': 'The Doctor',
        'title': 'Family Physician',
        'age': 56,
        'relation': 'Victim\'s personal doctor',
        'motive': 'medical malpractice cover-up',
        'personality': 'Evasive: speaks in medical jargon, deflects with professional authority, vague about specifics, often says "I can\'t discuss patient confidentiality."',
        'archetype': 'Evasive',
        'truthfulness_baseline': 50,
        'hidden_secrets': 'He prescribed the victim a dangerous combination of medications that could have caused erratic behavior.',
        'bio': 'Dr. Reed has been the family doctor for decades. He seems concerned but is careful with his words, hiding behind his Hippocratic oath.',
        'alibi': 'I was at the clinic catching up on patient files. I left around 9 PM.',
        'real_location': 'Medical Clinic',
        'icon': '🩺',
        'base_alibi': 'Clinic - reviewing patient files'
    },
    'E': {
        'name': 'Lena Petrova',
        'alias': 'The Journalist',
        'title': 'Investigative Reporter',
        'age': 34,
        'relation': 'Was writing an exposé on the victim',
        'motive': 'career-making story, source protection',
        'personality': 'Inquisitive: asks more questions than she answers, notes everything, seems to know more than she lets on, protective of her sources.',
        'archetype': 'Inquisitive',
        'truthfulness_baseline': 70,
        'hidden_secrets': 'She received an anonymous tip about the victim\'s illegal activities the night before the murder.',
        'bio': 'Lena is sharp and observant. She was seen near the crime scene but claims it was for her investigation. Her notebook is filled with cryptic shorthand.',
        'alibi': 'I was in my car outside the building, waiting for a source who never showed.',
        'real_location': 'Car outside building',
        'icon': '📸',
        'base_alibi': 'Car - waiting for anonymous source'
    },
    'F': {
        'name': 'Tomás Herrera',
        'alias': 'The Gardener',
        'title': 'Groundskeeper',
        'age': 47,
        'relation': 'Long-time estate employee',
        'motive': 'loyalty to the family, possible blackmail',
        'personality': 'Loyal but nervous: speaks highly of the family, avoids direct eye contact, fidgets with his cap, offers too much unsolicited praise.',
        'archetype': 'Nervous',
        'truthfulness_baseline': 65,
        'hidden_secrets': 'He saw the victim arguing with someone near the greenhouse an hour before the murder.',
        'bio': 'Tomás has worked the grounds for 20 years. He knows every corner of the estate and is fiercely protective of the family\'s reputation.',
        'alibi': 'I was in the greenhouse preparing seedlings for the spring planting.',
        'real_location': 'Greenhouse',
        'icon': '🌿',
        'base_alibi': 'Greenhouse - preparing seedlings'
    },
    'G': {
        'name': 'Priya Sharma',
        'alias': 'The Accountant',
        'title': 'Financial Advisor',
        'age': 41,
        'relation': 'Managed victim\'s investments',
        'motive': 'embezzlement discovery',
        'personality': 'Calculating: speaks precisely, answers only what is asked, watches her words carefully, never volunteers extra information.',
        'archetype': 'Calculating',
        'truthfulness_baseline': 75,
        'hidden_secrets': 'She discovered a large, unexplained transfer from the victim\'s account to an offshore entity two days ago.',
        'bio': 'Priya is meticulous and keeps perfect records. She seems helpful but guards information like currency.',
        'alibi': 'I was working late at my office downtown. I have security badge logs to prove it.',
        'real_location': 'Downtown Office',
        'icon': '📊',
        'base_alibi': 'Office - working late on accounts'
    },
    'H': {
        'name': 'Dimitri Volkov',
        'alias': 'The Ex-Con',
        'title': 'Former Employee',
        'age': 38,
        'relation': 'Recently fired by victim',
        'motive': 'revenge, anger issues',
        'personality': 'Volatile: quick to anger, easily frustrated by repeated questions, uses intimidation, but occasionally shows vulnerability.',
        'archetype': 'Volatile',
        'truthfulness_baseline': 45,
        'hidden_secrets': 'He was seen arguing with the victim about unpaid wages the day of the murder.',
        'bio': 'Dimitri has a short temper and a record. He was fired last week and hasn\'t taken it well. He was seen near the estate that night.',
        'alibi': 'I was at a bar down the street. The bartender knows me.',
        'real_location': 'Neighborhood Bar',
        'icon': '🥃',
        'base_alibi': 'Bar - drinking alone'
    },
    'I': {
        'name': 'Yuki Tanaka',
        'alias': 'The Artist',
        'title': 'Commissioned Painter',
        'age': 31,
        'relation': 'Painting victim\'s portrait',
        'motive': 'artistic obsession, secret affair',
        'personality': 'Eccentric: speaks in metaphors, easily distracted by details, emotional, sometimes contradicts herself without realizing.',
        'archetype': 'Eccentric',
        'truthfulness_baseline': 55,
        'hidden_secrets': 'She was having an affair with the victim and painted hidden messages in the portrait.',
        'bio': 'Yuki sees the world in colors and emotions. She spent hours alone with the victim, capturing their likeness. Her studio is filled with half-finished canvases.',
        'alibi': 'I was in my studio at the east end of the property, working on the underpainting.',
        'real_location': 'Art Studio',
        'icon': '🎨',
        'base_alibi': 'Studio - working on portrait'
    },
    'J': {
        'name': 'Robert Sterling III',
        'alias': 'The Rival',
        'title': 'Business Competitor',
        'age': 49,
        'relation': 'Arch-rival in industry',
        'motive': 'corporate sabotage, personal grudge',
        'personality': 'Arrogant: condescending, acts above suspicion, uses status to deflect, subtly insults the investigation process.',
        'archetype': 'Arrogant',
        'truthfulness_baseline': 60,
        'hidden_secrets': 'He was secretly negotiating a buyout that the victim was blocking.',
        'bio': 'Sterling sees this as an inconvenience. He believes his wealth and connections make him untouchable. He was in town for "business."',
        'alibi': 'I was dining with clients at an exclusive club across town. The staff will vouch for me.',
        'real_location': 'Exclusive Club',
        'icon': '🎩',
        'base_alibi': 'Private club - business dinner'
    },
    'K': {
        'name': 'Sophie Martin',
        'alias': 'The Ex-Wife',
        'title': 'First Wife',
        'age': 45,
        'relation': 'Divorced from victim',
        'motive': 'alimony dispute, jealousy',
        'personality': 'Bitter: sarcastic, quick to point out victim\'s flaws, plays the victim card, emotional swings between anger and sadness.',
        'archetype': 'Bitter',
        'truthfulness_baseline': 70,
        'hidden_secrets': 'She still had a key to the estate and was seen near the property that evening.',
        'bio': 'Sophie feels she was wronged by the divorce settlement. She came by to "pick up some things" but may have had ulterior motives.',
        'alibi': 'I was at my apartment, alone, watching old movies and drinking wine.',
        'real_location': 'Her Apartment',
        'icon': '🥀',
        'base_alibi': 'Apartment - alone'
    },
    'L': {
        'name': 'Omar Hassan',
        'alias': 'The Security Guard',
        'title': 'Night Watchman',
        'age': 52,
        'relation': 'On duty the night of murder',
        'motive': 'negligence, possible inside job',
        'personality': 'Anxious: eager to please, over-explains his rounds, nervous about losing his job, sweats under questioning.',
        'archetype': 'Nervous',
        'truthfulness_baseline': 50,
        'hidden_secrets': 'He was asleep in the security booth for about an hour during his shift.',
        'bio': 'Omar has worked security for 15 years without incident. He seems more worried about his pension than the murder.',
        'alibi': 'I was making my rounds. I checked the east gate at 10 PM, then the main hall at 10:30.',
        'real_location': 'Security Booth/Grounds',
        'icon': '🔦',
        'base_alibi': 'Security rounds - patrolling estate'
    },
    'M': {
        'name': 'Maeve O\'Connell',
        'alias': 'The Bartender',
        'title': 'Local Pub Owner',
        'age': 36,
        'relation': 'Victim\'s favorite watering hole',
        'motive': 'unpaid debts, overheard secrets',
        'personality': 'Gossipy: friendly but sharp, knows everyone\'s business, remembers who drank what and when, deflects with charm.',
        'archetype': 'Inquisitive',
        'truthfulness_baseline': 75,
        'hidden_secrets': 'The victim confided in her about a threatening letter two nights before.',
        'bio': 'Maeve runs the corner pub. She sees everything and forgets nothing. Her alibi is shaky but her memory is sharp.',
        'alibi': 'I was closing up the pub. I left around midnight and went straight home.',
        'real_location': 'The Rusty Anchor Pub',
        'icon': '🍺',
        'base_alibi': 'Pub - closing shift'
    },
    'N': {
        'name': 'Father Dominic',
        'alias': 'The Priest',
        'title': 'Parish Priest',
        'age': 61,
        'relation': 'Victim\'s spiritual advisor',
        'motive': 'protecting confession seal, moral outrage',
        'personality': 'Pious but troubled: speaks gently, chooses words carefully, seems burdened, refuses to break confidentiality.',
        'archetype': 'Evasive',
        'truthfulness_baseline': 85,
        'hidden_secrets': 'The victim confessed something deeply troubling the afternoon of the murder.',
        'bio': 'Father Dominic has served the parish for 30 years. He knows more than he can say, and his conscience is heavy.',
        'alibi': 'I was in the rectory preparing my sermon for Sunday.',
        'real_location': 'Church Rectory',
        'icon': '⛪',
        'base_alibi': 'Rectory - preparing sermon'
    },
    'O': {
        'name': 'Jasmine Lee',
        'alias': 'The Intern',
        'title': 'Junior Assistant',
        'age': 23,
        'relation': 'Worked directly under victim',
        'motive': 'overworked, undervalued, possible harassment',
        'personality': 'Timid: speaks softly, avoids eye contact, flinches at loud voices, eager to please but easily overwhelmed.',
        'archetype': 'Nervous',
        'truthfulness_baseline': 70,
        'hidden_secrets': 'She witnessed a heated argument between the victim and another suspect just hours before.',
        'bio': 'Jasmine is new to the city and the job. She idolized the victim but also feared them. She\'s terrified of being blamed.',
        'alibi': 'I was working late at my desk in the office annex. I was the last to leave.',
        'real_location': 'Office Annex',
        'icon': '📎',
        'base_alibi': 'Office annex - working late'
    },
    'P': {
        'name': 'Viktor Kozlov',
        'alias': 'The Neighbor',
        'title': 'Retired Military',
        'age': 68,
        'relation': 'Lived next door',
        'motive': 'noise complaints, property disputes',
        'personality': 'Suspicious: watches everything, keeps meticulous notes, distrusts authorities, answers in short, clipped sentences.',
        'archetype': 'Calculating',
        'truthfulness_baseline': 90,
        'hidden_secrets': 'He has surveillance cameras that captured something unusual that night.',
        'bio': 'Viktor is a creature of habit. He knows every car that parks on the street, every visitor, every unusual sound.',
        'alibi': 'I was at home, watching my security monitors as I always do.',
        'real_location': 'His Home',
        'icon': '📷',
        'base_alibi': 'Home - monitoring security feeds'
    },
    'Q': {
        'name': 'Delilah Rose',
        'alias': 'The Mistress',
        'title': 'Secret Lover',
        'age': 29,
        'relation': 'Victim\'s extramarital partner',
        'motive': 'jealousy, fear of exposure',
        'personality': 'Emotional: cries easily, then turns cold, oscillates between love and hate for the victim, desperate to protect her secret.',
        'archetype': 'Manipulative',
        'truthfulness_baseline': 35,
        'hidden_secrets': 'She was pregnant with the victim\'s child and threatened to tell his wife.',
        'bio': 'Delilah lived in the shadows of the victim\'s life. She loved him, resented him, and now fears her world will collapse.',
        'alibi': 'I was at home, alone, waiting for a call that never came.',
        'real_location': 'Her Apartment',
        'icon': '💋',
        'base_alibi': 'Apartment - waiting by the phone'
    },
    'R': {
        'name': 'Harold Finch',
        'alias': 'The Butler',
        'title': 'Head of Household Staff',
        'age': 59,
        'relation': 'Loyal servant for 35 years',
        'motive': 'protecting family reputation at all costs',
        'personality': 'Impeccable: formal, precise, never a hair out of place, answers with "Sir" or "Madam", reveals nothing.',
        'archetype': 'Calm',
        'truthfulness_baseline': 95,
        'hidden_secrets': 'He cleaned up something incriminating before the police arrived.',
        'bio': 'Harold has served the family longer than anyone. His loyalty is absolute. He would do anything to protect the household\'s name.',
        'alibi': 'I was attending to my evening duties: locking up the silver, turning down beds, ensuring all was in order.',
        'real_location': 'Main House',
        'icon': '🎩',
        'base_alibi': 'Estate - evening duties'
    },
    'S': {
        'name': 'Nina Kowalski',
        'alias': 'The Hacker',
        'title': 'IT Security Consultant',
        'age': 28,
        'relation': 'Freelancer hired by victim',
        'motive': 'discovered dirty data, blackmail opportunity',
        'personality': 'Sarcastic: tech-savvy, impatient with non-tech people, uses jargon as a shield, acts superior but is deeply paranoid.',
        'archetype': 'Calculating',
        'truthfulness_baseline': 55,
        'hidden_secrets': 'She found encrypted files on the victim\'s server detailing illegal transactions.',
        'bio': 'Nina was brought in to upgrade security. She found more than she bargained for. Now she holds all the keys.',
        'alibi': 'I was at my home office, logged into the network remotely. My logs will prove it.',
        'real_location': 'Home Office',
        'icon': '💻',
        'base_alibi': 'Home - remote work'
    },
    'T': {
        'name': 'Gabriel Santos',
        'alias': 'The Valet',
        'title': 'Personal Driver',
        'age': 33,
        'relation': 'Drove victim everywhere',
        'motive': 'overheard damaging conversation, cut from will',
        'personality': 'Observant but quiet: speaks only when spoken to, notices details about cars and routes, loyal to whoever pays him.',
        'archetype': 'Evasive',
        'truthfulness_baseline': 60,
        'hidden_secrets': 'He drove the victim to a secret meeting the night of the murder and knows who they met.',
        'bio': 'Gabriel spent more time with the victim than anyone. He knows schedules, routes, and secrets hidden in the backseat.',
        'alibi': 'I was washing and detailing the car in the garage after dropping the victim off.',
        'real_location': 'Garage',
        'icon': '🚗',
        'base_alibi': 'Garage - detailing vehicle'
    }
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
},    {
        'id': 'mansion_murder',
        'title': 'Murder at Blackwood Manor',
        'difficulty': 'Hard',
        'victim': {
            'name': 'Lord Reginald Blackwood',
            'age': 71,
            'role': 'Eccentric Millionaire',
            'background': 'Made his fortune in railroads, recently changed his will, and had strained relationships with all his heirs.'
        },
        'crime_scene': {
            'location': 'Blackwood Manor - Library',
            'time_of_death': 'Between 9:00 PM and 11:00 PM',
            'weapon': 'Heavy crystal decanter (smashed)',
            'description': '''
                The body was found slumped over his antique mahogany desk.
                A shattered crystal decanter lay nearby, with brandy soaking into the Persian rug.
                The room was locked from the inside, but a hidden servant's passage was found ajar.
                A torn piece of fabric was caught on the passage door handle.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the victim\'s niece and stood to inherit the manor, but they had a public argument about selling the family estate.',
            'B': 'Marcus Chen was the victim\'s financial advisor and knew about a recent bad investment that would have ruined the family.',
            'C': 'Elena Reyes was a maid who recently discovered a hidden safe in the library and was caught snooping by the victim.'
        },
        'key_evidence': [
            'Locked room with hidden passage ajar',
            'Torn fabric on door handle',
            'Shattered crystal decanter (murder weapon)',
            'Burn marks in fireplace (documents destroyed)'
        ],
        'case_summary': '''
            Lord Blackwood was found dead in his locked library. Only three people were in the manor at the time:
            his niece Victoria, his advisor Marcus, and the maid Elena. Each has a motive, and the hidden passage
            suggests someone knew the house's secrets well.
        '''
    },
    {
        'id': 'theater_murder',
        'title': 'Final Curtain Call',
        'difficulty': 'Medium',
        'victim': {
            'name': 'Adrian Sterling',
            'age': 38,
            'role': 'Lead Actor / Theater Owner',
            'background': 'Charismatic but ruthless, he recently fired the understudy and was rumored to be selling the historic theater to developers.'
        },
        'crime_scene': {
            'location': 'Grand Regal Theater - Backstage Dressing Room',
            'time_of_death': 'Approximately 10:15 PM (during intermission)',
            'weapon': 'Sandbag counterweight (fell from fly system)',
            'description': '''
                The victim was found on the floor of his dressing room, struck by a sandbag that had been tampered with.
                The rope holding it was cleanly cut. The door was unlocked, and a bouquet of roses with a cryptic note
                was found on his makeup table. The note read: "The show must not go on."
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the lead actress and former lover of the victim; she was seen arguing with him about her contract earlier that day.',
            'B': 'Marcus Chen was the theater\'s accountant who discovered financial discrepancies and was pressured to keep quiet.',
            'C': 'Elena Reyes was the stage manager who had access to the fly system and was the last person seen leaving the backstage area before the incident.'
        },
        'key_evidence': [
            'Cut rope (clean slice, premeditated)',
            'Threatening note with bouquet',
            'Financial records showing embezzlement',
            'Witness saw someone on the catwalk during intermission'
        ],
        'case_summary': '''
            During the sold-out performance, the lead actor was killed in his dressing room by a falling sandbag.
            The theater is full of suspects with motives ranging from jealousy to money. Who wanted the final curtain
            to fall on Adrian Sterling?
        '''
    },
    {
        'id': 'yacht_murder',
        'title': 'Death on the High Seas',
        'difficulty': 'Hard',
        'victim': {
            'name': 'Dominic Sterling',
            'age': 52,
            'role': 'Billionaire Tech Mogul',
            'background': 'Founder of a social media empire, recently embroiled in a privacy scandal and a messy divorce.'
        },
        'crime_scene': {
            'location': 'Luxury Yacht "Sea Serpent" - Master Cabin',
            'time_of_death': 'Between 1:00 AM and 3:00 AM',
            'weapon': 'Blunt object (missing ship\'s bell)',
            'description': '''
                The victim was found in his cabin, which was locked from the inside.
                The porthole was open, and the ship's bell (a heavy bronze piece) was missing.
                There were signs of a struggle, and a life preserver was thrown overboard.
                GPS records show the yacht drifted off course for an hour that night.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the victim\'s estranged wife, on board to discuss divorce terms; she would inherit half his fortune.',
            'B': 'Marcus Chen was the yacht\'s captain, who was being blackmailed by the victim over a past smuggling conviction.',
            'C': 'Elena Reyes was the stewardess who had been secretly copying the victim\'s financial data onto a USB drive.'
        },
        'key_evidence': [
            'Missing ship\'s bell (presumed murder weapon)',
            'Open porthole and thrown life preserver',
            'Tampered GPS log (course altered)',
            'USB drive with encrypted files found in stewardess quarters'
        ],
        'case_summary': '''
            Miles from shore, billionaire Dominic Sterling was found dead in his locked cabin aboard his yacht.
            Only three crew members/passengers were present. The isolated setting means the killer is still on board.
        '''
    },
    {
        'id': 'gallery_murder',
        'title': 'The Poisoned Palette',
        'difficulty': 'Easy',
        'victim': {
            'name': 'Isabelle Moreau',
            'age': 34,
            'role': 'Controversial Contemporary Artist',
            'background': 'Known for provocative installations, she recently accused a rival of stealing her ideas and was about to unveil a shocking new piece.'
        },
        'crime_scene': {
            'location': 'Avant-Garde Gallery - Installation Room',
            'time_of_death': 'Around 8:00 PM (before opening)',
            'weapon': 'Poison (cyanide in her wine glass)',
            'description': '''
                The victim collapsed near her latest installation, a cage filled with live birds.
                A half-empty wine glass tested positive for cyanide.
                The gallery's security system was off for "artistic ambiance."
                A single white feather was found clutched in her hand.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the gallery owner who stood to gain financially from the victim\'s death due to increased art value.',
            'B': 'Marcus Chen was the victim\'s assistant who mixed her paints and prepared her drinks; he was often belittled publicly.',
            'C': 'Elena Reyes was a rival artist whose work was "coincidentally" similar to the victim\'s new piece.'
        },
        'key_evidence': [
            'Cyanide-laced wine glass',
            'White feather in victim\'s hand',
            'Security system turned off',
            'Rival\'s paint samples match victim\'s new work'
        ],
        'case_summary': '''
            The art world is shocked as rising star Isabelle Moreau is poisoned before her biggest show.
            Three people were in the gallery that evening: the owner, the assistant, and a jealous rival.
            The killer left a feather behind – but whose signature is it?
        '''
    },
    {
        'id': 'greenhouse_murder',
        'title': 'Poison Ivy',
        'difficulty': 'Medium',
        'victim': {
            'name': 'Harrison Green',
            'age': 62,
            'role': 'Award-Winning Botanist',
            'background': 'Renowned for developing rare hybrids, he recently announced a breakthrough that could revolutionize agriculture, but rumors of corporate sabotage swirled.'
        },
        'crime_scene': {
            'location': 'Private Greenhouse - Orchid House',
            'time_of_death': 'Between 4:00 PM and 6:00 PM',
            'weapon': 'Poison (plant toxin - curare)',
            'description': '''
                Found face-down among prized orchids, a small puncture wound on his neck.
                A broken syringe was found nearby containing traces of curare.
                A rare orchid (worth thousands) was missing from its pot.
                Muddy footprints led to the back entrance.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was a competing botanist whose research was discredited by the victim; she desperately wanted his new hybrid formula.',
            'B': 'Marcus Chen was the greenhouse manager who was secretly selling rare plants on the black market and was recently confronted by the victim.',
            'C': 'Elena Reyes was an environmental activist who believed the victim\'s experiments were dangerous and had been protesting outside the property.'
        },
        'key_evidence': [
            'Syringe with curare toxin',
            'Missing rare orchid',
            'Muddy footprints leading to back entrance',
            'Protest pamphlets found near scene'
        ],
        'case_summary': '''
            Botanist Harrison Green was killed in his own greenhouse by a potent plant toxin.
            His death leaves a fortune in research and a garden of suspects. Who had the knowledge to use such a rare poison?
        '''
    },
    {
        'id': 'train_murder',
        'title': 'Murder on the Midnight Express',
        'difficulty': 'Hard',
        'victim': {
            'name': 'Archibald Finch',
            'age': 68,
            'role': 'Retired Judge',
            'background': 'Known for harsh sentences, he was traveling with sensitive legal documents related to an old case. He had many enemies.'
        },
        'crime_scene': {
            'location': 'Private Cabin on the Midnight Express Train',
            'time_of_death': 'Approximately 2:00 AM',
            'weapon': 'Stab wound (missing letter opener)',
            'description': '''
                The judge was found slumped in his seat, a single stab wound to the chest.
                The door was locked with the chain on, but the window was open slightly.
                His briefcase was open and important documents were scattered.
                A conductor's cap was left on the floor.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the judge\'s former clerk who was dismissed in disgrace; she was on the train "by coincidence."',
            'B': 'Marcus Chen was a former defendant whose life was ruined by the judge\'s ruling; he had been released from prison just last month.',
            'C': 'Elena Reyes was the train attendant assigned to that car; she had been seen arguing with the judge about an unpaid fare earlier.'
        },
        'key_evidence': [
            'Locked room with open window',
            'Missing letter opener (likely murder weapon)',
            'Conductor\'s cap left behind',
            'Scattered legal documents (old case files)'
        ],
        'case_summary': '''
            On a moving train in the dead of night, a retired judge is murdered in his locked cabin.
            The killer could be anyone on board, but three passengers have particularly strong motives.
            The train will arrive at the station in two hours. Can you solve it before the killer disappears?
        '''
    },
    {
        'id': 'casino_murder',
        'title': 'Ace of Spades',
        'difficulty': 'Medium',
        'victim': {
            'name': 'Salvatore "Sal" Marchetti',
            'age': 59,
            'role': 'Casino Owner / Alleged Mobster',
            'background': 'Owned the largest casino in the city, rumored to have ties to organized crime. Recently, a rival family made threats.'
        },
        'crime_scene': {
            'location': 'Private Penthouse Suite above Casino',
            'time_of_death': 'Between 11:00 PM and 1:00 AM',
            'weapon': 'Single gunshot (silenced)',
            'description': '''
                Found sitting in his leather chair, a single gunshot to the chest.
                An Ace of Spades playing card was placed on his chest.
                The suite's security camera was looped with old footage.
                A half-empty bottle of expensive whiskey and two glasses were on the table.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the casino manager who was skimming profits and feared exposure; she was the last person seen leaving the suite.',
            'B': 'Marcus Chen was a high-stakes gambler who owed the victim a massive debt and had his kneecaps threatened.',
            'C': 'Elena Reyes was the cocktail waitress who delivered the whiskey; she had been seen talking to a known rival gang member earlier.'
        },
        'key_evidence': [
            'Ace of Spades card (calling card)',
            'Looped security footage',
            'Two glasses (one with lipstick)',
            'Silencer found in trash chute'
        ],
        'case_summary': '''
            Casino owner Sal Marchetti was executed in his own penthouse. The Ace of Spades suggests a professional hit,
            but was it an inside job? Three employees had reasons to want him dead, and the killer left a clue on purpose.
        '''
    },
    {
        'id': 'antique_shop_murder',
        'title': 'The Cursed Antique',
        'difficulty': 'Easy',
        'victim': {
            'name': 'Edgar Winthrop',
            'age': 74,
            'role': 'Antique Shop Owner',
            'background': 'Known for acquiring mysterious artifacts, he recently bragged about obtaining a cursed Egyptian scarab. He was found dead hours later.'
        },
        'crime_scene': {
            'location': 'Winthrop\'s Curiosities - Back Room',
            'time_of_death': 'Around 9:00 PM (closing time)',
            'weapon': 'Blunt force (heavy artifact)',
            'description': '''
                The victim was found behind the counter, struck from behind.
                The display case for the Egyptian scarab was smashed and the artifact was missing.
                A dusty footprint on the floor matched a rare vintage shoe.
                The front door was locked, but the back alley door was ajar.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was a collector who desperately wanted the scarab and had a heated argument with the victim earlier that day.',
            'B': 'Marcus Chen was a rival dealer who accused the victim of stealing the scarab from him years ago.',
            'C': 'Elena Reyes was a cleaning lady who had just started working there; she claims to have seen a "shadowy figure" near the back door.'
        },
        'key_evidence': [
            'Missing cursed scarab',
            'Dusty vintage footprint',
            'Smashed display case',
            'Back door ajar'
        ],
        'case_summary': '''
            Edgar Winthrop claimed he owned a cursed artifact. By nightfall, he was dead and the scarab was gone.
            Was it a robbery gone wrong, or did someone believe in the curse enough to kill for it?
        '''
    },
    {
        'id': 'ski_lodge_murder',
        'title': 'Avalanche of Lies',
        'difficulty': 'Hard',
        'victim': {
            'name': 'Blake Sterling',
            'age': 45,
            'role': 'CEO of Outdoor Gear Company',
            'background': 'Cutthroat businessman, recently laid off half the company and was vacationing with his executive team. An avalanche warning had trapped everyone at the lodge.'
        },
        'crime_scene': {
            'location': 'Snowpeak Lodge - Hot Tub Deck',
            'time_of_death': 'Between 10:00 PM and 11:00 PM',
            'weapon': 'Electrocution (tampered outdoor wiring)',
            'description': '''
                The victim was found in the hot tub, unresponsive. Investigation revealed the outdoor lighting wire
                had been deliberately stripped and dropped into the water. The fuse box was found unlocked.
                The lodge was isolated due to heavy snow and an avalanche blocking the only road.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was the CFO who was about to be fired for objecting to the layoffs; she had access to the maintenance room.',
            'B': 'Marcus Chen was the head of engineering who had been humiliated by the victim in a meeting; he knew exactly how to rig the wiring.',
            'C': 'Elena Reyes was a junior employee who was having a secret affair with the victim and was seen arguing with him by the hot tub earlier.'
        },
        'key_evidence': [
            'Tampered wiring (stripped deliberately)',
            'Unlocked fuse box',
            'Witness saw someone in a red jacket near the deck',
            'Avalanche trapped everyone at lodge (no escape)'
        ],
        'case_summary': '''
            Stranded at a remote ski lodge by an avalanche, the CEO is found electrocuted in the hot tub.
            With no way in or out, the killer is definitely among the guests. Was it a disgruntled employee,
            a jealous lover, or a financial saboteur?
        '''
    },
    {
        'id': 'bakery_murder',
        'title': 'The Bitter Crumb',
        'difficulty': 'Easy',
        'victim': {
            'name': 'Martha Butterfield',
            'age': 65,
            'role': 'Beloved Pastry Chef',
            'background': 'Owner of the famous "Sweet Haven Bakery." She recently won a prestigious recipe contest but was known to guard her secret recipes fiercely.'
        },
        'crime_scene': {
            'location': 'Sweet Haven Bakery - Kitchen',
            'time_of_death': 'Approximately 5:00 AM (before opening)',
            'weapon': 'Rolling pin (blunt force)',
            'description': '''
                The victim was found on the kitchen floor, her prized rolling pin nearby.
                Flour was scattered everywhere, and her secret recipe book was missing from its locked drawer.
                A tray of burnt croissants was still in the oven, suggesting a struggle interrupted her work.
            '''
        },
        'suspects_involved': ['A', 'B', 'C'],
        'connections': {
            'A': 'Victoria Ashford was a rival baker from across town who had been trying to buy the bakery for years; the victim refused to sell.',
            'B': 'Marcus Chen was an apprentice baker who was fired last week for trying to photograph the secret recipes.',
            'C': 'Elena Reyes was a regular customer who had a gambling debt and was seen lingering near the back door the night before.'
        },
        'key_evidence': [
            'Missing secret recipe book',
            'Burnt croissants (timer stopped)',
            'Rolling pin with initials "M.B." (victim\'s own)',
            'Flour footprints leading out the back'
        ],
        'case_summary': '''
            Martha Butterfield, the sweetest baker in town, met a bitter end in her own kitchen.
            Her famous secret recipes are missing. Was it a jealous rival, a disgruntled apprentice, or a desperate customer?
        '''
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



def get_stress_level(score):
    """Phase 4 Stress Mechanics"""
    if score >= 85: return 'Extreme'
    if score >= 60: return 'High'
    if score >= 40: return 'Medium'
    return 'Low'

def evaluate_intent_and_strategy(suspect, question, game):
    """Phase 3: Determine intent and strategy"""
    question_lower = question.lower()
    
    # Phase 6 & 3 Check: Evidence mentioned?
    case = game.get('case', {})
    evidence_words = []
    for ev in case.get('key_evidence', []):
        for word in ev.lower().split():
            if len(word) > 4: evidence_words.append(word)
    evidence_mentioned = any(word in question_lower for word in evidence_words)
    
    intent = 'General'
    if evidence_mentioned:
        intent = 'Evidence'
    elif any(word in question_lower for word in ['where', 'location', 'place', 'alibi', 'when', 'time']):
        intent = 'Alibi'
    elif any(word in question_lower for word in ['why', 'motive', 'relation', 'know', 'feel']):
        intent = 'Motive'
        
    stress_level = get_stress_level(suspect['score'])
    
    if suspect['role'] == 'innocent' and stress_level == 'Extreme' and random.random() < 0.3:
        strategy = 'False Confession'
        base_answer = "Fine! I did it! Are you happy now? Just stop the questions... I can't take it anymore. *sobs* But I don't remember how I did it... everything is floating..."
        return intent, strategy, base_answer

    if suspect['role'] == 'killer':
        if intent == 'Evidence':
            if stress_level in ['High', 'Extreme']:
                strategy = 'Panic and Deflect'
                base_answer = "I don't know anything about that! Why are you asking me? Someone else must have put it there!"
            else:
                strategy = 'Lie'
                base_answer = "I've never seen that before in my life."
        elif intent == 'Alibi':
            if stress_level == 'Extreme':
                strategy = 'Slip Up Contradiction'
                base_answer = f"I was in the {suspect['real_location']}! I mean, I was exactly where I said I was!"
            elif stress_level == 'High':
                strategy = 'Defensive Lie'
                base_answer = f"I already told you, I was {suspect['base_alibi']}. Are you calling me a liar?"
            else:
                strategy = 'Lie'
                base_answer = f"I was {suspect['base_alibi']} the entire time."
        elif intent == 'Motive':
            if stress_level in ['High', 'Extreme']:
                strategy = 'Aggressive Denial'
                base_answer = "I had nothing to do with them. We were fine, entirely fine!"
            else:
                strategy = 'Lie'
                base_answer = "We were on good terms. I have no motive."
        else:
            strategy = 'Deflection'
            base_answer = "I had nothing to do with this. You should look at the others."
    else: # Innocent
        if intent == 'Evidence':
            if stress_level in ['High', 'Extreme']:
                strategy = 'Anxious Clarification'
                base_answer = "I don't know what that means! Please, I had nothing to do with it!"
            else:
                strategy = 'Truth'
                base_answer = "I really don't recognize that piece of evidence."
        elif intent == 'Alibi':
            strategy = 'Truth'
            base_answer = f"I was {suspect['base_alibi']}. That's the truth."
        else:
            strategy = 'Truth'
            base_answer = "I'm telling you everything I know."
            
    return intent, strategy, base_answer

def format_history(history):
    """Format conversation history for the prompt"""
    if not history:
        return "No previous questions asked yet."
    
    formatted = []
    for i, entry in enumerate(history, 1):
        formatted.append(f"Q{i}: {entry['question']}\nA{i}: {entry['answer']}")
    
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
    if score >= 85: return 'extreme stress', '🚫'
    if score >= 60: return 'high stress', '😠'
    if score >= 40: return 'medium stress', '😰'
    return 'low stress', '😌'


def apply_gravity_drift(suspect):
    if ANTI_GRAVITY_MODE and random.random() < 0.2:
        drift_options = [
            suspect['base_alibi'].replace('Study', 'Library').replace('Office', 'Conference Room'),
            suspect['base_alibi'] + " ...or was it earlier? I lose track.",
            suspect['base_alibi'] + " ...wait, the gravity shifted then."
        ]
        suspect['alibi'] = random.choice(drift_options)

def evaluate_question_effect(game, suspect_id, question):
    question_lower = question.lower()
    delta = 0
    reasons = []

    # Base increment for any question (pressure builds on everyone)
    delta += 5

    # Accusation keywords affect everyone strongly
    if any(keyword in question_lower for keyword in ACCUSATION_KEYWORDS):
        delta += 20
        reasons.append('direct accusation')

    # Contradiction keywords
    if any(keyword in question_lower for keyword in CONTRADICTION_KEYWORDS):
        delta += 10
        reasons.append('contradiction')

    # Aggressive tone
    if any(keyword in question_lower for keyword in AGGRESSIVE_KEYWORDS):
        delta += 8
        reasons.append('aggressive tone')

    suspect = game['suspects'][suspect_id]

    # Calming approach reduces tension for everyone (but killer resists more)
    if any(keyword in question_lower for keyword in CALMING_KEYWORDS):
        if suspect['role'] == 'killer':
            delta -= 2  # barely calms down
        else:
            delta -= 8

    # Repeated questions increase tension for killer more, but still affect innocents
    history = game['question_history'].get(suspect_id, [])
    if question_lower in history:
        if suspect['role'] == 'killer':
            delta += 12
        else:
            delta += 5
        reasons.append('repeated question')

    history.append(question_lower)
    game['question_history'][suspect_id] = history

    # Random noise makes meter less predictable
    delta += random.randint(-4, 6)

    return delta, reasons


games = {}


def make_game():
    game_id = str(uuid.uuid4())
    
    # 1. Randomly select 3 different suspects from all available profiles
    all_suspect_keys = list(SUSPECT_PROFILES.keys())
    selected_profile_keys = random.sample(all_suspect_keys, min(3, len(all_suspect_keys)))
    
    # Map selected profiles to A, B, C for frontend consistency
    api_suspect_ids = ['A', 'B', 'C']
    killer_id = random.choice(api_suspect_ids)
    
    suspects = {}
    for api_id, profile_key in zip(api_suspect_ids, selected_profile_keys):
        profile = SUSPECT_PROFILES[profile_key]
        mood, mood_icon = get_mood(20)
        suspects[api_id] = {
            'id': api_id,
            'name': profile['name'],
            'alias': profile['alias'],
            'title': profile['title'],
            'age': profile['age'],
            'relation': profile['relation'],
            'motive': profile['motive'],
            'bio': profile['bio'],
            'icon': profile['icon'],
            'role': 'killer' if api_id == killer_id else 'innocent',
            'history': [],
            'score': 20,
            'mood': mood,
            'mood_icon': mood_icon,
            'alibi': profile['alibi'],
            'real_location': profile['real_location'],
            'personality': profile['personality'],
            'base_alibi': profile['base_alibi']
        }
    
    # 2. Randomly select a case from available cases
    selected_case = random.choice(CASE_FILES).copy()
    
    old_conn = list(selected_case.get('connections', {}).values())
    new_conn = {}
    for i, api_id in enumerate(api_suspect_ids):
        fallback_role = "Was seen near the crime scene."
        role_text = old_conn[i] if i < len(old_conn) else fallback_role
        new_conn[api_id] = f"{suspects[api_id]['name']} - {role_text}"
    
    selected_case['connections'] = new_conn
    selected_case['suspects_involved'] = api_suspect_ids
    
    game = {
        'game_id': game_id,
        'killer_id': killer_id,
        'suspects': suspects,
        'question_count': 0,
        'questions_asked': 0,
        'time_remaining': TIME_LIMIT_HOURS,
        'question_history': {api_id: [] for api_id in api_suspect_ids},
        'created': True,
        'case': selected_case
    }
    games[game_id] = game
    return game


def format_prompt(suspect, question, game, intent, strategy, base_answer, stress_level):
    """Phase 8 & 10: Player guidance and immersion prompt formatting"""
    profile = SUSPECT_PROFILES[suspect['id']]
    
    # Grab the last 6 interactions for accurate memory & contradiction checks
    history_arr = suspect['history'][-6:] if 'history' in suspect else []
    history_str = format_history(history_arr)
    
    case = game.get('case', {})
    evidence_str = "\n".join(f"- {ev}" for ev in case.get('key_evidence', []))
    
    anti_gravity_context = ""
    if ANTI_GRAVITY_MODE:
        anti_gravity_context = """
# ANTI-GRAVITY INTERROGATION PROTOCOL
You are being questioned in a zero-gravity environment. Your thoughts drift, memories float unanchored.
- Your answers may momentarily contradict themselves as if your mind is weightless.
- You might recall a detail you previously forgot, or forget something you just said.
- Your emotional state is untethered: calm one second, agitated the next.
- You sometimes speak in fragments, as if pulling words from a floating cloud.
- The detective's questions seem to come from all directions; you may lose track of time.
This is not a malfunction-it is the new reality of the interrogation. Embrace the drift.
"""

    tells = profile.get('tells', ['touches face', 'voice wavers', 'blinks rapidly', 'shifts weight'])
    
    adaptation_note = ""
    if suspect['score'] >= 60:
        adaptation_note = f"# Adaptation (Suspect becoming unraveled)\nNotable: Their tension level is at {suspect['score']}% - they should be showing signs of stress."

    system_content = f"""You are an advanced game design engine roleplaying as {profile['name']} ({profile['alias']}), a suspect in a detective game.
{anti_gravity_context}

# Core Identity
Role: {suspect['role'].upper()} (Keep this secret unless extreme pressure forces a confession)
Hidden Secret: {profile.get('hidden_secrets', '')}
Truthfulness Baseline: {profile.get('truthfulness_baseline', '100')}%

# Personality & Tells
Archetype: {profile.get('archetype', 'Neutral')}
Behavior Traits: {profile['personality']}
Tells when stressed: {', '.join(tells)}

# Stress & Tension
Current Stress Level: {stress_level}
- Low: Controlled but with subtle drift.
- Medium: Hesitation, minor slips, phrases may hang unfinished.
- High: Contradictions appear, emotional whiplash, may start a sentence and end it differently.
- Extreme: Refusal, breakdown, or accidental truth fragments floating to surface.

# Strategy & Memory
Player Intent: {intent}
Core Strategy: {strategy}
Base Answer: "{base_answer}"

Past Conversation (may be hazy):
{history_str}
{adaptation_note}

Case Evidence (if mentioned, react with appropriate gravity distortion):
{evidence_str}

CRITICAL DIRECTIVES:
1. NEVER break character. You ARE the suspect being questioned.
2. Keep answers concise and focused on answering the detective's question.
3. Respond naturally without any asterisks, brackets, or stage directions.
4. If your Strategy is 'Slip Up Contradiction', make the contradiction feel natural and unintentional.
"""
    return [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': f"Detective asks (from somewhere in the chamber): {question}"}
    ]

def call_openrouter(messages):
    import time
    if not OPENROUTER_API_KEY:
        return 'OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.'
    
    payload = {
        'model': 'meta-llama/llama-2-70b-chat',
        'messages': messages,
        'temperature': 0.75,
        'max_tokens': 220,
    }
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and data['choices']:
                answer = data['choices'][0].get('message', {}).get('content', '').strip()
                # Strip action cues like *description* from the response
                answer = remove_action_cues(answer)
                return answer
            return 'The AI failed to produce an answer.'
        except Exception as exc:
            # If it's a 401 error, retrying won't help because it's a key issue
            if hasattr(exc, 'response') and exc.response is not None and exc.response.status_code == 401:
                return f'Error: 401 Unauthorized. Your OpenRouter API key is invalid or missing.'
                
            if attempt == max_retries - 1:
                return f'Error: {str(exc)}'
            time.sleep(2)  # Wait before retrying

def remove_action_cues(text):
    """Remove action cues in asterisks from AI responses"""
    import re
    # Remove *text* patterns while preserving the rest
    text = re.sub(r'\*[^*]*\*', '', text)
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text



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

    apply_gravity_drift(suspect)

    if game['time_remaining'] <= 0:
        return jsonify({'error': 'Time has run out. The investigation is over.'}), 400
    
    intent, strategy, base_answer = evaluate_intent_and_strategy(suspect, question, game)
    stress_level = get_stress_level(suspect['score'])
    
    prompt = format_prompt(suspect, question, game, intent, strategy, base_answer, stress_level)
    answer = call_openrouter(prompt)
    store_answer(game_id, suspect_id, question, answer, strategy)

    tension_change, reasons, hours_spent, mood = update_tension(game, suspect_id, question)
    
    entry = {
        'question': question,
        'answer': answer,
        'mode': strategy,
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
            'mode': strategy,
            'history': suspect['history'],
            'suspects': get_suspect_summary(game),
            'tension_scores': get_tension_summary(game),
            'time_remaining': game['time_remaining'],
            'message': 'The clock has run out. The investigation has ended.',
            'game_over': True,
        })

    return jsonify({
        'game_id': game_id,
        'suspect_id': suspect_id,
        'answer': answer,
        'mode': strategy,
        'history': suspect['history'],
        'suspects': get_suspect_summary(game),
        'tension_scores': get_tension_summary(game),
        'time_remaining': game['time_remaining'],
        'reason': reasons,
        'message': '',
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
    
    # Phase 9: Multiple Outcomes Calculation
    q_asked = game['questions_asked']
    tensions = [v['score'] for v in game['suspects'].values()]
    avg_tension = sum(tensions) / len(tensions) if tensions else 0
    killer_tension = game['suspects'][game['killer_id']]['score']
    
    outcome_rank = "Inconclusive"
    message = ""
    if correct:
        if q_asked < 3:
            outcome_rank = "Lucky Guess"
            message = "Correct! But with so few questions asked, they're calling it a lucky guess down at the precinct. The DA might struggle to convict."
        elif killer_tension > 70:
            outcome_rank = "Master Detective"
            message = "Brilliant! You applied the perfect amount of pressure and unmasked the killer beautifully. An airtight case!"
        else:
            outcome_rank = "Solid Case"
            message = "Correct! Your detective instincts were right. The killer has been unmasked and justice is served."
    else:
        if q_asked > 15:
            outcome_rank = "Embarrassing Failure"
            message = "Wrong suspect! Despite hours of interrogation, you let the real killer slip away while harassing an innocent."
        else:
            outcome_rank = "False Accusation"
            message = "Wrong suspect. You jumped the gun. The real killer is still at large. Case closed in failure."
            
    return jsonify(
        {
            'game_id': game_id,
            'accused': suspect_id,
            'correct': correct,
            'outcome_rank': outcome_rank,
            'killer_id': game['killer_id'] if correct else None,
            'message': message,
            'questions_asked': q_asked
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
    return send_from_directory('frontend/static', 'index.html')

@app.route('/case/<game_id>', methods=['GET'])
def get_case_details(game_id):
    """Return the case file for the current game"""
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found.'}), 404
    
    case_data = game.get('case', {})
    safe_case = {
        'id': case_data.get('id'),
        'title': case_data.get('title'),
        'difficulty': case_data.get('difficulty'),
        'victim': case_data.get('victim'),
        'crime_scene': case_data.get('crime_scene'),
        'key_evidence': case_data.get('key_evidence'),
        'case_summary': case_data.get('case_summary'),
        'connections': case_data.get('connections', {})
    }
    return jsonify({'case': safe_case})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
