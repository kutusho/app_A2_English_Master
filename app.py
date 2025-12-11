import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit.components.v1 as components  # Para embeber las presentaciones HTML
import datetime as dt
import csv
import textwrap

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
RESPONSES_DIR = BASE_DIR / "responses"
RESPONSES_DIR.mkdir(exist_ok=True)
RESPONSES_FILE = RESPONSES_DIR / "unit2_responses.csv"

# ==========================
# ADMIN / AUTH CONFIG
# ==========================
ADMIN_ACCESS_CODE = os.getenv("ENGLISH_MASTER_ADMIN_CODE", "A2-ADMIN-2025")


def init_session():
    if "auth" not in st.session_state:
        st.session_state["auth"] = {
            "logged_in": False,
            "role": "guest",   # guest | student | admin
            "name": "",
            "email": "",
        }


def get_current_user():
    auth = st.session_state.get("auth", {})
    return (
        auth.get("name", ""),
        auth.get("email", ""),
        auth.get("role", "guest"),
    )


def save_unit2_response(user_email, user_name, session, hour, exercise_id, text):
    """
    Guarda una respuesta de la Unidad 2 en responses/unit2_responses.csv
    session: 'S1' | 'S2' | 'S3'
    hour: 'H1' | 'H2'
    exercise_id: string corto tipo 'grammar', 'writing', etc.
    """
    RESPONSES_DIR.mkdir(exist_ok=True)
    row = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "user_email": user_email or "",
        "user_name": user_name or "",
        "unit": 2,
        "session": session,
        "hour": hour,
        "exercise_id": exercise_id,
        "response": (text or "").replace("\n", "\\n"),
    }
    try:
        file_exists = RESPONSES_FILE.exists()
        with open(RESPONSES_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        return True, "Answer saved."
    except Exception as e:
        return False, f"Error saving answer: {e}"


def unit2_answer_box(session, hour, exercise_id, label, height=180):
    """
    Pequeño componente reutilizable:
    - Muestra un text_area
    - Botón para guardar
    - Guarda respuesta ligada a usuario (si está logueado)
    """
    name, email, role = get_current_user()
    key_text = f"u2_{session}_{hour}_{exercise_id}"

    st.markdown(f"#### ✏️ Your answer – {label}")
    text = st.text_area(
        "Write here",
        key=key_text,
        height=height,
        label_visibility="collapsed",
    )

    if st.button("💾 Save this answer", key=f"save_{key_text}"):
        if not email:
            st.warning(
                "Please go to **Access → Student access** and login with your email "
                "so your answers are linked to your name."
            )
        ok, msg = save_unit2_response(
            user_email=email,
            user_name=name,
            session=session,
            hour=hour,
            exercise_id=exercise_id,
            text=text,
        )
        if ok:
            st.success("✅ Answer saved correctly.")
        else:
            st.error(msg)


# ==========================
# GLOBAL STYLES (BRANDING + DARK MODE FRIENDLY)
# ==========================

def inject_global_css():
    st.markdown(
        """
<style>
.floating-menu-wrapper {
    position: fixed;
    top: 4.5rem;
    left: 1.4rem;
    z-index: 2000;
}

/* Escondemos el checkbox */
.floating-menu-toggle {
    display: none;
}

/* Botón redondo "Menu" */
.floating-menu-button {
    background: linear-gradient(135deg, #1f4b99, #274b8f);
    color: #ffffff;
    border-radius: 999px;
    padding: 0.55rem 1.4rem;
    font-size: 0.95rem;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    border: none;
    display: inline-flex;
    align-items: center;
}

/* Panel flotante */
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

/* Mostrar el menú cuando el checkbox está activado */
.floating-menu-toggle:checked ~ .floating-menu-panel {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0);
}

/* Cabecera del panel */
.floating-menu-header {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
    color: #4b5563;
}

/* Enlaces del menú (<a>) */
.menu-link-btn {
    width: 100%;
    display: block;
    text-align: left;
    padding: 0.5rem 0.7rem;
    border-radius: 0.55rem;
    border: none;
    background: transparent;
    cursor: pointer;
    color: #111827;
    font-size: 0.9rem;
    text-decoration: none;
}

.menu-link-btn:hover {
    background-color: #f1f4fb;
}

.menu-link-btn.active {
    background-color: #1f4b99;
    color: white;
    font-weight: 600;
}

/* Modo oscuro del sistema */
@media (prefers-color-scheme: dark) {
    .floating-menu-panel {
        background-color: #020617;
    }
    .floating-menu-header {
        color: #9ca3af;
    }
    .menu-link-btn {
        color: #e5e7eb;
    }
    .menu-link-btn:hover {
        background-color: #0f172a;
    }
    .menu-link-btn.active {
        background-color: #1d4ed8;
    }
}
</style>
        """,
        unsafe_allow_html=True
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
    {"id": "Teacher Panel", "label": "Teacher", "icon": "📂"},
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
    # Construcción de items usando <form method="get"> (sin JS, sin <a>)
    items_html = ""
    for page in PAGES:
        page_id = page["id"]
        label = page["label"]
        icon = page["icon"]

        is_active = (page_id == current_page_id)
        active_class = "active" if is_active else ""

        # Cada item es un formulario GET que envía ?page=<page_id>
        items_html += f"""
<form method="get" style="margin:0; padding:0;">
  <input type="hidden" name="page" value="{page_id}">
  <button type="submit" class="menu-link-btn {active_class}">
    {icon} {label}
  </button>
</form>
"""

    # Contenedor principal
    menu_html = textwrap.dedent(f"""
<div class="floating-menu-wrapper">
  <input type="checkbox" id="floating-menu-toggle" class="floating-menu-toggle" />
  
  <label for="floating-menu-toggle" class="floating-menu-button">
    ☰ Menu
  </label>

  <div class="floating-menu-panel">
    <div class="floating-menu-header">Navigate</div>
    {items_html}
  </div>
</div>
""")

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
# UNIT 2 – SESSIONS
# (Unidad 1 la conservas como ya la tenías si la usas)
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
        "\"On weekdays I usually get up at 6:30. I have coffee and bread, then I go to work.\n"
        "I start work at 8:00 and finish at 4:00. After work I sometimes go to the gym\n"
        "or I meet my friends. I never go to bed late on Monday to Friday.\""
    )

    st.write("Now write **5–7 sentences** about your typical day. Use:")
    st.markdown(
        "- Present simple (get up, start, finish, go, have…)\n"
        "- At least **3 adverbs of frequency**."
    )

    st.markdown("---")
    unit2_answer_box("S1", "H1", "practice", "Grammar & practice answers")
    unit2_answer_box("S1", "H1", "writing", "My typical day – paragraph")


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

    st.markdown("---")
    unit2_answer_box("S1", "H2", "listening_notes", "Listening notes and answers")
    unit2_answer_box("S1", "H2", "speaking", "Speaking – My day (notes)")


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

    st.markdown("---")
    unit2_answer_box("S2", "H1", "questions", "Your free-time questions")
    unit2_answer_box("S2", "H1", "notes", "Notes / extra examples")


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

    st.markdown("---")
    unit2_answer_box("S2", "H2", "survey_notes", "Survey results – notes")
    unit2_answer_box("S2", "H2", "summary", "Final summary to present")


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
        "\"I usually get up early on weekdays because I work in the morning.\n"
        "I drink coffee and I sometimes eat fruit for breakfast.\n"
        "I don’t do a lot of exercise, but I walk to work every day.\n"
        "At the weekend I relax and spend time with my family.\""
    )
    st.write(
        "Write **6–8 sentences** about your lifestyle. Use **present simple, frequency expressions "
        "and connectors (and, but, because)**."
    )

    st.markdown("---")
    unit2_answer_box("S3", "H1", "connectors", "Connector practice – sentences")
    unit2_answer_box("S3", "H1", "lifestyle", "My lifestyle – paragraph")


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

