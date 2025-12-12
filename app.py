import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit.components.v1 as components  # Para embeber presentaciones HTML
import datetime as dt
import csv
import textwrap
import requests

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
STATIC_DIR = BASE_DIR / "static"   # Presentaciones HTML
RESPONSES_DIR = BASE_DIR / "responses"
RESPONSES_DIR.mkdir(exist_ok=True)
RESPONSES_FILE = RESPONSES_DIR / "unit2_responses.csv"

# Carpeta para contenido dinámico (scripts, textos, etc.)
CONTENT_DIR = BASE_DIR / "content"
CONTENT_DIR.mkdir(exist_ok=True)

# ==========================
# ADMIN / AUTH CONFIG
# ==========================
ADMIN_ACCESS_CODE = os.getenv("ENGLISH_MASTER_ADMIN_CODE", "A2-ADMIN-2025")

# API ElevenLabs (por si quieres usarla desde la app)
ELEVENLABS_API_KEY = (
    st.secrets.get("ELEVENLABS_API_KEY", "")
    if hasattr(st, "secrets")
    else os.getenv("ELEVENLABS_API_KEY", "")
)


def eleven_generate_audio(text: str, voice_id: str, filename: str, model_id: str = "eleven_multilingual_v2"):
    """
    Llama a ElevenLabs y guarda el audio en /audio/<filename>.
    Se usa de forma opcional desde paneles/admin.
    """
    if not ELEVENLABS_API_KEY:
        st.error("ElevenLabs API key is not configured. Add ELEVENLABS_API_KEY to Streamlit secrets or environment.")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
        },
    }

    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            st.error(f"ElevenLabs error: {resp.status_code} – {resp.text[:200]}")
            return False

        AUDIO_DIR.mkdir(exist_ok=True)
        out_path = AUDIO_DIR / filename
        with open(out_path, "wb") as f:
            f.write(resp.content)

        st.success(f"Audio saved: audio/{filename}")
        return True
    except Exception as e:
        st.error(f"Error calling ElevenLabs: {e}")
        return False


# ==========================
# SESSION / AUTH HELPERS
# ==========================

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


# ==========================
# RESPUESTAS UNIT 2
# ==========================

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
    Componente reutilizable para textos de Unit 2.
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
# CONTENT STORAGE HELPERS
# ==========================

def save_content_block(unit: int, lesson: int, content_key: str, text: str):
    """
    Guarda un bloque de contenido en:
      content/unit<unit>/class<lesson>/<content_key>.txt
    Ejemplo:
      content/unit3/class1/audio_intro.txt
    """
    if not content_key:
        raise ValueError("content_key is required")

    safe_key = "".join(c for c in content_key if c.isalnum() or c in ("_", "-")).strip()
    if not safe_key:
        raise ValueError("content_key is invalid")

    folder = CONTENT_DIR / f"unit{unit}" / f"class{lesson}"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / f"{safe_key}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text or "")

    return file_path


def load_content_block(unit: int, lesson: int, content_key: str) -> str:
    """
    Carga un bloque de contenido. Si no existe, regresa cadena vacía.
    """
    if not content_key:
        return ""

    safe_key = "".join(c for c in content_key if c.isalnum() or c in ("_", "-")).strip()
    if not safe_key:
        return ""

    file_path = CONTENT_DIR / f"unit{unit}" / f"class{lesson}" / f"{safe_key}.txt"
    if not file_path.exists():
        return ""

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ==========================
# GLOBAL STYLES (MENU FLOTANTE)
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
    border: none;
    display: inline-flex;
    align-items: center;
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
.floating-menu-toggle:checked ~ .floating-menu-panel {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(0);
}
.floating-menu-header {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
    color: #4b5563;
}
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
# LESSONS BY UNIT (RESUMEN)
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
    # (El resto de unidades igual que antes, omitidas aquí por espacio;
    # puedes mantener tu propia versión completa si ya la tenías)
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
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
# NAVIGATION (MENU FLOTANTE)
# ==========================

