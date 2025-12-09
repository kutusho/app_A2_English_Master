import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit.components.v1 as components  # Para embeber las presentaciones HTML

# ==========================
# BASIC CONFIG
# ==========================
st.set_page_config(
    page_title="A2 English Master",
    page_icon="📘",
    layout="wide"
)

# Base paths for assets and media
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())
AUDIO_DIR = BASE_DIR / "audio"
STATIC_DIR = BASE_DIR / "static"  # aquí irán las presentaciones HTML

# Admin code (cámbialo o usa variable de entorno ENGLISH_MASTER_ADMIN_CODE)
ADMIN_ACCESS_CODE = os.getenv("ENGLISH_MASTER_ADMIN_CODE", "A2-ADMIN-2025")


# ==========================
# GLOBAL STYLES (BRANDING + DARK MODE FRIENDLY)
# ==========================

def inject_global_css():
    st.markdown(
        """
<style>
/* ========= PALETA BASE (MODO CLARO) ========= */
:root {
  --bg-main: #eef3fb;
  --bg-soft: #f9fafb;
  --card-bg: #ffffff;
  --navy: #111827;
  --navy-soft: #1f2937;
  --accent-blue: #1d4ed8;
  --accent-blue-soft: #2563eb;
  --accent-red: #b91c1c;
  --accent-gold: #eab308;
  --muted: #6b7280;
  --border-subtle: rgba(15, 23, 42, 0.12);
  --shadow-soft: 0 18px 45px rgba(15, 23, 42, 0.18);
}

/* ========= PALETA PARA MODO OSCURO ========= */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-main: #020617;
    --bg-soft: #020617;
    --card-bg: #020617;
    --navy: #e5e7eb;
    --navy-soft: #f9fafb;
    --accent-blue: #60a5fa;
    --accent-blue-soft: #3b82f6;
    --accent-red: #fb7185;
    --accent-gold: #facc15;
    --muted: #9ca3af;
    --border-subtle: rgba(148, 163, 184, 0.4);
    --shadow-soft: 0 22px 60px rgba(0, 0, 0, 0.9);
  }
}

/* ========= RESET SUAVE ========= */
*, *::before, *::after {
  box-sizing: border-box;
}

/* Fondo general */
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Fondo de toda la app */
.stApp {
  background: radial-gradient(circle at top left, #ffffff 0%, var(--bg-main) 45%, #c7d2fe 100%);
  color: var(--navy);
  min-height: 100vh;
}

@media (prefers-color-scheme: dark) {
  .stApp {
    background: radial-gradient(circle at top left, #020617 0%, #020617 45%, #020617 100%);
  }
}

/* Contenedor principal de Streamlit */
.main .block-container {
  max-width: 1100px;
  padding-top: 3rem;
  padding-bottom: 3rem;
}

/* Títulos y texto */
h1, h2, h3 {
  color: var(--navy-soft);
}

h1 {
  font-weight: 800 !important;
}

@media (prefers-color-scheme: dark) {
  h1, h2, h3 {
    color: var(--navy-soft);
  }
}

/* Tablas más limpias */
table {
  border-collapse: collapse;
  width: 100%;
}

table thead tr th {
  background-color: rgba(248, 250, 252, 0.9);
  color: var(--navy-soft);
  font-weight: 600;
  border-bottom: 1px solid var(--border-subtle);
}

table tbody tr td {
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}

/* Cards suaves para cajas de contenido de Streamlit */
.stAlert, .stTable, .stDataFrame, .stMarkdown, .element-container {
  border-radius: 18px;
}

/* ========= MENÚ FLOTANTE SUPERIOR IZQUIERDA ========= */
.floating-menu-wrapper {
    position: fixed;
    top: 4.5rem;
    left: 1.4rem;
    z-index: 2000;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.floating-menu-toggle {
    display: none;
}

.floating-menu-button {
    background: linear-gradient(135deg, #1f4b99, #274b8f);
    color: #ffffff;
    border-radius: 999px;
    padding: 0.55rem 1.4rem;
    font-size: 0.95rem;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    border: none;
    user-select: none;
    white-space: nowrap;
}

.floating-menu-button:hover {
    filter: brightness(1.05);
}

.floating-menu-panel {
    position: absolute;
    top: 3.1rem;
    left: 0;
    background-color: #ffffff;
    border-radius: 0.9rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    padding: 0.6rem;
    min-width: 220px;
    opacity: 0;
    pointer-events: none;
    transform: translateY(-10px);
    transition: all 0.18s ease-out;
}

@media (prefers-color-scheme: dark) {
  .floating-menu-panel {
      background-color: #020617;
      border: 1px solid rgba(148, 163, 184, 0.5);
  }
}

.floating-menu-header {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #555;
    margin-bottom: 0.4rem;
    padding: 0 0.2rem;
}

.menu-link {
    display: block;
    padding: 0.4rem 0.5rem;
    border-radius: 0.55rem;
    text-decoration: none;
    font-size: 0.9rem;
    color: #222;
    margin-bottom: 0.15rem;
}

.menu-link:hover {
    background-color: #f1f4fb;
}

.menu-link.active {
    background-color: #1f4b99;
    color: #ffffff;
    font-weight: 600;
}

/* Toggle behaviour */
.floating-menu-toggle:checked ~ .floating-menu-panel {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0);
}

/* Responsive */
@media (max-width: 600px) {
    .floating-menu-wrapper {
        top: 4.0rem;
        left: 1rem;
    }
    .floating-menu-button {
        padding: 0.45rem 1.1rem;
        font-size: 0.9rem;
    }
    .floating-menu-panel {
        min-width: 200px;
    }
}

/* ========= BOTONES REDONDOS GLOBAL ========= */
div.stButton > button {
  border-radius: 999px;
  padding: 0.6rem 1.6rem;
  font-weight: 600;
  border: none;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-blue-soft));
  color: #ffffff;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.45);
  cursor: pointer;
  transition: all 0.15s ease-out;
}

div.stButton > button:hover {
  filter: brightness(1.06);
  transform: translateY(-1px);
}

div.stButton > button:active {
  transform: translateY(0);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.55);
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ==========================
# COURSE DATA
# ==========================

COURSE_INFO = {
    "title": "A2 English Master – Elementary Course",
    "level": "A2 – Elementary (CEFR)",
    "total_hours": 60,
    "units": 10,
    "hours_per_unit": 6,
    "description": (
        "A practical and communicative English course based on the Cambridge Empower "
        "A2 (Second Edition) syllabus. The program develops listening, speaking, reading "
        "and writing through real-life contexts such as travel, work, study and everyday "
        "communication."
    ),
    "target_students": (
        "Adult and young adult learners who already know basic A1 structures and want "
        "to consolidate and expand their English up to A2 level with clear, guided practice."
    ),
    "general_objectives": [
        "Understand and use everyday expressions related to personal information, daily life and common situations.",
        "Participate in simple, routine conversations that require a direct exchange of information.",
        "Describe in simple terms aspects of their background, immediate environment and basic needs.",
        "Build confidence using English in real-life situations: travel, work, cultural exchange and online communication."
    ],
    "methodology": [
        "Communicative approach with strong focus on speaking and listening.",
        "Task-based learning: role plays, pair work and group activities.",
        "Integration of grammar and vocabulary in realistic situations.",
        "Continuous feedback and short reflection moments (insights) to track progress."
    ],
    "assessment": [
        "Unit progress checks every two units.",
        "Continuous assessment through participation, homework and short tasks.",
        "Mid-course written and oral assessment after Unit 5.",
        "Final integrated exam (listening, reading, writing and speaking) after Unit 10."
    ]
}

# ==========================
# UNITS (SYLLABUS)
# ==========================

UNITS = [
    {
        "number": 1,
        "name": "People",
        "focus": "Personal information, countries, jobs and everyday objects.",
        "grammar": ["Verb be: present", "Wh-questions"],
        "vocabulary": ["Countries and nationalities", "Jobs", "Everyday things"],
        "skills": {
            "speaking": ["Ask and answer basic personal questions", "Talk about people you know"],
            "listening": ["Understand short conversations about people", "Recognise common introductions"],
            "reading": ["Notes about people", "A simple country profile"],
            "writing": ["Simple notes and introductions"]
        }
    },
    {
        "number": 2,
        "name": "Daily Life",
        "focus": "Routines, free time and frequency.",
        "grammar": ["Present simple", "Adverbs of frequency"],
        "vocabulary": ["Daily routines", "Free-time activities"],
        "skills": {
            "speaking": ["Talk about what you do every day", "Talk about free time"],
            "listening": ["Conversations about routines", "A conversation about time"],
            "reading": ["An article about habits"],
            "writing": ["Write an email about your routine"]
        }
    },
    {
        "number": 3,
        "name": "Food",
        "focus": "Food, drink and eating out.",
        "grammar": ["Countable and uncountable nouns", "Some / any", "A / an"],
        "vocabulary": ["Food and drink", "Restaurants"],
        "skills": {
            "speaking": ["Talk about food you like", "Order a meal in a restaurant"],
            "listening": ["A conversation in a restaurant"],
            "reading": ["A restaurant review"],
            "writing": ["Write about food you like"]
        }
    },
    {
        "number": 4,
        "name": "Places",
        "focus": "Homes, furniture and the city.",
        "grammar": ["There is / there are", "Prepositions of place"],
        "vocabulary": ["Buildings and furniture", "Places in a city"],
        "skills": {
            "speaking": ["Describe your home", "Talk about your neighbourhood"],
            "listening": ["A conversation about a new home"],
            "reading": ["An article about a town"],
            "writing": ["Short descriptions of places"]
        }
    },
    {
        "number": 5,
        "name": "Past",
        "focus": "Life events and family history.",
        "grammar": ["Past simple (regular verbs)", "Past simple: positive/negative"],
        "vocabulary": ["Regular verbs", "Life events"],
        "skills": {
            "speaking": ["Talk about your past", "Talk about your family"],
            "listening": ["A life story"],
            "reading": ["Notes about childhood"],
            "writing": ["Write about your family history"]
        }
    },
    {
        "number": 6,
        "name": "Leisure",
        "focus": "Free time, days out and past experiences.",
        "grammar": ["Past simple (irregular verbs)", "Past simple questions"],
        "vocabulary": ["Free-time activities", "Days out"],
        "skills": {
            "speaking": ["Make future arrangements based on past experiences"],
            "listening": ["Conversations about plans"],
            "reading": ["An article about leisure"],
            "writing": ["Short messages about plans"]
        }
    },
    {
        "number": 7,
        "name": "Work",
        "focus": "Jobs, work routines and comparisons.",
        "grammar": ["Comparative adjectives", "Present continuous"],
        "vocabulary": ["Jobs", "Workplace language"],
        "skills": {
            "speaking": ["Talk about jobs and studies", "Compare people, places and things"],
            "listening": ["Conversations at work"],
            "reading": ["A work profile"],
            "writing": ["Write about your job or studies"]
        }
    },
    {
        "number": 8,
        "name": "Travel",
        "focus": "Trips, geography and future plans.",
        "grammar": ["Future: going to", "Travel questions"],
        "vocabulary": ["Geography", "Travel and holiday vocabulary"],
        "skills": {
            "speaking": ["Talk about future plans", "Plan a trip"],
            "listening": ["A conversation about a trip"],
            "reading": ["A travel blog"],
            "writing": ["Write about travel plans"]
        }
    },
    {
        "number": 9,
        "name": "Health",
        "focus": "Health, body and lifestyle.",
        "grammar": ["Should / shouldn’t", "Imperatives"],
        "vocabulary": ["Parts of the body", "Health problems"],
        "skills": {
            "speaking": ["Give advice", "Talk about lifestyle and routines"],
            "listening": ["A conversation at the doctor’s"],
            "reading": ["An article about sports and health"],
            "writing": ["Write basic health advice"]
        }
    },
    {
        "number": 10,
        "name": "The World",
        "focus": "Countries, geography and world cultures.",
        "grammar": ["Present perfect (ever/never)", "Present vs past"],
        "vocabulary": ["Countries and geography", "Continents"],
        "skills": {
            "speaking": ["Talk about places you have visited", "Talk about world cultures"],
            "listening": ["A conversation about world travel"],
            "reading": ["An article about unusual places"],
            "writing": ["Write about your country"]
        }
    }
]

# ==========================
# LESSONS BY UNIT
# ==========================

LESSONS = {
    1: [
        {
            "title": "Class 1 – Personal information",
            "theory": [
                "Verb to be in the present (affirmative, negative and questions).",
                "Subject pronouns (I, you, he, she, it, we, they).",
                "Basic word order in English sentences."
            ],
            "practice": [
                "Complete short dialogues with am / is / are.",
                "Introduce yourself and a partner: “This is …”.",
                "Card game with countries and nationalities."
            ],
            "insights": [
                "In English you almost always need a subject – avoid sentences without I / you / he…",
                "Practice saying your name, country and job in under 20 seconds."
            ]
        },
        {
            "title": "Class 2 – Countries & jobs",
            "theory": [
                "Countries and nationalities (Mexico – Mexican, Brazil – Brazilian, etc.).",
                "Questions with “Where are you from?” and “What do you do?”."
            ],
            "practice": [
                "Class survey about countries and jobs.",
                "Role play: first conversation at an international event."
            ],
            "insights": [
                "Learn nationalities for the countries you usually receive as tourists.",
                "Always use capital letters for countries and nationalities in English."
            ]
        },
        {
            "title": "Class 3 – People you know",
            "theory": [
                "Review of verb be and Wh-questions.",
                "Basic adjectives to describe people (friendly, funny, quiet, etc.)."
            ],
            "practice": [
                "Talk about three important people in your life.",
                "Write short notes about friends or family members."
            ],
            "insights": [
                "With 10–15 adjectives you can describe almost anyone at A2 level.",
                "Think of real people (family, colleagues, tourists) when you practise."
            ]
        }
    ],
    2: [
        {
            "title": "Class 1 – Daily routines",
            "theory": [
                "Present simple: basic structure.",
                "Adverbs of frequency (always, usually, sometimes, never)."
            ],
            "practice": [
                "Complete a daily schedule with routines.",
                "Interview a partner: “What time do you …?”."
            ],
            "insights": [
                "Adverbs of frequency usually go before the main verb (I usually get up at 7).",
                "Connect English to your real routine to remember faster."
            ]
        },
        {
            "title": "Class 2 – Free time",
            "theory": [
                "Present simple in questions and short answers.",
                "Free-time activities vocabulary."
            ],
            "practice": [
                "Survey about favourite free-time activities.",
                "Create a simple bar chart and talk about the results."
            ],
            "insights": [
                "Short answers (“Yes, I do / No, I don’t”) help a lot in listening and speaking.",
                "Use “I like / I love / I don’t like” to sound more natural."
            ]
        },
        {
            "title": "Class 3 – Habits & lifestyle",
            "theory": [
                "Review of frequency expressions.",
                "Simple connectors: and, but, because."
            ],
            "practice": [
                "Write a short paragraph about your typical day.",
                "Compare routines with a partner: “We both…, but I…, and he…”."
            ],
            "insights": [
                "Even with simple grammar, connectors make your English sound more fluent.",
                "Think of your real day, not imaginary examples."
            ]
        }
    ],
    3: [
        {
            "title": "Class 1 – Food vocabulary",
            "theory": [
                "Countable vs uncountable nouns.",
                "Use of a / an / some / any."
            ],
            "practice": [
                "Classify food items into countable and uncountable.",
                "Shopping-list games in pairs."
            ],
            "insights": [
                "Don’t translate every word; learn food vocabulary directly in English.",
                "Use real menus from local restaurants when you practise."
            ]
        },
        {
            "title": "Class 2 – At the restaurant",
            "theory": [
                "Common questions in restaurants: “Can I have…?”, “Would you like…?”.",
                "Polite expressions: please, thank you, here you are."
            ],
            "practice": [
                "Role play waiter / customer.",
                "Create a mini-menu and practise ordering."
            ],
            "insights": [
                "Perfect content for tourism and hospitality contexts.",
                "Polite phrases completely change the customer experience."
            ]
        },
        {
            "title": "Class 3 – Talking about food you like",
            "theory": [
                "Like / love / don’t like + noun or + -ing.",
                "Food adjectives: spicy, sweet, salty, bitter."
            ],
            "practice": [
                "Group survey about favourite food.",
                "Write a short paragraph about your favourite dish."
            ],
            "insights": [
                "You can use this language to describe local gastronomy to visitors.",
                "Use typical dishes from Chiapas as examples when you teach."
            ]
        }
    ],
    4: [
        {
            "title": "Class 1 – My home",
            "theory": [
                "There is / there are.",
                "Some / any with places and objects."
            ],
            "practice": [
                "Draw a simple floor plan of your home and describe it.",
                "Spot-the-difference game with two homes."
            ],
            "insights": [
                "Use this language when you describe accommodation to tourists.",
                "Start with the general idea, then add details."
            ]
        },
        {
            "title": "Class 2 – In the city",
            "theory": [
                "Places in a city.",
                "Prepositions of place (next to, opposite, between, etc.)."
            ],
            "practice": [
                "Give directions on a simple map.",
                "Role play: tourist asking for directions in the city."
            ],
            "insights": [
                "Essential for guides and front-desk staff.",
                "Practise with real maps of Tuxtla or San Cristóbal."
            ]
        },
        {
            "title": "Class 3 – Describing places",
            "theory": [
                "Adjectives for places: quiet, busy, modern, traditional.",
                "Basic structure of a descriptive paragraph."
            ],
            "practice": [
                "Write about your neighbourhood or city.",
                "Present a tourist place in Chiapas to the group."
            ],
            "insights": [
                "Using photos or slides strongly activates vocabulary.",
                "You can reuse this text later in tours or websites."
            ]
        }
    ],
    5: [
        {
            "title": "Class 1 – Regular past",
            "theory": [
                "Past simple regular: affirmative.",
                "Pronunciation of -ed (/t/, /d/, /ɪd/)."
            ],
            "practice": [
                "Change present sentences into past.",
                "Timeline game with personal events."
            ],
            "insights": [
                "Good -ed pronunciation makes your speech much clearer.",
                "Connect verbs to real moments in your life to remember them."
            ]
        },
        {
            "title": "Class 2 – Past questions",
            "theory": [
                "Questions with did + base form.",
                "Short answers: “Yes, I did / No, I didn’t”."
            ],
            "practice": [
                "Interviews about last weekend.",
                "Survey: “When did you first…?” (travel abroad, work, study English)."
            ],
            "insights": [
                "Common questions help you keep real conversations going.",
                "Great for connecting with visitors during tours."
            ]
        },
        {
            "title": "Class 3 – Family stories",
            "theory": [
                "Review of regular past.",
                "Time expressions: yesterday, last week, two years ago."
            ],
            "practice": [
                "Write a short family story.",
                "Tell a personal anecdote in pairs."
            ],
            "insights": [
                "Personal stories make the language meaningful and memorable.",
                "Use storytelling techniques in your tours as well."
            ]
        }
    ],
    6: [
        {
            "title": "Class 1 – Free time in the past",
            "theory": [
                "Past simple irregular verbs (go, have, do, see, etc.).",
                "Contrast with present simple."
            ],
            "practice": [
                "Matching game: base form – past form.",
                "Circle game: “Yesterday I…”."
            ],
            "insights": [
                "Focus first on the most frequent irregular verbs.",
                "Create your own flashcards or Quizlet sets."
            ]
        },
        {
            "title": "Class 2 – Days out",
            "theory": [
                "Past simple questions with irregular verbs.",
                "Review of time expressions."
            ],
            "practice": [
                "Talk about a recent excursion or trip.",
                "Role play: describing your perfect day off."
            ],
            "insights": [
                "Excellent topic for tourism and weekend activities.",
                "Use real photos from your tours when possible."
            ]
        },
        {
            "title": "Class 3 – Leisure texts",
            "theory": [
                "Finding main ideas and details in short texts.",
                "Simple linkers for narratives."
            ],
            "practice": [
                "Read a short text about free time and answer questions.",
                "Write a mini blog entry about your weekend."
            ],
            "insights": [
                "Reading aloud helps you internalise grammar and rhythm.",
                "Combining reading and writing accelerates your progress."
            ]
        }
    ],
    7: [
        {
            "title": "Class 1 – Jobs & routines",
            "theory": [
                "Job vocabulary.",
                "Present simple vs present continuous (basic contrast)."
            ],
            "practice": [
                "Describe your current job or dream job.",
                "Guess-the-job game."
            ],
            "insights": [
                "Connect work vocabulary to your real context (guide, hotel, agency, etc.).",
                "Practise describing a typical workday in simple English."
            ]
        },
        {
            "title": "Class 2 – Comparisons",
            "theory": [
                "Comparative adjectives: bigger, more interesting, cheaper, etc.",
                "Structure: X is more/-er than Y."
            ],
            "practice": [
                "Compare cities, tourist destinations or jobs.",
                "Survey: “Which is better…?” and class discussion."
            ],
            "insights": [
                "Very useful when you recommend destinations or services.",
                "Master the pattern “X is more … than Y”."
            ]
        },
        {
            "title": "Class 3 – Work profile",
            "theory": [
                "Basic structure of a professional profile.",
                "Review of present tenses."
            ],
            "practice": [
                "Write a simple mini-CV in English.",
                "Introduce yourself professionally to the group."
            ],
            "insights": [
                "You can reuse this text for LinkedIn or your website.",
                "Short, clear sentences are very effective at A2 level."
            ]
        }
    ],
    8: [
        {
            "title": "Class 1 – Travel plans",
            "theory": [
                "Going to for future plans.",
                "Future time expressions (next week, this weekend, in July, etc.)."
            ],
            "practice": [
                "Talk about your next holiday or trip.",
                "Plan a trip in pairs (destination, transport, activities)."
            ],
            "insights": [
                "Ideal language for explaining itineraries to tourists.",
                "Use real tours or packages you offer when you practise."
            ]
        },
        {
            "title": "Class 2 – At the airport / station",
            "theory": [
                "Common travel questions and answers.",
                "Key vocabulary: ticket, boarding pass, platform, gate, delay, etc."
            ],
            "practice": [
                "Role play at an airport or station.",
                "Listen to short announcements (teacher-made) and complete information."
            ],
            "insights": [
                "These dialogues are great for international travellers.",
                "You can record simple audios yourself for extra listening practice."
            ]
        },
        {
            "title": "Class 3 – Travel blog",
            "theory": [
                "Paragraph structure for travel stories.",
                "Linkers: first, then, after that, finally."
            ],
            "practice": [
                "Read a short travel blog and answer questions.",
                "Write about your favourite trip using linkers."
            ],
            "insights": [
                "Perfect for social media or agency blog content.",
                "Think of a real tour and turn it into a short story."
            ]
        }
    ],
    9: [
        {
            "title": "Class 1 – Parts of the body",
            "theory": [
                "Body vocabulary (head, arm, back, knee, etc.).",
                "Useful structures for pain: “My back hurts”, “I have a headache”."
            ],
            "practice": [
                "Point-and-say games with body parts.",
                "Mini dialogues about simple injuries."
            ],
            "insights": [
                "Very useful in emergency situations with tourists.",
                "Memorise a few key phrases like “Do you need a doctor?”."
            ]
        },
        {
            "title": "Class 2 – Health problems",
            "theory": [
                "Should / shouldn’t for advice.",
                "Common health problems vocabulary (cold, fever, stomach ache, etc.)."
            ],
            "practice": [
                "Doctor / patient role plays.",
                "Give advice based on short symptom cards."
            ],
            "insights": [
                "Tone of voice and calm body language are part of communication too.",
                "Keep your advice simple and clear at this level."
            ]
        },
        {
            "title": "Class 3 – Healthy lifestyle",
            "theory": [
                "Review of advice and habits.",
                "Frequency expressions in lifestyle (once a week, every day, etc.)."
            ],
            "practice": [
                "Write recommendations for a healthy lifestyle.",
                "Simple debate: “What is healthy / unhealthy for you?”."
            ],
            "insights": [
                "This topic connects well with almost every group.",
                "Combine food, routines and health vocabulary in the same lesson."
            ]
        }
    ],
    10: [
        {
            "title": "Class 1 – Countries & continents",
            "theory": [
                "Country and continent vocabulary.",
                "Question: “Have you ever been to…?” (light introduction to present perfect)."
            ],
            "practice": [
                "World map activity: mark countries you have visited or want to visit.",
                "Pair questions about travel experience."
            ],
            "insights": [
                "You don’t need to master the whole present perfect, just key phrases.",
                "Focus on understanding and using short, fixed patterns first."
            ]
        },
        {
            "title": "Class 2 – World cultures",
            "theory": [
                "Adjectives for cultures and places (interesting, diverse, ancient, modern, etc.).",
                "Review of present and past for cultural facts."
            ],
            "practice": [
                "Talk about a culture you admire.",
                "Compare traditions between two countries."
            ],
            "insights": [
                "Connect this lesson with your passion for indigenous and local cultures.",
                "Excellent material for cultural tourism and storytelling."
            ]
        },
        {
            "title": "Class 3 – My country",
            "theory": [
                "Paragraph structure for country descriptions.",
                "Global review of key A2 grammar in context."
            ],
            "practice": [
                "Write a short text about Mexico for foreign visitors.",
                "Give a mini-tour style presentation of your country."
            ],
            "insights": [
                "This text can later be used on your website, brochures or tour scripts.",
                "It is a powerful way to show learners how much English they can use at A2."
            ]
        }
    ]
}

# ==========================
# LOGO & SIGNATURE
# ==========================

def show_logo():
    logo_path = os.path.join("assets", "logo-english-classes.png")
    if os.path.exists(logo_path):
        try:
            st.image(logo_path, width=220)
        except Exception:
            st.warning("The file 'logo-english-classes.png' exists but is not a valid image.")

def show_signature():
    sig_path = os.path.join("assets", "firma-ivan-diaz.png")
    if os.path.exists(sig_path):
        try:
            st.image(sig_path, width=220)
        except Exception:
            st.warning("The file 'firma-ivan-diaz.png' exists but is not a valid image.")
    else:
        st.info("Add your signature as 'assets/firma-ivan-diaz.png' to display it here.")


# ==========================
# NAVIGATION (QUERY PARAMS + FLOATING MENU)
# ==========================

PAGES = [
    {"id": "Overview", "label": "Overview", "icon": "🏠"},
    {"id": "English Levels", "label": "Levels", "icon": "📊"},
    {"id": "Assessment & Progress", "label": "Assessment", "icon": "📝"},
    {"id": "Instructor", "label": "Instructor", "icon": "👨‍🏫"},
    {"id": "Enter your class", "label": "Class", "icon": "🎓"},
    {"id": "Access", "label": "Access", "icon": "🔐"},
    {"id": "Admin", "label": "Admin", "icon": "⚙️"},
]

def _get_query_params():
    try:
        params = dict(st.query_params)
    except Exception:
        params = st.experimental_get_query_params()
    return params

def get_current_page_id() -> str:
    params = _get_query_params()
    page = params.get("page")
    if isinstance(page, list):
        page = page[0] if page else None
    valid_ids = [p["id"] for p in PAGES]
    if not page or page not in valid_ids:
        return "Overview"
    return page

def _rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

def go_to_page(page_id: str):
    valid_ids = [p["id"] for p in PAGES]
    if page_id not in valid_ids:
        page_id = "Overview"
    try:
        st.query_params["page"] = page_id
    except Exception:
        st.experimental_set_query_params(page=page_id)
    _rerun()

def render_floating_menu(current_page_id: str):
    items_html = []
    for page in PAGES:
        page_id = page["id"]
        label = page["label"]
        icon = page["icon"]
        is_active = (page_id == current_page_id)
        active_class = "active" if is_active else ""
        href = f"?page={page_id}"
        items_html.append(
            f'<a class="menu-link {active_class}" href="{href}" target="_self">{icon} {label}</a>'
        )

    menu_html = f"""
    <div class="floating-menu-wrapper">
        <input type="checkbox" id="floating-menu-toggle" class="floating-menu-toggle" />
        <label for="floating-menu-toggle" class="floating-menu-button">
            ☰ Menu
        </label>
        <div class="floating-menu-panel">
            <div class="floating-menu-header">Navigate</div>
            {''.join(items_html)}
        </div>
    </div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)