<<<<<<< HEAD
# ==========================
# UNIT 3 – FOOD
# CLASS 1 – FOOD VOCABULARY
# ==========================

def unit3_class1_food_vocabulary():
    """
    A2 – Unit 3: Food · Class 1 – Food vocabulary
    Suggested audio files:
      - AUDIO_DIR / "U3_C1_audio1_food_words.mp3"        # vocab + pronunciation
      - AUDIO_DIR / "U3_C1_audio2_at_the_supermarket.mp3"  # short dialogue
    """

    st.title("Unit 3 – Food")
    st.subheader("Class 1 – Food vocabulary")
    st.caption("A2 English Master · Flunex")

    # --------------------------
    # LEARNING GOALS
    # --------------------------
    with st.expander("🎯 Learning goals for this class"):
        st.markdown(
            """
By the end of this class, you will be able to:

- Recognise and use basic **food vocabulary** (fruits, vegetables, drinks, meals).  
- Talk about what you **like** and **don’t like** eating and drinking.  
- Understand a short **listening** about shopping for food.  
- Practice simple **speaking** about food preferences.
            """
        )

    # --------------------------
    # MAIN TABS
    # --------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Warm-up", "Vocabulary", "Pronunciation", "Practice", "Listening", "Speaking & Wrap-up"]
    )

    # ============= TAB 1: WARM-UP =============
    with tab1:
        st.subheader("1. Warm-up – What do you eat?")

        st.markdown(
            """
Answer these questions in English:

- What do you usually eat for **breakfast**?  
- What do you usually eat for **lunch**?  
- What do you usually eat for **dinner**?  

Write short sentences:
            """
        )

        warmup_text = st.text_area(
            "Write your answers here:",
            placeholder="Example: For breakfast I usually eat eggs and tortillas. For lunch I eat chicken and rice..."
        )

        st.markdown("---")
        st.markdown("Now, look at the list and think: **Which foods do you like? Which foods don’t you like?**")

        foods_like = st.multiselect(
            "Tick the foods you like:",
            [
                "apples", "bananas", "oranges", "grapes",
                "tomatoes", "carrots", "lettuce", "onions",
                "chicken", "fish", "rice", "pasta",
                "water", "juice", "coffee", "tea"
            ]
        )

        if foods_like:
            st.info("Good! Now try to say: **I like... / I don’t like...** using your list.")

    # ============= TAB 2: VOCABULARY =============
    with tab2:
        st.subheader("2. Vocabulary – Food words")

        st.markdown("### 2.1 Food groups")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