PAGES = [
    {"id": "Overview", "label": "Overview", "icon": "🏠"},
    {"id": "English Levels", "label": "Levels", "icon": "📊"},
    {"id": "Assessment & Progress", "label": "Assessment", "icon": "📝"},
    {"id": "Instructor", "label": "Instructor", "icon": "👨‍🏫"},
    {"id": "Enter your class", "label": "Class", "icon": "🎓"},
    {"id": "Access", "label": "Access", "icon": "🔐"},
    {"id": "Teacher Panel", "label": "Teacher", "icon": "📂"},
    {"id": "Content Admin", "label": "Content admin", "icon": "⚙️"},
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
    items_html = ""
    for page in PAGES:
        page_id = page["id"]
        label = page["label"]
        icon = page["icon"]

        is_active = (page_id == current_page_id)
        active_class = "active" if is_active else ""

        items_html += f"""
<form method="get" style="margin:0; padding:0;">
  <input type="hidden" name="page" value="{page_id}">
  <button type="submit" class="menu-link-btn {active_class}">
    {icon} {label}
  </button>
</form>
"""

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
# HELPERS AUDIO / PRESENTACIONES
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
# UNIT 2 – SESSIONS (resumen)
# ==========================
# (Aquí puedes mantener tus funciones completas; dejo solo una como ejemplo)

def render_unit2_session1_hour1():
    st.subheader("Unit 2 – Session 1 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Daily routines")
    # ... (mantén aquí tu desarrollo completo de la sesión)
    unit2_answer_box("S1", "H1", "practice", "Grammar & practice answers")
    unit2_answer_box("S1", "H1", "writing", "My typical day – paragraph")


def render_unit2_session1_hour2():
    st.subheader("Unit 2 – Session 1 · 2nd Hour – Listening & Speaking")
    # ...
    unit2_answer_box("S1", "H2", "listening_notes", "Listening notes and answers")
    unit2_answer_box("S1", "H2", "speaking", "Speaking – My day (notes)")


# (Igual con render_unit2_session2_hour1/2, render_unit2_session3_hour1/2...)


# ==========================
# UNIT 3 – FOOD · CLASS 1 – MOBILE CLASS
# ==========================

def unit3_class1_food_vocabulary():
    """
    A2 – Unit 3: Food · Class 1 – Food vocabulary
    """
    st.title("Unit 3 – Food")
    st.subheader("Class 1 – Food vocabulary")
    st.caption("A2 English Master · Flunex")

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Warm-up", "Vocabulary", "Pronunciation", "Practice", "Listening", "Speaking & Wrap-up"]
    )

    # TAB 1
    with tab1:
        st.subheader("1. Warm-up – What do you eat?")
        st.markdown(
            """
Answer these questions in English:

- What do you usually eat for **breakfast**?  
- What do you usually eat for **lunch**?  
- What do you usually eat for **dinner**?  
            """
        )
        st.text_area(
            "Write your answers here:",
            placeholder="Example: For breakfast I usually eat eggs and tortillas. For lunch I eat chicken and rice...",
            key="u3c1_warmup",
        )

        st.markdown("---")
        st.markdown("Now, look at the list and think: **Which foods do you like? Which foods don’t you like?**")

        st.multiselect(
            "Tick the foods you like:",
            [
                "apples", "bananas", "oranges", "grapes",
                "tomatoes", "carrots", "lettuce", "onions",
                "chicken", "fish", "rice", "pasta",
                "water", "juice", "coffee", "tea"
            ],
            key="u3c1_like_foods",
        )

    # TAB 2
    with tab2:
        st.subheader("2. Vocabulary – Food words")

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
        q_vocab = st.selectbox(
            "Which word is a **drink**?",
            ["apple", "bread", "juice", "carrot"],
            key="u3c1_drink_question",
        )
        if q_vocab:
            if q_vocab == "juice":
                st.success("Correct ✅. **Juice** is a drink.")
            else:
                st.warning("Not exactly. The drink is **juice**.")

    # TAB 3
    with tab3:
        st.subheader("3. Pronunciation – Listen and repeat")
        st.markdown("First, listen to the pronunciation and repeat out loud.")

        _audio_or_warning("U3_C1_audio1_food_words.mp3")

        st.markdown(
            """
Repeat these groups of words:

- **Fruits:** apple, banana, orange, mango  
- **Vegetables:** tomato, carrot, potato, onion  
- **Drinks:** water, coffee, juice, tea  
            """
        )

    # TAB 4
    with tab4:
        st.subheader("4. Practice – Food and likes/dislikes")
        st.text_input("1) I like ______ (fruit).", key="u3c1_pr1")
        st.text_input("2) I don’t like ______ (vegetable).", key="u3c1_pr2")
        st.text_input("3) I usually drink ______ for breakfast.", key="u3c1_pr3")
        st.text_input("4) For lunch I eat ______ and ______.", key="u3c1_pr4")
        st.text_input("5) My favourite drink is ______.", key="u3c1_pr5")

        if st.button("Show sample answers – Practice", key="u3c1_samples_btn"):
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

    # TAB 5
    with tab5:
        st.subheader("5. Listening – At the supermarket")

        st.markdown("Listen to a short dialogue in a supermarket.")
        _audio_or_warning("U3_C1_audio2_at_the_supermarket.mp3")

        st.markdown("### Comprehension questions")
        st.radio(
            "1) What does the woman want?",
            ["Some apples and bananas", "Bread and milk", "Chicken and fish"],
            key="u3c1_l1",
        )
        st.radio(
            "2) What drink do they buy?",
            ["Water", "Orange juice", "Coffee"],
            key="u3c1_l2",
        )

    # TAB 6
    with tab6:
        st.subheader("6. Speaking & Wrap-up")
        st.markdown(
            """
Use these questions with a partner or record yourself:

1. What is your favourite food?  
2. What food don’t you like?  
3. What do you usually eat for breakfast / lunch / dinner?  
4. What healthy food do you eat every week?  

Complete:

- Today I learned new **food words** like...  
- Now I can **talk about food I like and don’t like**.  
- One sentence I remember from this class is...
            """
        )
        st.text_area(
            "Write your reflection here:",
            key="u3c1_reflection",
        )