# ==========================
# HELPERS FOR AUDIO & PRESENTATIONS
# ==========================

def _audio_or_warning(filename: str):
    """Render audio if file exists, else a gentle warning."""
    audio_path = AUDIO_DIR / filename
    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning(f"Audio file not found: `audio/{filename}`")

def render_presentation_html(filename: str):
    """Render a Reveal.js HTML presentation inside the app if the file exists."""
    html_path = STATIC_DIR / filename
    if html_path.exists():
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            components.html(html_content, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error loading presentation: {e}")
    else:
        st.warning(f"Presentation file not found: `static/{filename}`")


# ==========================
# UNIT 1 – SESSION 1
# ==========================

def render_unit1_session1_hour1():
    st.subheader("Unit 1 – Session 1 · 1st Hour – Grammar & Writing")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Review the verb **be** in the present\n"
        "- Use **be** to talk about name, country and job\n"
        "- Write a short introduction about yourself and another person"
    )

    st.markdown("### ✏️ Warm-up")
    st.write(
        "Think of one person you know. Who is this person? "
        "Where is this person from? What is their job?"
    )
    st.info('Example: **"She is my friend. She is from Mexico. She is a designer."**')

    st.markdown("### 🧩 Grammar: Verb *be* – Forms")
    st.write(
        "I am → I’m\n\n"
        "You are → You’re\n\n"
        "He is → He’s\n\n"
        "She is → She’s\n\n"
        "We are → We’re\n\n"
        "They are → They’re"
    )

    st.markdown("### ✍️ Practice – Complete with *am / is / are*")
    st.markdown(
        "1. I ______ from Guatemala.\n\n"
        "2. She ______ a tour guide.\n\n"
        "3. They ______ not students.\n\n"
        "4. We ______ friends.\n\n"
        "5. He ______ from Italy.\n\n"
        "6. You ______ my classmate."
    )

    st.markdown("### ✍️ Guided writing – About you")
    st.info(
        'Model: *"Hello, my name is Laura. I’m from Mexico City and I’m Mexican. '
        'I’m a student. I’m very happy to study English."*'
    )
    st.write("Now write your own introduction in your notebook.")

    st.markdown("### ✍️ Guided writing – Another person")
    st.info(
        'Model: *"This is my friend Daniel. He’s from Costa Rica and he’s Costa Rican. '
        'He’s an architect. He isn’t a student."*'
    )
    st.write("Write about a friend, classmate or family member.")