**Fruits**

- apple  
- banana  
- orange  
- grape  
- pineapple  
- mango  
                """
            )

        with col2:
            st.markdown(
                """
**Vegetables**

- tomato  
- carrot  
- onion  
- lettuce  
- potato  
- cucumber  
                """
            )

        with col3:
            st.markdown(
                """
**Drinks**

- water  
- juice  
- soda  
- coffee  
- tea  
- milk  
                """
            )

        with col4:
            st.markdown(
                """
**Other food**

- bread  
- rice  
- pasta  
- eggs  
- cheese  
- chicken  
- fish  
                """
            )

        st.markdown("---")
        st.markdown("### 2.2 Check meaning")

        q_vocab = st.selectbox(
            "Which word is a **drink**?",
            ["apple", "bread", "juice", "carrot"]
        )

        if q_vocab:
            if q_vocab == "juice":
                st.success("Correct ✅. **Juice** is a drink.")
            else:
                st.warning("Not exactly. The drink is **juice**.")

        st.markdown("---")
        st.markdown("### 2.3 Mini matching activity (mental)")

        st.markdown(
            """
Match the pairs in your mind:

- milk → drink / fruit?  
- carrot → drink / vegetable?  
- rice → fruit / other food?  

Then say the answers:  
**Milk is a drink. Carrot is a vegetable. Rice is food.**
            """
        )

    # ============= TAB 3: PRONUNCIATION =============
    with tab3:
        st.subheader("3. Pronunciation – Listen and repeat")

        st.markdown(
            """
### 3.1 Listen to the food words

First, listen to the pronunciation and repeat out loud.
            """
        )

        audio1_path = AUDIO_DIR / "U3_C1_audio1_food_words.mp3"
        st.audio(str(audio1_path))

        st.markdown(
            """
Repeat these groups of words:

- **Fruits:** apple, banana, orange, mango  
- **Vegetables:** tomato, carrot, potato, onion  
- **Drinks:** water, coffee, juice, tea  

