import streamlit as st
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
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
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
UNIT2_ANSWERS_FILE = DATA_DIR / "unit2_answers.csv"


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

/* Cards suaves */
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

</style>
        """,
        unsafe_allow_html=True,
    )


# ==========================
# ACCESS / SESSION STATE
# ==========================

def ensure_session_defaults():
    if "role" not in st.session_state:
        st.session_state["role"] = "guest"  # guest / student / admin
    if "student_name" not in st.session_state:
        st.session_state["student_name"] = ""
    if "student_email" not in st.session_state:
        st.session_state["student_email"] = ""
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False


def access_panel():
    ensure_session_defaults()
    role = st.session_state["role"]

    st.markdown("### 🔐 Access · Registro y administrador")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(
            "Elige cómo quieres usar la plataforma: como **estudiante** o como **administrador**."
        )
    with col2:
        label = "Invitado"
        icon = "👀"
        if role == "student":
            label, icon = "Estudiante", "🎧"
        elif role == "admin":
            label, icon = "Admin", "🛠️"
        st.info(f"{icon} Modo actual: **{label}**")

    tab_student, tab_admin = st.tabs(["🎓 Registro estudiante", "🛠️ Login admin"])

    with tab_student:
        name = st.text_input("Nombre", value=st.session_state["student_name"])
        email = st.text_input("Email (opcional)", value=st.session_state["student_email"])
        if st.button("Entrar como estudiante"):
            st.session_state["role"] = "student"
            st.session_state["student_name"] = name
            st.session_state["student_email"] = email
            st.session_state["is_admin"] = False
            st.success("Modo estudiante activado. Ya puedes entrar a tu clase y guardar tus respuestas.")

    with tab_admin:
        st.warning("Solo para ti. Usa un código que solo tú conozcas.")
        admin_code = st.text_input("Código de acceso admin", type="password")
        if st.button("Entrar como admin"):
            # Cambia este código por uno que solo tú conozcas
            if admin_code == "FLUNEX-ADMIN-2025":
                st.session_state["role"] = "admin"
                st.session_state["is_admin"] = True
                st.success("Modo administrador activado.")
            else:
                st.error("Código incorrecto.")


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
# LESSONS BY UNIT (igual que tu código original, no lo toco)
# ==========================
# (… aquí va TODO tu bloque LESSONS exactamente igual …)

# --- por espacio, dejo un comentario, pero en tu archivo pega
#     íntegro el bloque LESSONS que ya tienes, SIN CAMBIOS ---


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
            f'<a class="menu-link {active_class}" href="{href}">{icon} {label}</a>'
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
    audio_path = AUDIO_DIR / filename
    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning(f"Audio file not found: `audio/{filename}`")

def render_presentation_html(filename: str):
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
# STORAGE HELPERS – UNIT 2 RESPONSES
# ==========================

def save_unit2_answer(exercise_id, answer_text, session=None, unit=2):
    """Guarda cualquier respuesta de la Unidad 2 en CSV."""
    if not answer_text:
        return
    row = {
        "unit": unit,
        "session": session or "",
        "exercise_id": exercise_id,
        "answer": answer_text,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user": st.session_state.get("student_name", "anonymous")
    }
    if UNIT2_ANSWERS_FILE.exists():
        try:
            df = pd.read_csv(UNIT2_ANSWERS_FILE)
        except Exception:
            df = pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(UNIT2_ANSWERS_FILE, index=False)


def load_unit2_answers():
    if not UNIT2_ANSWERS_FILE.exists():
        return None
    try:
        return pd.read_csv(UNIT2_ANSWERS_FILE)
    except Exception:
        return None


# ==========================
# (AQUÍ siguen TODAS tus funciones render_unitX_sessionY_hourZ
#  tal cual las tenías, PERO voy a reescribir SOLO las de UNIDAD 2
#  para que sean "booklet" editable con guardado)
# ==========================

# --- deja tus funciones de Unit 1 y Unit 3+ exactamente igual ---


# ==========================
# UNIT 2 – SESSION 1 (EDITABLE)
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
    st.info('Example: *\"I get up at 7:00. I have breakfast, then I go to work.\"*')

    st.markdown("### 🧩 Grammar – Present simple (affirmative)")
    st.markdown(
        "We use the **present simple** to talk about routines and habits.\n\n"
        "**Structure:**\n\n"
        "- I / You / We / They **+ base verb** → *I work, They live, We study*\n"
        "- He / She / It **+ base verb + s / es** → *He works, She lives, It closes*"
    )

    st.markdown("### ✍️ Exercise 1 – Complete the verbs")
    st.markdown(
        "1. I ______ (get up) at 7:00.\n\n"
        "2. She ______ (start) work at 9:30.\n\n"
        "3. They ______ (have) lunch at 2:00.\n\n"
        "4. He ______ (go) to bed at 11:00.\n\n"
        "5. We ______ (study) English on Tuesday.\n\n"
        "6. My sister ______ (watch) series at night."
    )

    ex1_text = st.text_area(
        "✏️ Write your answers (1–6) here:",
        height=140,
        key="u2_s1_ex1"
    )
    if st.button("💾 Save Exercise 1", key="btn_u2_s1_ex1"):
        save_unit2_answer("U2_S1_EX1_PRESENT_SIMPLE", ex1_text, session="U2 S1 – Ex1")
        st.success("Your answers for Exercise 1 have been saved ✅")

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
        st.info('Example: *\"I sometimes have breakfast at a café.\"*')

    st.markdown("### ✍️ Exercise 2 – Frequency")
    st.markdown(
        "Rewrite the sentences with an adverb of frequency.\n\n"
        "1. I eat breakfast at home. (**usually**)\n\n"
        "2. She is late for work. (**sometimes**)\n\n"
        "3. They drink coffee in the evening. (**never**)\n\n"
        "4. We go to the cinema. (**hardly ever**)"
    )

    ex2_text = st.text_area(
        "✏️ Write your new sentences here:",
        height=140,
        key="u2_s1_ex2"
    )
    if st.button("💾 Save Exercise 2", key="btn_u2_s1_ex2"):
        save_unit2_answer("U2_S1_EX2_FREQUENCY", ex2_text, session="U2 S1 – Ex2")
        st.success("Your sentences for Exercise 2 have been saved ✅")

    st.markdown("### 📝 Booklet – My typical day")
    st.info(
        '"On weekdays I usually get up at 6:30. I have coffee and bread, then I go to work.\n'
        'I start work at 8:00 and finish at 4:00. After work I sometimes go to the gym\n'
        'or I meet my friends. I never go to bed late on Monday to Friday."'
    )
    st.write("Write **5–7 sentences** about your typical day. Use present simple + adverbs.")

    paragraph = st.text_area(
        "✏️ Write your paragraph here:",
        height=200,
        key="u2_s1_paragraph"
    )
    if st.button("💾 Save my paragraph", key="btn_u2_s1_paragraph"):
        save_unit2_answer("U2_S1_PARAGRAPH_MY_DAY", paragraph, session="U2 S1 – Writing")
        st.success("Your paragraph has been saved ✅")


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

    st.markdown("### 🔊 Listening 2 – Daily routine vocabulary")
    _audio_or_warning("U2_S1_audio2_routines_vocab.mp3")

    st.markdown("### 🔊 Listening 3 – Two people’s routines")
    _audio_or_warning("U2_S1_audio3_two_routines.mp3")

    st.markdown("### 🗣️ Speaking – Compare your routine")
    st.write("Use the booklet you escribiste en la primera hora para hablar 1–2 minutos.")


# ==========================
# UNIT 2 – SESSION 2 (EDITABLE)
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

    st.markdown("### ✍️ Exercise 1 – Make questions")
    st.markdown(
        "Write questions using **do/does**.\n\n"
        "1. you / watch TV / in the evening?\n"
        "2. your friends / play football / at the weekend?\n"
        "3. your teacher / give / a lot of homework?\n"
        "4. your family / go out / on Sundays?\n"
        "5. your best friend / like / coffee?"
    )

    ex1 = st.text_area(
        "✏️ Write your 5 questions here:",
        height=160,
        key="u2_s2_ex1"
    )
    if st.button("💾 Save Exercise 1", key="btn_u2_s2_ex1"):
        save_unit2_answer("U2_S2_EX1_QUESTIONS", ex1, session="U2 S2 – Ex1")
        st.success("Your questions have been saved ✅")

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

    st.markdown("### 📝 Booklet – Survey questions")
    st.info(
        'Example: *\"Do you usually watch TV at night?\"* / *\"Does your best friend play any sport?\"*'
    )
    survey = st.text_area(
        "✏️ Write your final 5 survey questions here:",
        height=180,
        key="u2_s2_survey"
    )
    if st.button("💾 Save my survey", key="btn_u2_s2_survey"):
        save_unit2_answer("U2_S2_SURVEY_QUESTIONS", survey, session="U2 S2 – Survey")
        st.success("Your survey questions have been saved ✅")


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

    st.markdown("### 🔊 Listening 2 – Three people and their free time")
    _audio_or_warning("U2_S2_audio2_three_people.mp3")

    st.markdown("### 🗣️ Speaking – Use your survey")
    st.write("Usa las preguntas que escribiste en el booklet para entrevistar a tus compañeros.")


# ==========================
# UNIT 2 – SESSION 3 (EDITABLE)
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
        "- **and** → to add information.\n"
        "- **but** → to contrast.\n"
        "- **because** → to give a reason."
    )

    st.markdown("### ✍️ Exercise – Complete with connectors")
    st.markdown(
        "1. I eat fruit in the morning ______ I drink water.\n\n"
        "2. I like watching series, ______ I don’t have much time.\n\n"
        "3. I go for a walk every day ______ it helps me relax.\n\n"
        "4. I usually sleep 7 hours, ______ sometimes I go to bed late."
    )

    ex_conn = st.text_area(
        "✏️ Write your sentences with connectors here:",
        height=160,
        key="u2_s3_ex_conn"
    )
    if st.button("💾 Save connector exercise", key="btn_u2_s3_ex_conn"):
        save_unit2_answer("U2_S3_EX_CONNECTORS", ex_conn, session="U2 S3 – Connectors")
        st.success("Your sentences have been saved ✅")

    st.markdown("### 📝 Booklet – My lifestyle")
    st.info(
        '"I usually get up early on weekdays because I work in the morning.\n'
        'I drink coffee and I sometimes eat fruit for breakfast.\n'
        'I don’t do a lot of exercise, but I walk to work every day.\n'
        'At the weekend I relax and spend time with my family."'
    )

    lifestyle = st.text_area(
        "✏️ Write 6–8 sentences about your lifestyle:",
        height=220,
        key="u2_s3_lifestyle"
    )
    if st.button("💾 Save my lifestyle paragraph", key="btn_u2_s3_life"):
        save_unit2_answer("U2_S3_PARAGRAPH_LIFESTYLE", lifestyle, session="U2 S3 – Lifestyle")
        st.success("Your paragraph has been saved ✅")


def render_unit2_session3_hour2():
    st.subheader("Unit 2 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Habits & lifestyle (listening & speaking)")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short texts about healthy and unhealthy lifestyles.\n"
        "- Discuss your own habits.\n"
        "- Give simple advice using **should / shouldn’t**."
    )

    st.markdown("### 🔊 Listening 1 – Two lifestyles")
    _audio_or_warning("U2_S3_audio1_two_lifestyles.mp3")

    st.markdown("### 🔊 Listening 2 – Expert tips")
    _audio_or_warning("U2_S3_audio2_details.mp3")

    st.markdown("### 🗣️ Speaking – Give advice")
    st.write("Da 2–3 consejos a un compañero usando **should / shouldn’t**.")


# ==========================
# PAGES
# ==========================

def overview_page():
    ensure_session_defaults()
    show_logo()
    st.title("📘 A2 English Master – Elementary Course")

    access_panel()

    st.markdown(
        """