def render_unit1_session1_hour2():
    st.subheader("Unit 1 – Session 1 · 2nd Hour – Listening & Speaking")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short audio introductions\n"
        "- Recognize countries, nationalities and jobs in context\n"
        "- Practice pronunciation\n"
        "- Speak about yourself and another person"
    )

    # Listening 1 – Welcome
    st.markdown("### 🔊 Listening 1 – Welcome")
    _audio_or_warning("unit1_hour2_welcome.mp3")
    st.caption(
        "Script: Welcome to the second part of Session One. Today, we will focus on "
        "listening and speaking. You will listen to real introductions, repeat key "
        "structures, and practice speaking about yourself and other people."
    )

    # Listening 2 – Verb be
    st.markdown("### 🔊 Listening 2 – Verb *be* pronunciation")
    _audio_or_warning("unit1_hour2_be_pronunciation.mp3")
    st.write("Listen first. Then repeat each form of **be**.")

    # Listening 3 – Countries & nationalities
    st.markdown("### 🔊 Listening 3 – Countries & nationalities")
    _audio_or_warning("unit1_hour2_countries.mp3")
    st.write("After listening, say: *I’m Mexican / I’m Guatemalan / I’m American*, etc.")

    # Listening 4 – Jobs
    st.markdown("### 🔊 Listening 4 – Jobs vocabulary")
    _audio_or_warning("unit1_hour2_jobs.mp3")
    st.write("Listen and repeat. Then answer: *What’s your job?*")

    # Listening 5 – Sample introduction
    st.markdown("### 🔊 Listening 5 – Sample introduction")
    _audio_or_warning("unit1_hour2_sample_intro.mp3")
    st.markdown(
        "**Questions:**\n\n"
        "1. What is his name?\n"
        "2. Where is he from?\n"
        "3. What is his job?\n"
        "4. What does he carry every day?"
    )

    # Final listening
    st.markdown("### 🔊 Final listening – A friend")
    _audio_or_warning("unit1_hour2_final_listening.mp3")
    st.markdown(
        "**Questions:**\n\n"
        "1. What is her name?\n"
        "2. Where is she from?\n"
        "3. What is her job?\n"
        "4. What does she carry every day?"
    )

    # Speaking tasks
    st.markdown("### 🗣️ Speaking – About you")
    st.markdown(
        "- What’s your name?\n"
        "- Where are you from?\n"
        "- What’s your nationality?\n"
        "- What’s your job?\n"
        "- What do you always carry with you?"
    )

    st.markdown("### 👥 Pair work – Interview")
    st.write(
        "Work in pairs. Ask and answer the questions above. "
        "Then introduce your partner to the group."
    )