Focus on **word stress**:  
- **OR**-ange, **TO**-mato, ba-**NA**-na
            """
        )

        st.markdown("---")
        st.markdown("### 3.2 Sound check")

        difficult_word = st.text_input(
            "Write one word that is difficult to pronounce for you:",
            placeholder="Example: vegetable"
        )

        if difficult_word:
            st.info("Good! Practice that word 5 times: slowly, clearly and with correct stress.")

    # ============= TAB 4: PRACTICE =============
    with tab4:
        st.subheader("4. Practice – Food and likes/dislikes")

        st.markdown("### 4.1 Complete the sentences")

        p1 = st.text_input("1) I like ______ (fruit).")
        p2 = st.text_input("2) I don’t like ______ (vegetable).")
        p3 = st.text_input("3) I usually drink ______ for breakfast.")
        p4 = st.text_input("4) For lunch I eat ______ and ______.")
        p5 = st.text_input("5) My favourite drink is ______.")

        if st.button("Show sample answers – Practice"):
            st.markdown(
                """
**Sample answers (just examples):**

1) I like **mango**.  
2) I don’t like **onions**.  
3) I usually drink **coffee** for breakfast.  
4) For lunch I eat **chicken** and **rice**.  
5) My favourite drink is **orange juice**.
                """
            )

        st.markdown("---")
        st.markdown("### 4.2 Choose the correct option")

        mc1 = st.radio(
            "A: Are you thirsty?\nB: Yes, I want a...",
            ["apple", "water", "carrot"],
            index=1
        )

        mc2 = st.radio(
            "Which is a **vegetable**?",
            ["tea", "banana", "tomato"],
            index=2
        )

        if st.button("Check answers – Multiple choice"):
            st.info("Suggested answers: 1) **water**  2) **tomato**")

    # ============= TAB 5: LISTENING =============
    with tab5:
        st.subheader("5. Listening – At the supermarket")

        st.markdown(
            """
### 5.1 First listening – Just listen

Listen to a short dialogue in a supermarket.

> Audio 2: *At the supermarket*

Then answer the questions.
            """
        )

        audio2_path = AUDIO_DIR / "U3_C1_audio2_at_the_supermarket.mp3"
        st.audio(str(audio2_path))

        st.markdown("### 5.2 Comprehension questions")

        l1 = st.radio(
            "1) What does the woman want?",
            [
                "Some apples and bananas",
                "Bread and milk",
                "Chicken and fish"
            ]
        )

        l2 = st.radio(
            "2) What drink do they buy?",
            [
                "Water",
                "Orange juice",
                "Coffee"
            ]
        )

        if st.button("Check answers – Listening"):
            st.info(
                "Suggested key (adapt to your final script):\n\n"
                "1) ✅ Some apples and bananas\n"
                "2) ✅ Orange juice"
            )

        st.markdown("---")
        st.markdown("### 5.3 Write 2–3 sentences about your shopping list")

        shopping_text = st.text_area(
            "Example: Today I want to buy rice, tomatoes, chicken and water.",
            key="u3c1_shopping_list"
        )

    # ============= TAB 6: SPEAKING & WRAP-UP =============
    with tab6:
        st.subheader("6. Speaking & Wrap-up")

        st.markdown(
            """
### 6.1 Speaking prompts

Use these questions with a partner or record yourself:

1. What is your favourite food?  
2. What food don’t you like?  
3. What do you usually eat for breakfast / lunch / dinner?  
4. What healthy food do you eat every week?  

### 6.2 Reflection

Complete:

- Today I learned new **food words** like...  
- Now I can **talk about food I like and don’t like**.  
- One sentence I remember from this class is...
            """
        )

        reflection = st.text_area(
            "Write your reflection here:",
            key="u3c1_reflection"
        )

        st.success("Great job! 🥗 Keep using this food vocabulary in real life.")
=======
    st.markdown("---")
    unit2_answer_box("S3", "H2", "listening", "Listening answers / notes")
    unit2_answer_box("S3", "H2", "advice", "Advice for a healthier lifestyle")

>>>>>>> c2ae00b5a4cdebe7e12c7dd02a09b550bc84f632

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

    # --- UNIT 2 special interactive blocks with saving answers ---
    if unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        if hour.startswith("1st"):
            render_unit2_session1_hour1()
        else:
            render_unit2_session1_hour2()

    elif unit_number == 2 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 2 · Mobile class")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        if hour.startswith("1st"):
            render_unit2_session2_hour1()
        else:
            render_unit2_session2_hour2()

    elif unit_number == 2 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 3 · Mobile class")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True
        )

        if hour.startswith("1st"):
            render_unit2_session3_hour1()
        else:
            render_unit2_session3_hour2()


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


def access_page():
    show_logo()
    st.title("🔐 Access")

    tabs = st.tabs(["Student access", "Admin access"])

    # ---- Student ----
    with tabs[0]:
        st.subheader("Student – Login or register")

        mode = st.radio("Choose an option", ["Login", "Register"], horizontal=True)

        if mode == "Login":
            email = st.text_input("Email", key="login_email")
            name = st.text_input("Your name (optional)", key="login_name")
            if st.button("Login", key="login_btn"):
                if email:
                    st.session_state["auth"]["logged_in"] = True
                    st.session_state["auth"]["role"] = "student"
                    st.session_state["auth"]["email"] = email
                    st.session_state["auth"]["name"] = name or email
                    st.success(f"Welcome, {st.session_state['auth']['name']}!")
                else:
                    st.error("Please write your email.")
        else:
            name = st.text_input("Full name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            goal = st.text_area("Why are you studying English? (optional)", key="reg_goal")
            if st.button("Create account & login", key="reg_btn"):
                if name and email:
                    st.session_state["auth"]["logged_in"] = True
                    st.session_state["auth"]["role"] = "student"
                    st.session_state["auth"]["email"] = email
                    st.session_state["auth"]["name"] = name
                    st.success(f"Welcome, {name}! Your account is active in this device.")
                else:
                    st.error("Please write at least your name and email.")

        if st.session_state["auth"]["logged_in"]:
            st.info(
                f"Current user: **{st.session_state['auth']['name']}** "
                f"({st.session_state['auth']['email']})"
            )
            if st.button("Logout", key="logout_btn"):
                st.session_state["auth"] = {
                    "logged_in": False,
                    "role": "guest",
                    "name": "",
                    "email": "",
                }
                st.success("Logged out.")

    # ---- Admin ----
    with tabs[1]:
        st.subheader("Admin access")
        st.write("Only for teacher / administrator.")

        code = st.text_input("Admin access code", type="password", key="admin_code")
        if st.button("Enter as admin", key="admin_btn"):
            if code == ADMIN_ACCESS_CODE:
                st.session_state["auth"]["logged_in"] = True
                st.session_state["auth"]["role"] = "admin"
                st.session_state["auth"]["name"] = "Admin"
                st.session_state["auth"]["email"] = "admin@local"
                st.success("✅ Admin access granted.")
            else:
                st.error("Invalid code")

        if st.session_state["auth"]["role"] == "admin":
            st.success("You are logged in as admin. Go to **Teacher Panel** from the menu.")


def teacher_panel_page():
    show_logo()
    st.title("📂 Teacher Panel – Unit 2 answers")

    name, email, role = get_current_user()
    if role != "admin":
        st.error("This area is only for admin. Please go to **Access → Admin** and enter your code.")
        return

    st.markdown(
        "Here you can review the answers that students saved for **Unit 2**.\n\n"
        "Data is stored in `responses/unit2_responses.csv` on the server."
    )

    if not RESPONSES_FILE.exists():
        st.info("No answers saved yet.")
        return

    try:
        df = pd.read_csv(RESPONSES_FILE)
        if "unit" in df.columns:
            df = df[df["unit"] == 2]
        if df.empty:
            st.info("No answers for Unit 2 yet.")
            return

        df["response"] = df["response"].fillna("").astype(str).str.replace("\\n", "\n")

        st.markdown("### Filters")
        sessions = sorted(df["session"].unique())
        session_choice = st.selectbox("Session", sessions)

        filtered = df[df["session"] == session_choice]

        emails = sorted(filtered["user_email"].unique())
        email_filter = st.multiselect("Filter by student (optional)", emails)

        if email_filter:
            filtered = filtered[filtered["user_email"].isin(email_filter)]

        st.markdown("### Answers")
        st.dataframe(
            filtered.sort_values("timestamp", ascending=False),
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error loading answers: {e}")


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
    elif page_id == "Teacher Panel":
        teacher_panel_page()
    else:
        overview_page()


# ==========================
# MAIN
# ==========================

def main():
    init_session()
    inject_global_css()
    current_page = get_current_page_id()
    render_page(current_page)
    render_floating_menu(current_page)


if __name__ == "__main__":
    main()