### Learn to communicate with confidence in real situations

This A2 English program is designed for learners who want *clear progress*, 
practical language and a professional learning experience.
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
    st.markmarkdown = st.markdown
    st.markdown("### 🟦 Where does this course fit?")
    st.success(
        "This program corresponds to **A2 – Elementary**.\n\n"
        "- It consolidates basic A1 structures.\n"
        "- It expands vocabulary for daily life, work and travel.\n"
        "- It prepares learners to move into **B1 – Intermediate** with confidence."
    )


def lessons_page():
    ensure_session_defaults()
    show_logo()
    st.title("📖 Enter your class")

    if st.session_state["role"] == "guest":
        st.warning("Primero regístrate como **estudiante** o entra como **admin** en la página Overview.")
        access_panel()
        return

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
        for item in lesson["theory"]:
            st.markdown(f"- {item}")

    with tab_practice:
        for item in lesson["practice"]:
            st.markdown(f"- {item}")
        st.info("You can adapt these activities to face-to-face classes, online sessions or autonomous work.")

    with tab_insights:
        for item in lesson["insights"]:
            st.markdown(f"- {item}")
        st.success("Use this space to add your own notes, examples or anecdotes for each group.")

    # --- Bloques especiales con app + slideshow (Unit 1 y 2) ---
    if unit_number == 1 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 1 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True)
        mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True)
        if mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit1_session1_hour1()
            else:
                render_unit1_session1_hour2()
        else:
            render_presentation_html("unit1_session1_hour1.html" if hour.startswith("1st") else "unit1_session1_hour2.html")

    # (mantén aquí tus bloques para Unit 1 Class 2 y 3 tal como los tenías)

    if unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s1_hour")
        mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s1_mode")
        if mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session1_hour1()
            else:
                render_unit2_session1_hour2()
        else:
            render_presentation_html("unit2_session1_hour1.html" if hour.startswith("1st") else "unit2_session1_hour2.html")

    if unit_number == 2 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 2 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s2_hour")
        mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s2_mode")
        if mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session2_hour1()
            else:
                render_unit2_session2_hour2()
        else:
            render_presentation_html("unit2_session2_hour1.html" if hour.startswith("1st") else "unit2_session2_hour2.html")

    if unit_number == 2 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 3 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s3_hour")
        mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s3_mode")
        if mode == "Interactive app":
            if hour.startswith("1st"):
                render_unit2_session3_hour1()
            else:
                render_unit2_session3_hour2()
        else:
            render_presentation_html("unit2_session3_hour1.html" if hour.startswith("1st") else "unit2_session3_hour2.html")

    # Panel de revisión solo para admin
    if unit_number == 2 and st.session_state.get("is_admin", False):
        st.markdown("---")
        st.markdown("### 📒 Teacher panel – Unit 2 answers")
        df = load_unit2_answers()
        if df is None or df.empty:
            st.info("No hay respuestas guardadas todavía para la Unidad 2.")
        else:
            ex_ids = sorted(df["exercise_id"].unique())
            selected = st.multiselect("Filter by exercise:", ex_ids, default=ex_ids)
            st.dataframe(df[df["exercise_id"].isin(selected)], use_container_width=True)


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