# ==========================
# UNIT 1 – SESSION 2
# ==========================

def render_unit1_session2_hour1():
    st.subheader("Unit 1 – Session 2 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Countries, nationalities & jobs – Question patterns")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Review countries, nationalities and jobs.\n"
        "- Use question patterns: **What’s your name? / Where are you from? / What’s your nationality? / What do you do?**\n"
        "- Practise controlled exercises with questions and answers.\n"
        "- Write a short form for an international event."
    )

    st.markdown("### ✏️ Warm-up – International event")
    st.write(
        "Imagine you are at an **international tourism event**. "
        "You meet people from different countries."
    )
    st.markdown(
        "- What questions do you ask first?\n"
        "- What information is important for you?"
    )
    st.info(
        'Typical questions: *"What’s your name? Where are you from? '
        'What do you do?"*'
    )

    st.markdown("### 🧩 Question patterns – Form & meaning")
    st.markdown(
        "| Question                         | Meaning                        | Example answer                         |\n"
        "|----------------------------------|--------------------------------|----------------------------------------|\n"
        "| **What’s your name?**            | Ask for name                   | My name is Ana. / I’m Ana.             |\n"
        "| **Where are you from?**          | Ask for country / city         | I’m from Mexico City.                  |\n"
        "| **What’s your nationality?**     | Ask for nationality            | I’m Mexican.                           |\n"
        "| **What do you do?**              | Ask for job / occupation       | I’m a tour guide. / I work in a hotel. |"
    )

    st.markdown("### ✍️ Controlled practice 1 – Complete the questions")
    st.markdown(
        "Complete with **What / Where / What’s / What do**.\n\n"
        "1. ______ your name?\n\n"
        "2. ______ are you from?\n\n"
        "3. ______ your nationality?\n\n"
        "4. ______ you do?\n"
    )

    st.markdown("### ✍️ Controlled practice 2 – Match questions and answers")
    st.markdown("Match the questions (1–4) with the answers (a–d).")
    st.markdown(
        "**Questions:**\n"
        "1. What’s your name?\n"
        "2. Where are you from?\n"
        "3. What’s your nationality?\n"
        "4. What do you do?\n\n"
        "**Answers:**\n"
        "a. I’m a receptionist.\n"
        "b. I’m Brazilian.\n"
        "c. I’m from São Paulo.\n"
        "d. My name is Carla.\n"
    )

    st.markdown("### ✍️ Controlled practice 3 – Complete the dialogue")
    st.write("Complete the dialogue with the correct questions.")

    st.markdown(
        "**A:** Hi, I’m Luis. __(1)____________________?\n\n"
        "**B:** My name is Sara.\n\n"
        "**A:** Nice to meet you, Sara. __(2)____________________?\n\n"
        "**B:** I’m from Guatemala City.\n\n"
        "**A:** Oh, great. __(3)____________________?\n\n"
        "**B:** I’m Guatemalan.\n\n"
        "**A:** And __(4)____________________?\n\n"
        "**B:** I’m a travel agent.\n"
    )

    st.markdown("### ✍️ Guided writing – Registration form")
    st.write(
        "Now write a **short registration form** for an international event. "
        "Use the four question patterns."
    )
    st.markdown(
        "**Example form:**\n\n"
        "1. What’s your name?\n"
        "2. Where are you from?\n"
        "3. What’s your nationality?\n"
        "4. What do you do?\n"
    )
    st.write(
        "Students write the form in their notebook and then use it to interview a partner."
    )

    st.markdown("### 🗣️ Quick speaking – Pair interview")
    st.markdown(
        "In pairs:\n"
        "1. Use your form and ask the four questions.\n"
        "2. Take notes about your partner.\n"
        "3. Introduce your partner to the class:\n"
        '   *\"This is Ana. She is from Colombia. She is Colombian and she is a tour guide.\"*'
    )