# ==========================
# PAGES
# ==========================

def overview_page():
    show_logo()
    st.title("📘 A2 English Master – Elementary Course")
    st.markdown("...")  # Mantén aquí tu descripción completa


def levels_page():
    show_logo()
    st.title("🎯 English Levels (CEFR)")
    # ...


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

    # Bloques especiales Unit 2 (si los tienes completos)
    if unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class")
        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True,
            key="u2s1_hour",
        )
        if hour.startswith("1st"):
            render_unit2_session1_hour1()
        else:
            render_unit2_session1_hour2()

    # Unit 3 – Class 1: despliegas la clase móvil
    if unit_number == 3 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 📲 Mobile class – Full interactive version")
        unit3_class1_food_vocabulary()


def assessment_page():
    show_logo()
    st.title("📝 Assessment & Progress")
    # ...


def instructor_page():
    show_logo()
    st.title("👨‍🏫 Instructor")
    # ...


def access_page():
    show_logo()
    st.title("🔐 Access")

    tabs = st.tabs(["Student access", "Admin access"])

    # Student
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

    # Admin
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
            st.success("You are logged in as admin. Go to **Teacher Panel** or **Content admin** from the menu.")


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


def content_admin_page():
    show_logo()
    st.title("⚙️ Content Admin – Dynamic updates")

    # Debug rápido para ver el estado real de la sesión
    with st.expander("Session debug (solo para ti)"):
        st.json(st.session_state.get("auth", {}))

    # Usamos el helper estándar
    name, email, role = get_current_user()

    # Si NO eres admin, solo avisamos y pedimos ir a Access → Admin
    if role != "admin":
        st.error("This area is only for admin. Please go to **Access → Admin** and enter your code.")
        return

    # Si llegaste aquí, ya eres admin
    st.success(f"You are logged in as admin (**{name or 'Admin'}**). You can edit dynamic content.")

    st.markdown(
        """
Use this panel to **paste scripts or content** and save them as dynamic blocks.

They are stored in:
`content/unit<unit>/class<class>/<content_key>.txt`

Later you can load them from your code for:
- Audio scripts (ElevenLabs)
- Listening texts
- Dialogues
- Extra class content
        """
    )

    st.markdown("### 1. Select where to save")

    col1, col2 = st.columns(2)
    with col1:
        unit = st.number_input("Unit number", min_value=1, max_value=10, value=3, step=1)
    with col2:
        lesson = st.number_input("Class number", min_value=1, max_value=3, value=1, step=1)

    content_key = st.text_input(
        "Content key (example: audio_intro, dialog1, script_food_vocab)",
        value="audio_intro",
        help="This will be used as the filename, e.g. audio_intro.txt"
    )

    st.markdown("### 2. Content")

    if st.button("🔄 Load existing content (if any)", key="load_content_btn"):
        try:
            existing = load_content_block(int(unit), int(lesson), content_key)
            if existing:
                st.session_state["content_admin_text"] = existing
                st.success("Existing content loaded into the text area below.")
            else:
                st.info("No existing content found for this Unit/Class/Key.")
        except Exception as e:
            st.error(f"Error loading content: {e}")

    content_area = st.text_area(
        "Paste or write your content here:",
        value=st.session_state.get("content_admin_text", ""),
        height=400,
        key="content_admin_text",
    )

    st.markdown("### 3. Save / update")

    if st.button("💾 Save / update content", key="save_content_btn"):
        try:
            path = save_content_block(int(unit), int(lesson), content_key, content_area)
            st.success(f"Content saved successfully in: `{path}`")
        except Exception as e:
            st.error(f"Error saving content: {e}")


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
    elif page_id == "Content Admin":
        content_admin_page()
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