def render_unit1_session2_hour2():
    st.subheader("Unit 1 – Session 2 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Countries, nationalities & jobs – International event")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand very slow introductions at an international event.\n"
        "- Recognize question patterns about name, country, nationality and job.\n"
        "- Practise short dialogues in pairs.\n"
        "- Prepare a final group introduction task."
    )

    # Listening 1 – Welcome
    st.markdown("### 🔊 Listening 1 – Welcome to Session 2")
    _audio_or_warning("U1_S2_audio1_welcome.mp3")
    st.caption(
        "Extra slow welcome to Session 2. Explains that students will listen to people "
        "from different countries and jobs at an international event."
    )

    # Listening 2 – Question patterns
    st.markdown("### 🔊 Listening 2 – Question patterns")
    _audio_or_warning("U1_S2_audio2_question_patterns.mp3")
    st.markdown(
        "**Focus:**\n"
        "- What’s your name?\n"
        "- Where are you from?\n"
        "- What’s your nationality?\n"
        "- What do you do?\n\n"
        "Students listen and repeat the questions several times."
    )

    # Listening 3 – Short dialogues
    st.markdown("### 🔊 Listening 3 – Short dialogues")
    _audio_or_warning("U1_S2_audio3_short_dialogues.mp3")
    st.write(
        "Listen to the mini-dialogues between two people at an international event. "
        "After listening, students practise the same dialogues in pairs."
    )
    st.markdown(
        "**Task:**\n"
        "1. Listen once – just understand the idea.\n"
        "2. Listen again and repeat.\n"
        "3. Practise in pairs changing the country, nationality and job."
    )

    # Listening 4 – Group introduction
    st.markdown("### 🔊 Listening 4 – Group introduction model")
    _audio_or_warning("U1_S2_audio4_group_introduction.mp3")
    st.markdown(
        "This audio gives a model of how to introduce several people in a group.\n\n"
        "**After listening, ask:**\n"
        "- How many people are in the group?\n"
        "- Where are they from?\n"
        "- What jobs do they have?"
    )

    # Listening 5 – Final task
    st.markdown("### 🔊 Listening 5 – Final task instructions")
    _audio_or_warning("U1_S2_audio5_final_task.mp3")
    st.markdown(
        "Students follow the instructions from the audio:\n"
        "1. Walk around the classroom and talk to **3 classmates**.\n"
        "2. Ask: *What’s your name? Where are you from? What do you do?*\n"
        "3. Take notes.\n"
        "4. At the end, introduce **one person** from your notes to the class."
    )

    st.markdown("### 🗣️ Speaking – Present a classmate")
    st.info(
        '"This is Carlos. He is from Colombia. He is Colombian and he is a tour guide. '
        'He works in Bogotá."'
    )
    st.write(
        "Students prepare one short introduction and present it to the group. "
        "Teacher checks pronunciation of countries, nationalities and jobs."
    )


# ==========================
# UNIT 1 – SESSION 3
# ==========================

def render_unit1_session3_hour1():
    st.subheader("Unit 1 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: People you know")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use **Wh- questions** to ask about people.\n"
        "- Use **adjectives** to describe personality and appearance.\n"
        "- Write a short description of a real person.\n"
        "- Review **verb be** in context."
    )

    st.markdown("### ✏️ Warm-up – People in your life")
    st.write("Think of **three important people** in your life.")
    st.markdown(
        "- Who are they?\n"
        "- How old are they?\n"
        "- What are they like?"
    )
    st.info('Example: *"This is my friend Laura. She is 28. She is very friendly and organized."*')

    st.markdown("### 🧩 Grammar – Wh- questions (review)")
    st.markdown(
        "| Question word | Use            | Example              |\n"
        "|--------------|----------------|----------------------|\n"
        "| **Who**      | person         | Who is he?           |\n"
        "| **Where**    | place / origin | Where is she from?   |\n"
        "| **How old**  | age            | How old is he?       |\n"
        "| **What … like** | personality | What is she like?    |\n"
        "| **What**     | job            | What does he do?     |"
    )

    st.markdown("**Complete the questions:**")
    st.markdown(
        "1. ___ is she?\n\n"
        "2. ___ is he from?\n\n"
        "3. ___ old is your friend?\n\n"
        "4. ___ is she like?\n\n"
        "5. ___ does he do?"
    )

    st.markdown("### 🧩 Adjectives to describe people")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Personality**")
        st.markdown(
            "- friendly\n"
            "- quiet\n"
            "- serious\n"
            "- funny\n"
            "- talkative\n"
            "- kind\n"
            "- shy\n"
            "- confident\n"
            "- patient\n"
            "- energetic"
        )

    with col2:
        st.markdown("**Appearance**")
        st.markdown(
            "- tall\n"
            "- short\n"
            "- young\n"
            "- old\n"
            "- strong"
        )
        st.info('Use **be**: *"She is tall"* – not *"She has tall".*')

    st.markdown("### ✍️ Controlled practice")
    st.write("Complete with adjectives:")
    st.markdown(
        "**Word bank:** friendly, funny, quiet, tall, young\n\n"
        "1. My nephew is very ______.\n\n"
        "2. My grandmother is ______ and ______.\n\n"
        "3. My best friend is ______ and ______.\n\n"
        "4. My teacher is ______ but very ______."
    )

    st.markdown("### ✍️ Guided writing – Model")
    st.info(
        '"This is my friend Marco. He is 25 years old.\n'
        'He is from Spain. He is Spanish.\n'
        'He is tall and very friendly.\n'
        'He works in a café and he is very funny."'
    )

    st.markdown("### ✍️ Guided writing – Your turn")
    st.write("Write about a real person you know. Answer these questions:")
    st.markdown(
        "- Who is the person?\n"
        "- How old are they?\n"
        "- Where are they from?\n"
        "- What are they like? (2–3 adjectives)\n"
        "- What do they do?"
    )
    st.write("Write **4–6 sentences** in your notebook, then share with your partner.")


def render_unit1_session3_hour2():
    st.subheader("Unit 1 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: People you know (listening & speaking – extra slow)")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand slow descriptions of different people.\n"
        "- Identify **name, age, personality and job** from audio.\n"
        "- Repeat and practise key adjectives with clear pronunciation.\n"
        "- Describe a real person and share the description orally."
    )

    # Listening 1
    st.markdown("### 🔊 Listening 1 – Welcome to Session 3")
    _audio_or_warning("U1_S3_audio1_intro.mp3")
    st.caption(
        "Extra slow · Warm introduction to Session 3 listening. "
        "Focus on what students will do in this part of the class."
    )

    # Listening 2 – Adjectives drill
    st.markdown("### 🔊 Listening 2 – Adjectives drill")
    _audio_or_warning("U1_S3_audio2_adjectives_drill.mp3")
    st.write(
        "Listen and repeat the adjectives. First, only listen. "
        "Then listen and repeat in chorus; finally, individual students practise."
    )
    st.markdown(
        "**Adjectives in this drill:**\n\n"
        "- friendly, funny, quiet, serious, talkative\n"
        "- kind, shy, confident, patient, energetic"
    )

    # Listening 3 – Short descriptions
    st.markdown("### 🔊 Listening 3 – Short descriptions")
    _audio_or_warning("U1_S3_audio3_short_descriptions.mp3")
    st.write("Listen to three short descriptions and complete the table:")

    st.markdown(
        "| # | Name    | Age   | Personality     | Job        |\n"
        "|---|---------|-------|-----------------|------------|\n"
        "| 1 | Maria   | ____  | ____            | ____       |\n"
        "| 2 | Roberto | ____  | ____            | ____       |\n"
        "| 3 | Elena   | ____  | ____            | ____       |"
    )
    st.info("Play twice: first for general idea, second for details.")

    # Listening 4 – Long description
    st.markdown("### 🔊 Listening 4 – Long description")
    _audio_or_warning("U1_S3_audio4_long_description.mp3")
    st.markdown("**After listening, ask these questions:**")
    st.markdown(
        "- How old is Daniel?\n"
        "- What is his job?\n"
        "- What adjectives describe him?"
    )

    # Listening 5 – Final task
    st.markdown("### 🔊 Listening 5 – Final task instructions")
    _audio_or_warning("U1_S3_audio5_final_task.mp3")
    st.markdown("Students follow these steps:")
    st.markdown(
        "1. Think of a person they know well.\n"
        "2. Ask their partner:\n"
        "   - Who is the person?\n"
        "   - How old is he or she?\n"
        "   - What is he or she like?\n"
        "   - What does he or she do?\n"
        "3. Listen carefully and take notes.\n"
        "4. Introduce their partner’s person to the class."
    )

    st.markdown("### 🗣️ Speaking – Introduce a person")
    st.info(
        '"This is my partner’s friend Ana. She is 30 years old.\n'
        'She is from Mexico. She is very friendly and energetic.\n'
        'She works as a designer."'
    )
    st.write(
        "Students present in pairs or small groups. "
        "Teacher listens for correct use of **be** and adjectives."
    )


# ==========================
# UNIT 2 – SESSION 1
# ==========================

def render_unit2_session1_hour1():
    st.subheader("Unit 2 – Session 1 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Daily routines")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use the **present simple** to talk about daily routines.\n"
        "- Use **adverbs of frequency** (always, usually, sometimes, never).\n"
        "- Write a short paragraph about your typical day."
    )

    st.markdown("### ✏️ Warm-up – Your day")
    st.write("Think about a normal weekday for you.")
    st.markdown(
        "- What time do you get up?\n"
        "- What do you do in the morning?\n"
        "- What do you do in the afternoon and evening?"
    )
    st.info('Example: *"I get up at 7:00. I have breakfast, then I go to work."*')

    st.markdown("### 🧩 Grammar – Present simple (affirmative)")
    st.markdown(
        "We use the **present simple** to talk about routines and habits.\n\n"
        "**Structure:**\n\n"
        "- I / You / We / They **+ base verb** → *I work, They live, We study*\n"
        "- He / She / It **+ base verb + s / es** → *He works, She lives, It closes*"
    )

    st.markdown("**Examples:**")
    st.markdown(
        "- I get up at 6:30.\n"
        "- She starts work at 9:00.\n"
        "- They finish school at 3:00.\n"
        "- He watches TV in the evening."
    )

    st.markdown("### ✍️ Practice – Complete with the correct form")
    st.markdown(
        "1. I ______ (get up) at 7:00.\n\n"
        "2. She ______ (start) work at 9:30.\n\n"
        "3. They ______ (have) lunch at 2:00.\n\n"
        "4. He ______ (go) to bed at 11:00.\n\n"
        "5. We ______ (study) English on Tuesday.\n\n"
        "6. My sister ______ (watch) series at night."
    )

    st.markdown("### 🧩 Adverbs of frequency")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Common adverbs:**")
        st.markdown(
            "- always (100%)\n"
            "- usually\n"
            "- often\n"
            "- sometimes\n"
            "- hardly ever\n"
            "- never (0%)"
        )

    with col2:
        st.markdown("**Position in the sentence:**")
        st.markdown(
            "- Before the main verb: *I **usually** get up at 7:00.*\n"
            "- After **be**: *She is **often** late.*"
        )
        st.info('Example: *"I sometimes have breakfast at a café."*')

    st.markdown("### ✍️ Controlled practice – Frequency")
    st.markdown(
        "Rewrite the sentences with an adverb of frequency.\n\n"
        "1. I eat breakfast at home. (**usually**)\n\n"
        "2. She is late for work. (**sometimes**)\n\n"
        "3. They drink coffee in the evening. (**never**)\n\n"
        "4. We go to the cinema. (**hardly ever**)"
    )

    st.markdown("### ✍️ Guided writing – My typical day")
    st.info(
        '"On weekdays I usually get up at 6:30. I have coffee and bread, then I go to work.\n'
        'I start work at 8:00 and finish at 4:00. After work I sometimes go to the gym\n'
        'or I meet my friends. I never go to bed late on Monday to Friday."'
    )

    st.write("Now write **5–7 sentences** about your typical day. Use:")
    st.markdown(
        "- Present simple (get up, start, finish, go, have…)\n"
        "- At least **3 adverbs of frequency**."
    )


def render_unit2_session1_hour2():
    st.subheader("Unit 2 – Session 1 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Daily routines (listening & speaking)")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short audios about people’s routines.\n"
        "- Identify **times, activities and frequency**.\n"
        "- Speak about your own daily routine."
    )

    st.markdown("### 🔊 Listening 1 – Welcome to Unit 2, Session 1")
    _audio_or_warning("U2_S1_audio1_intro.mp3")
    st.caption(
        "Slow introduction to the topic of daily routines: what students will hear and practise."
    )

    st.markdown("### 🔊 Listening 2 – Daily routine vocabulary")
    _audio_or_warning("U2_S1_audio2_routines_vocab.mp3")
    st.markdown(
        "Listen and repeat verbs like: **get up, have breakfast, go to work, start work, finish work, "
        "have lunch, study, go home, cook, relax, go to bed**."
    )

    st.markdown("### 🔊 Listening 3 – Two people’s routines")
    _audio_or_warning("U2_S1_audio3_two_routines.mp3")
    st.write("Listen and complete the table:")

    st.markdown(
        "| Person | Time they get up | Time they start work / school | What they do in the evening |\n"
        "|--------|------------------|-------------------------------|------------------------------|\n"
        "| A      | ______           | ______                        | ______                       |\n"
        "| B      | ______           | ______                        | ______                       |"
    )

    st.markdown("### 🔊 Listening 4 – Frequency")
    _audio_or_warning("U2_S1_audio4_frequency.mp3")
    st.markdown(
        "Listen for **always, usually, sometimes, never**.\n\n"
        "**Questions:**\n"
        "- What does Person A always do in the morning?\n"
        "- What does Person B sometimes do in the evening?\n"
        "- What do they never do on weekdays?"
    )

    st.markdown("### 🗣️ Speaking – My day")
    st.markdown(
        "Use these prompts to speak for **1–2 minutes** about your day:\n\n"
        "- On weekdays I usually…\n"
        "- I get up at… and I start work/school at…\n"
        "- In the evening I sometimes…\n"
        "- I never… on weekdays."
    )

    st.markdown("### 👥 Pair work – Compare your routines")
    st.write("Work in pairs. Ask and answer:")
    st.markdown(
        "- What time do you get up on weekdays?\n"
        "- Do you have breakfast at home or outside?\n"
        "- What do you usually do after work / school?\n"
        "- Do you ever study or work at night?"
    )
    st.info("Then tell the class **one similarity** and **one difference** between your routines.")


# ==========================
# UNIT 2 – SESSION 2
# ==========================

def render_unit2_session2_hour1():
    st.subheader("Unit 2 – Session 2 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Free time & present simple questions")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use **present simple questions** with **do / does**.\n"
        "- Talk about **free-time activities**.\n"
        "- Write short questions and answers about free time."
    )

    st.markdown("### ✏️ Warm-up – Free time")
    st.write("Think about your free time.")
    st.markdown(
        "- What do you do in your free time?\n"
        "- When do you usually have free time?\n"
        "- Do you prefer staying at home or going out?"
    )

    st.markdown("### 🧩 Grammar – Questions with do/does")
    st.markdown(
        "**Structure:**\n\n"
        "- **Do** I/you/we/they + base verb → *Do you work on Sunday?*\n"
        "- **Does** he/she/it + base verb → *Does she play tennis?*\n\n"
        "**Short answers:**\n"
        "- Yes, I do. / No, I don’t.\n"
        "- Yes, she does. / No, she doesn’t."
    )

    st.markdown("### ✍️ Controlled practice – Make questions")
    st.markdown(
        "Write questions using **do/does**.\n\n"
        "1. you / watch TV / in the evening?\n"
        "2. your friends / play football / at the weekend?\n"
        "3. your teacher / give / a lot of homework?\n"
        "4. your family / go out / on Sundays?\n"
        "5. your best friend / like / coffee?"
    )

    st.markdown("### 🧩 Vocabulary – Free-time activities")
    st.markdown(
        "- watch series / movies\n"
        "- go to the cinema\n"
        "- read books / magazines\n"
        "- listen to music / podcasts\n"
        "- go for a walk\n"
        "- play sports (football, basketball, volleyball, etc.)\n"
        "- meet friends\n"
        "- play video games"
    )

    st.markdown("### ✍️ Guided writing – Survey questions")
    st.write("Write **5 questions** about free time to ask your classmates.")
    st.info(
        'Example: *"Do you usually watch TV at night?"* / *"Does your best friend play any sport?"*'
    )


def render_unit2_session2_hour2():
    st.subheader("Unit 2 – Session 2 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Free time (listening & survey)")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand people talking about free-time activities.\n"
        "- Practise questions with **do/does**.\n"
        "- Create and present a simple class survey."
    )

    st.markdown("### 🔊 Listening 1 – Free time intro")
    _audio_or_warning("U2_S2_audio1_intro.mp3")
    st.caption(
        "Intro to free-time activities and what students will do in the session."
    )

    st.markdown("### 🔊 Listening 2 – Three people and their free time")
    _audio_or_warning("U2_S2_audio2_three_people.mp3")
    st.write("Listen and answer:")
    st.markdown(
        "1. What does **Person A** do in their free time?\n"
        "2. What does **Person B** usually do at the weekend?\n"
        "3. Does **Person C** like staying at home or going out?"
    )

    st.markdown("### 🔊 Listening 3 – Questions & short answers")
    _audio_or_warning("U2_S2_audio3_questions_answers.mp3")
    st.markdown(
        "Listen to the questions and short answers and repeat:\n\n"
        "- *Do you watch TV every day?* – *Yes, I do. / No, I don’t.*\n"
        "- *Does she go to the gym?* – *Yes, she does. / No, she doesn’t.*"
    )

    st.markdown("### 👥 Pair work – Mini survey")
    st.write(
        "Use your **5 questions** from the first hour. Ask **3 classmates** and note their answers."
    )
    st.markdown(
        "Then prepare **2–3 sentences** about the results, for example:\n"
        "- *Most people watch TV in the evening.*\n"
        "- *Two people don’t like going out at night.*"
    )

    st.markdown("### 🗣️ Speaking – Report your results")
    st.write("Share your results with the class using present simple:")
    st.info(
        '"In our group, three people play sports at the weekend and two people '
        'hardly ever watch TV."'
    )


# ==========================
# UNIT 2 – SESSION 3
# ==========================

def render_unit2_session3_hour1():
    st.subheader("Unit 2 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Habits & lifestyle")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Review **present simple** and frequency expressions.\n"
        "- Use simple connectors: **and, but, because**.\n"
        "- Write a short paragraph about your lifestyle."
    )

    st.markdown("### ✏️ Warm-up – Healthy or unhealthy?")
    st.write("Think about your lifestyle.")
    st.markdown(
        "- Do you sleep enough?\n"
        "- Do you eat healthy food?\n"
        "- Do you do any exercise?"
    )

    st.markdown("### 🧩 Grammar – Connectors")
    st.markdown(
        "- **and** → to add information: *I drink coffee **and** tea.*\n"
        "- **but** → to contrast: *I like sweets, **but** I don’t like chocolate.*\n"
        "- **because** → to give a reason: *I go to bed early **because** I work a lot.*"
    )

    st.markdown("### ✍️ Controlled practice – Complete the sentences")
    st.markdown(
        "1. I eat fruit in the morning ______ I drink water.\n\n"
        "2. I like watching series, ______ I don’t have much time.\n\n"
        "3. I go for a walk every day ______ it helps me relax.\n\n"
        "4. I usually sleep 7 hours, ______ sometimes I go to bed late."
    )

    st.markdown("### 🧩 Frequency expressions for lifestyle")
    st.markdown(
        "- every day\n"
        "- once a week / twice a week\n"
        "- three times a week\n"
        "- at the weekend\n"
        "- on weekdays\n"
        "- in the morning / in the evening"
    )

    st.markdown("### ✍️ Guided writing – My lifestyle")
    st.info(
        '"I usually get up early on weekdays because I work in the morning.\n'
        'I drink coffee and I sometimes eat fruit for breakfast.\n'
        'I don’t do a lot of exercise, but I walk to work every day.\n'
        'At the weekend I relax and spend time with my family."'
    )
    st.write(
        "Write **6–8 sentences** about your lifestyle. Use **present simple, frequency expressions "
        "and connectors (and, but, because)**."
    )


def render_unit2_session3_hour2():
    st.subheader("Unit 2 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Habits & lifestyle (listening & speaking)")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short texts about healthy and unhealthy lifestyles.\n"
        "- Discuss your own habits.\n"
        "- Give simple advice using **should / shouldn’t** (light review)."
    )

    st.markdown("### 🔊 Listening 1 – Two lifestyles")
    _audio_or_warning("U2_S3_audio1_two_lifestyles.mp3")
    st.markdown(
        "Listen to **Person A** and **Person B** and decide:\n\n"
        "- Who has a **healthier** lifestyle?\n"
        "- Why?"
    )

    st.markdown("### 🔊 Listening 2 – Details")
    _audio_or_warning("U2_S3_audio2_details.mp3")
    st.markdown(
        "Answer the questions:\n\n"
        "1. How many hours does Person A sleep?\n"
        "2. What does Person B usually eat for breakfast?\n"
        "3. How often does Person A do exercise?\n"
        "4. What does Person B do at the weekend?"
    )

    st.markdown("### 🧩 Quick review – Should / shouldn’t")
    st.markdown(
        "- You **should** sleep 7–8 hours.\n"
        "- You **shouldn’t** eat fast food every day."
    )

    st.markdown("### 🗣️ Pair work – Talk about your lifestyle")
    st.markdown(
        "In pairs, ask and answer:\n\n"
        "- How many hours do you sleep?\n"
        "- What do you usually eat for breakfast?\n"
        "- Do you do any exercise? How often?\n"
        "- What healthy habits do you have?\n"
        "- What unhealthy habits do you have?"
    )

    st.markdown("### 🗣️ Speaking – Give advice")
    st.write("Give **two pieces of advice** to your partner using **should / shouldn’t**.")
    st.info(
        '"You should drink more water." / "You shouldn’t work so late at night."'
    )


# ==========================
# PAGES
# ==========================

def overview_page():
    show_logo()
    st.title("📘 A2 English Master – Elementary Course")

    st.markdown(
        """
### Learn to communicate with confidence in real situations

This A2 English program is designed for learners who want *clear progress*, 
practical language and a professional learning experience.

**With this course your students will:**
- Speak about their life, work, studies and travel plans in clear, simple English.  
- Understand real conversations at normal speed in common situations.  
- Write short emails, messages and descriptions with correct grammar.  
- Build a solid base to move confidently to **B1 – Intermediate**.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🎯 For whom?")
        st.write(
            "- Adults and young adults\n"
            "- Tourism, service and business professionals\n"
            "- Learners who finished A1 and want the next step"
        )

    with col2:
        st.subheader("📚 What’s inside?")
        st.write(
            "- 10 carefully structured units\n"
            "- Clear grammar and vocabulary focus\n"
            "- Step-by-step lessons with theory, practice and insights\n"
            "- Progress checks and final assessment"
        )

    with col3:
        st.subheader("🌍 Why this course?")
        st.write(
            "- Based on Cambridge Empower A2 (Second Edition)\n"
            "- Strong focus on speaking and listening\n"
            "- Real-world topics: travel, work, culture and health\n"
            "- Designed by Iván Díaz, Tourist Guide & English Instructor"
        )

    st.markdown("---")
    st.markdown("#### Quick course facts")

    facts_df = pd.DataFrame(
        [
            ["Level", COURSE_INFO["level"]],
            ["Total units", COURSE_INFO["units"]],
            ["Suggested total hours", COURSE_INFO["total_hours"]],
            ["Hours per unit (average)", COURSE_INFO["hours_per_unit"]],
        ],
        columns=["Item", "Details"],
    )
    facts_df["Details"] = facts_df["Details"].astype(str)
    st.table(facts_df)

    st.markdown("### 🚀 Ready to start?")
    if st.button("Start your first class", use_container_width=True):
        go_to_page("Enter your class")

    with st.expander("View Spanish summary / Ver resumen en español"):
        st.write(
            """
Este curso A2 está pensado para que los estudiantes hablen de su vida diaria, trabajo y viajes 
en un inglés claro y funcional. Integra el libro Cambridge Empower A2 y lo adapta a contextos 
reales, especialmente útiles para turismo y servicios.
            """
        )


def levels_page():
    show_logo()
    st.title("🎯 English Levels (CEFR)")

    data = [
        ["A1", "Beginner", "Can use very basic everyday expressions, introduce themselves and ask/answer simple questions."],
        ["A2", "Elementary", "Can talk about daily routines, family, simple work, shopping and immediate needs in simple terms."],
        ["B1", "Intermediate", "Can deal with most situations while travelling, describe experiences and give simple opinions."],
        ["B2", "Upper-Intermediate", "Can interact with a good degree of fluency and understand the main ideas of complex texts."],
        ["C1", "Advanced", "Can express ideas fluently and spontaneously for academic and professional purposes."],
        ["C2", "Proficiency", "Can understand practically everything and express themselves with precision in almost any context."]
    ]
    df = pd.DataFrame(data, columns=["Level", "Name", "Description"])
    st.table(df)

    st.markdown("---")
    st.markdown("### 🟦 Where does this course fit?")
    st.success(
        "This program corresponds to **A2 – Elementary**.\n\n"
        "- It consolidates basic A1 structures.\n"
        "- It expands vocabulary for daily life, work and travel.\n"
        "- It prepares learners to move into **B1 – Intermediate** with confidence."
    )


def lessons_page():
    show_logo()
    st.title("📖 Enter your class")

    unit_options = [f"Unit {u['number']} – {u['name']}" for u in UNITS]
    unit_choice = st.selectbox("Choose your unit", unit_options)
    unit_number = UNITS[unit_options.index(unit_choice)]["number"]

    lessons = LESSONS.get(unit_number, [])
    if not lessons:
        st.info("No lessons defined for this unit yet.")
        return

    lesson_titles = [l["title"] for l in lessons]
    lesson_choice = st.selectbox("Choose your lesson", lesson_titles)

    lesson = next(l for l in lessons if l["title"] == lesson_choice)

    st.markdown(f"## {lesson['title']}")
    st.caption(f"Unit {unit_number} – {UNITS[unit_number - 1]['name']}")

    tab_theory, tab_practice, tab_insights = st.tabs(["📘 Theory", "📝 Practice", "💡 Insights"])

    with tab_theory:
        st.markdown("### Key theory")
        for item in lesson["theory"]:
            st.markdown(f"- {item}")

    with tab_practice:
        st.markdown("### Suggested activities")
        for item in lesson["practice"]:
            st.markdown(f"- {item}")
        st.info("You can adapt these activities to face-to-face classes, online sessions or autonomous work.")

    with tab_insights:
        st.markdown("### Teaching & learning insights")
        for item in lesson["insights"]:
            st.markdown(f"- {item}")
        st.success("Use this space to add your own notes, examples or anecdotes for each group.")

    # --- SPECIAL BLOCKS: UNIT 1 – CLASS 1, 2, 3 (Sessions with app + slideshow) ---
    if unit_number == 1 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 1 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit1_session1_hour1()
            else:
                render_unit1_session1_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit1_session1_hour1.html")
            else:
                render_presentation_html("unit1_session1_hour2.html")

    elif unit_number == 1 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 2 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit1_session2_hour1()
            else:
                render_unit1_session2_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit1_session2_hour1.html")
            else:
                render_presentation_html("unit1_session2_hour2.html")

    elif unit_number == 1 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 3 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit1_session3_hour1()
            else:
                render_unit1_session3_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit1_session3_hour1.html")
            else:
                render_presentation_html("unit1_session3_hour2.html")

    # --- SPECIAL BLOCKS: UNIT 2 – CLASS 1, 2, 3 ---
    elif unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session1_hour1()
            else:
                render_unit2_session1_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit2_session1_hour1.html")
            else:
                render_presentation_html("unit2_session1_hour2.html")

    elif unit_number == 2 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 2 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session2_hour1()
            else:
                render_unit2_session2_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit2_session2_hour1.html")
            else:
                render_presentation_html("unit2_session2_hour2.html")

    elif unit_number == 2 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 3 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True
        )

        if view_mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session3_hour1()
            else:
                render_unit2_session3_hour2()
        else:
            if hour.startswith("1st"):
                render_presentation_html("unit2_session3_hour1.html")
            else:
                render_presentation_html("unit2_session3_hour2.html")


def assessment_page():
    show_logo()
    st.title("📝 Assessment & Progress")

    st.markdown("### Assessment structure")
    st.markdown(
        """
- Unit progress checks every **two units**  
- **Mid-course assessment** (after Unit 5): listening, reading, writing & speaking  
- **Final exam** (after Unit 10): full integrated assessment  
"""
    )

    st.markdown("### Suggested weighting")
    df = pd.DataFrame(
        [
            ["Class participation & homework", "20%"],
            ["Progress checks", "30%"],
            ["Mid-course test", "20%"],
            ["Final exam", "30%"],
        ],
        columns=["Component", "Weight"]
    )
    st.table(df)


def instructor_page():
    show_logo()
    st.title("👨‍🏫 Instructor")

    st.markdown(
        """
**Instructor:** Iván de Jesús Díaz Navarro  
**Profile:** Certified Tourist Guide & English Instructor  

This A2 English Master program connects communicative English teaching with real-life 
contexts, especially tourism, culture and professional interaction.  

Learners not only study grammar and vocabulary – they practise situations they can 
actually experience in their daily life and work.
        """
    )

    st.markdown("### Signature")
    show_signature()


# ==========================
# ACCESS (LOGIN / REGISTER / ADMIN CODE)
# ==========================

def access_page():
    show_logo()
    st.title("🔐 Access · Login & Registration")
    st.caption("Acceso para estudiantes y panel de administrador (con código).")

    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        tab_login, tab_register, tab_admin = st.tabs(
            ["Student login", "Student registration", "Admin access"]
        )

        # --- Student login ---
        with tab_login:
            st.subheader("Student login")
            st.write("Log in to quickly open your classes from this device.")

            with st.form("login_form"):
                email = st.text_input("Email")
                name = st.text_input("Name (optional)")
                password = st.text_input("Password", type="password")
                login_submit = st.form_submit_button("Log in")

            if login_submit:
                if email and password:
                    st.session_state["is_authenticated"] = True
                    st.session_state["user_role"] = "student"
                    st.session_state["user_name"] = name or email
                    st.success(f"Welcome, {st.session_state['user_name']}! ✅")
                    if st.button("Go to your classes →", key="go_classes_from_login"):
                        go_to_page("Enter your class")
                else:
                    st.error("Please enter at least your email and password.")

        # --- Student registration ---
        with tab_register:
            st.subheader("Student registration")
            st.write(
                "Create a simple profile to start using the platform. "
                "(Prototype – data is stored only in this session)."
            )

            with st.form("register_form"):
                reg_name = st.text_input("Full name")
                reg_email = st.text_input("Email")
                reg_level = st.selectbox(
                    "Current English level",
                    ["A1", "A2", "B1", "B2", "I’m not sure"]
                )
                reg_submit = st.form_submit_button("Register")

            if reg_submit:
                if reg_name and reg_email:
                    st.session_state["last_registered_user"] = {
                        "name": reg_name,
                        "email": reg_email,
                        "level": reg_level,
                    }
                    st.success(f"Registration saved for {reg_name}. 🎉")
                    st.info(
                        "In a future version this will connect to your database or Google Sheets."
                    )
                else:
                    st.error("Please complete at least name and email.")

        # --- Admin access ---
        with tab_admin:
            st.subheader("Admin access")
            st.write("Enter with the secret admin code to open the control panel.")

            with st.form("admin_form"):
                code = st.text_input("Admin access code", type="password")
                admin_submit = st.form_submit_button("Access as admin")

            if admin_submit:
                if code == ADMIN_ACCESS_CODE:
                    st.session_state["is_authenticated"] = True
                    st.session_state["user_role"] = "admin"
                    st.session_state["user_name"] = "Administrator"
                    st.success("Admin access granted. ⚙️")
                    if st.button("Open admin panel →", key="go_admin_from_access"):
                        go_to_page("Admin")
                else:
                    st.error("Incorrect code. Please try again.")

    with col_right:
        st.markdown("### 👀 What can you do here?")
        st.markdown(
            """
- Save a basic student profile on this device  
- Quickly open your classes after login  
- Enter the **admin panel** with a secret code  
            """
        )

        if st.session_state.get("is_authenticated"):
            st.success(
                f"Current session: {st.session_state.get('user_name', 'user')} "
                f"({st.session_state.get('user_role', 'student')})"
            )
            if st.button("Log out", key="logout_button"):
                st.session_state.clear()
                _rerun()
        else:
            st.info("You are not logged in yet.")


# ==========================
# ADMIN PANEL (CODE ONLY)
# ==========================

def admin_page():
    show_logo()
    st.title("⚙️ Admin panel")

    role = st.session_state.get("user_role", "guest")
    if role != "admin":
        st.error("Admin code required. Please go to the Access page and enter the admin code.")
        if st.button("Go to Access page"):
            go_to_page("Access")
        return

    st.success("Admin mode active. Welcome.")

    st.markdown("### Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active students", "—")
    with col2:
        st.metric("Units available", len(UNITS))
    with col3:
        st.metric("Created today", "—")

    st.markdown("### Next steps for this panel")
    st.markdown(
        """
In future iterations, this admin area can include:

- Student list and individual progress  
- Automatic certificate generation  
- Control of audio files and presentations  
- Configuration of access codes and groups  
        """
    )


# ==========================
# PAGE ROUTER
# ==========================

def render_page(page_id: str):
    if page_id == "Overview":
        overview_page()
    elif page_id == "English Levels":
        levels_page()
    elif page_id == "Assessment & Progress":
        assessment_page()
    elif page_id == "Instructor":
        instructor_page()
    elif page_id == "Enter your class":
        lessons_page()
    elif page_id == "Access":
        access_page()
    elif page_id == "Admin":
        admin_page()
    else:
        overview_page()


# ==========================
# MAIN
# ==========================

def main():
    inject_global_css()
    current_page = get_current_page_id()
    render_page(current_page)
    render_floating_menu(current_page)

if __name__ == "__main__":
    main()
