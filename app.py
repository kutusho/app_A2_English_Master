import streamlit as st
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components  # Para embeber presentaciones HTML

# ==========================
# BASIC CONFIG
# ==========================
st.set_page_config(
    page_title="A2 English Master",
    page_icon="📘",
    layout="wide"
)

# Rutas base
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())
AUDIO_DIR = BASE_DIR / "audio"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
UNIT2_ANSWERS_FILE = DATA_DIR / "unit2_answers.csv"

# ==========================
# GLOBAL STYLES
# ==========================

def inject_global_css():
    st.markdown(
        """
<style>
:root {
  --bg-main: #eef3fb;
  --bg-soft: #f9fafb;
  --bg-card: #ffffff;
  --accent: #3b82f6;
  --accent-strong: #1d4ed8;
  --accent-contrast: #f97316;
  --navy: #0f172a;
  --text-main: #0f172a;
  --text-soft: #6b7280;
  --border-soft: #d1d5db;
  --shadow-soft: 0 18px 45px rgba(15, 23, 42, 0.18);
  --radius-xl: 1.6rem;
}

/* Fondo general */
.stApp {
  background: radial-gradient(circle at top left, #ffffff 0%, var(--bg-main) 45%, #c7d2fe 100%);
  color: var(--navy);
  min-height: 100vh;
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Contenedor principal */
.main-container {
  max-width: 1180px;
  margin: 1.5rem auto 3rem auto;
  padding: 1.6rem 1.8rem 2.4rem 1.8rem;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.96), rgba(239,246,255,0.98));
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(148,163,184,0.35);
}

/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.2rem;
}

.header-logo {
  width: 70px;
  height: 70px;
  border-radius: 1.2rem;
  background: radial-gradient(circle at top left, #eff6ff 0%, #dbeafe 40%, #bfdbfe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16px 35px rgba(59,130,246,0.35);
  border: 1px solid rgba(129,140,248,0.6);
  position: relative;
  overflow: hidden;
}
.header-logo-inner {
  width: 68%;
  height: 68%;
  border-radius: 1rem;
  background: conic-gradient(from 220deg, #1d4ed8, #3b82f6, #38bdf8, #6366f1, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #eff6ff;
  font-weight: 800;
  font-size: 1.6rem;
  letter-spacing: 0.04em;
}

.header-title {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--navy);
}
.header-subtitle {
  font-size: 0.96rem;
  color: var(--text-soft);
}

/* Badge de rol */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.7);
  background: rgba(15,23,42,0.96);
  color: #e5e7eb;
  font-size: 0.78rem;
}

/* Cards */
.section-card {
  border-radius: 1.35rem;
  padding: 1.1rem 1.3rem;
  background: rgba(255,255,255,0.98);
  border: 1px solid rgba(191,219,254,0.9);
  box-shadow: 0 16px 30px rgba(148,163,184,0.4);
  margin-bottom: 1rem;
}
.section-card-muted {
  border-radius: 1.2rem;
  padding: 1rem 1.2rem;
  background: #020617;
  color: #e5e7eb;
  border: 1px solid rgba(148,163,184,0.8);
  box-shadow: 0 18px 36px rgba(15,23,42,0.9);
  margin-bottom: 1rem;
}

/* Títulos */
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}
.section-subtitle {
  font-size: 0.9rem;
  color: var(--text-soft);
}

/* Grid overview */
.overview-grid {
  display: grid;
  gap: 0.9rem;
}
@media (min-width: 900px) {
  .overview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.overview-card {
  border-radius: 1.1rem;
  padding: 0.9rem 1rem;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.97), rgba(219,234,254,0.97));
  border: 1px solid rgba(191,219,254,0.9);
  box-shadow: 0 18px 35px rgba(148,163,184,0.48);
}
.overview-icon {
  font-size: 1.4rem;
  margin-bottom: 0.35rem;
}

/* Botones globales */
.stButton>button {
  border-radius: 999px;
  border: none;
  padding: 0.45rem 1.1rem;
  font-weight: 600;
  font-size: 0.9rem;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #ffffff;
  box-shadow: 0 14px 30px rgba(37,99,235,0.5);
  transition: all 0.15s ease-out;
}
.stButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(37,99,235,0.8);
}

/* Sidebar: volvemos a algo limpio y clásico */
section[data-testid="stSidebar"] {
  background: #f8fafc;
}

/* Bloque principal */
.block-container {
  padding-top: 1.2rem;
}

/* H1–H3 */
h1, h2, h3 {
  letter-spacing: -0.02em;
}

/* Mobile */
@media (max-width: 768px) {
  .main-container {
    margin: 0.8rem 0.3rem 2.8rem 0.3rem;
    padding: 1.1rem 1rem 1.9rem 1rem;
  }
  .header-title {
    font-size: 1.45rem;
  }
  .header-logo {
    width: 62px;
    height: 62px;
  }
}

/* Ocultamos footer de Streamlit */
footer { visibility: hidden; }
</style>
        """,
        unsafe_allow_html=True,
    )

# ==========================
# DATA STRUCTURES
# ==========================

UNITS = [
    {"number": 1, "name": "People and descriptions"},
    {"number": 2, "name": "Daily life and routines"},
    {"number": 3, "name": "Past experiences"},
    {"number": 4, "name": "Travel and transport"},
    {"number": 5, "name": "Work and study"},
    {"number": 6, "name": "Food and restaurants"},
    {"number": 7, "name": "Health and emergencies"},
    {"number": 8, "name": "Plans and future"},
    {"number": 9, "name": "Stories and experiences"},
    {"number": 10, "name": "Review and final project"},
]

# Para Units 1–3 detallamos; Units 4–10 quedan como placeholder listos
LESSONS = {
    1: [
        {
            "title": "Class 1 – Meeting people & introductions",
            "theory": [
                "Verb **be** (am/is/are) in affirmative, negative and questions.",
                "Subject pronouns (I, you, he, she, we, they).",
                "Short introductions and personal information.",
            ],
            "practice": [
                "Introduce yourself to a partner.",
                "Write a short paragraph about a new friend.",
            ],
            "insights": [
                "Focus on clear pronunciation of names and countries.",
                "Encourage follow-up questions.",
            ],
        },
        {
            "title": "Class 2 – Describing people & appearance",
            "theory": [
                "Adjectives for physical description.",
                "Verb **be** with adjectives.",
                "Using **have/has** for hair, eyes and accessories.",
            ],
            "practice": [
                "Describe a person in a picture.",
                "Guessing game: Who is it?",
            ],
            "insights": [
                "Use real photos for more meaning.",
                "Review word order with adjectives.",
            ],
        },
        {
            "title": "Class 3 – Personality & describing others",
            "theory": [
                "Personality adjectives.",
                "Using **be** and **have** for personality and habits.",
                "Linking appearance and personality.",
            ],
            "practice": [
                "Write a description of a person you admire.",
                "Match descriptions to photos.",
            ],
            "insights": [
                "Highlight cultural differences in how we describe people.",
            ],
        },
    ],
    2: [
        {
            "title": "Class 1 – Daily routines & frequency",
            "theory": [
                "Present simple for routines (affirmative).",
                "Adverbs of frequency (always, usually, sometimes, never).",
                "Daily routine vocabulary.",
            ],
            "practice": [
                "Talk about your routine using adverbs of frequency.",
                "Write a paragraph about a typical weekday.",
            ],
            "insights": [
                "Connect the language with real schedules.",
            ],
        },
        {
            "title": "Class 2 – Free time & questions",
            "theory": [
                "Present simple questions with **do/does**.",
                "Short answers (Yes, I do / No, she doesn’t).",
                "Free-time activities vocabulary.",
            ],
            "practice": [
                "Survey classmates about free-time habits.",
                "Write questions and answers about hobbies.",
            ],
            "insights": [
                "Contrast routine and free time.",
            ],
        },
        {
            "title": "Class 3 – Habits & lifestyle",
            "theory": [
                "Present simple to talk about habits.",
                "Expressions for healthy / unhealthy lifestyles.",
                "Connectors (and, but, because).",
            ],
            "practice": [
                "Compare your lifestyle with a partner.",
                "Write about good and bad habits.",
            ],
            "insights": [
                "Integrate simple well-being vocabulary.",
            ],
        },
    ],
    3: [
        {
            "title": "Class 1 – Talking about last weekend",
            "theory": [
                "Past simple – regular verbs.",
                "Time expressions for the past (yesterday, last weekend, etc.).",
            ],
            "practice": [
                "Write about your last weekend.",
                "Interview a partner about what they did.",
            ],
            "insights": [
                "Use timelines to contrast present and past.",
            ],
        },
        {
            "title": "Class 2 – Past simple with irregular verbs",
            "theory": [
                "Common irregular verbs (go, see, have, do, etc.).",
            ],
            "practice": [
                "Short stories using irregular verbs.",
            ],
            "insights": [
                "Introduce verbs gradually, grouped by meaning.",
            ],
        },
        {
            "title": "Class 3 – Longer past stories",
            "theory": [
                "Sequencing events (first, then, after that).",
            ],
            "practice": [
                "Write a short story about a trip or experience.",
            ],
            "insights": [
                "Encourage students to personalize their stories.",
            ],
        },
    ],
}

# Units 4–10: tres clases genéricas cada una (ya están “todas las lecciones” en estructura)
for unit_num in range(4, 11):
    if unit_num not in LESSONS:
        LESSONS[unit_num] = [
            {
                "title": "Class 1 – Core lesson",
                "theory": ["Unit content coming soon."],
                "practice": ["Practice activities coming soon."],
                "insights": ["Use this space to add your own notes and activities."],
            },
            {
                "title": "Class 2 – Skills & practice",
                "theory": ["Skills focus coming soon."],
                "practice": ["Listening/reading speaking tasks coming soon."],
                "insights": ["Adapt to the needs of your group."],
            },
            {
                "title": "Class 3 – Integration & review",
                "theory": ["Review content coming soon."],
                "practice": ["Integrated tasks coming soon."],
                "insights": ["Connect this unit with real-life situations."],
            },
        ]

# ==========================
# HELPERS: DATA (UNIT 2 ANSWERS)
# ==========================

def save_unit2_answer(exercise_id, answer_text, session=None, unit=2, user_id=None):
    if not answer_text:
        return
    row = {
        "unit": unit,
        "session": session or "",
        "exercise_id": exercise_id,
        "answer": answer_text,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_id": user_id or st.session_state.get("student_name", "anonymous"),
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
# HELPERS: LOGOS & AUDIO
# ==========================

def show_logo():
    logo_path = os.path.join("assets", "logo-english-classes.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=210)

def show_signature():
    sig_path = os.path.join("assets", "firma-ivan-diaz.png")
    if os.path.exists(sig_path):
        st.image(sig_path, width=180)

def _audio_or_warning(filename: str):
    audio_path = AUDIO_DIR / filename
    if audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.warning(f"Audio file not found: `{filename}`. Please check the audio folder.")

def render_presentation_html(filename: str):
    html_path = STATIC_DIR / filename
    if not html_path.exists():
        st.warning(f"Presentation not found: `{filename}` in /static.")
        return
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=600, scrolling=True)

# ==========================
# ACCESS PANEL (Registro & Admin)
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

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("#### 🔐 Access · Registro y administrador")
        st.markdown(
            "Choose how you want to use the platform: as a **student** or as **administrator**."
        )
    with col_right:
        if role == "admin":
            label = "Admin"
            icon = "🛠️"
        elif role == "student":
            label = "Student"
            icon = "🎧"
        else:
            label = "Guest"
            icon = "👀"
        st.markdown(
            f'<span class="role-badge">{icon} Current mode: <strong>{label}</strong></span>',
            unsafe_allow_html=True,
        )

    tab_student, tab_admin = st.tabs(["🎓 Student registration", "🛠️ Admin login"])

    with tab_student:
        name = st.text_input("Your name", value=st.session_state["student_name"])
        email = st.text_input("Email (optional)", value=st.session_state["student_email"])
        if st.button("Start as student"):
            st.session_state["role"] = "student"
            st.session_state["student_name"] = name
            st.session_state["student_email"] = email
            st.session_state["is_admin"] = False
            st.success("Student mode activated. You can now enter your class and save your work.")

    with tab_admin:
        st.info("Admin mode is only for you. Use a private access code.")
        admin_code = st.text_input("Admin access code", type="password")
        if st.button("Login as admin"):
            # Código muy simple – cámbialo por algo que solo tú conozcas
            if admin_code == "FLUNEX-ADMIN-2025":
                st.session_state["role"] = "admin"
                st.session_state["is_admin"] = True
                st.success("Admin mode activated. Teacher panels are now visible.")
            else:
                st.error("Incorrect code. Try again.")

# ==========================
# PAGES
# ==========================

def overview_page():
    show_logo()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header
    col_h1, col_h2 = st.columns([1, 3], vertical_alignment="center")
    with col_h1:
        st.markdown(
            """
<div class="header">
  <div class="header-logo">
    <div class="header-logo-inner">A2</div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            """
<div class="header">
  <div>
    <div class="header-title">A2 English Master</div>
    <div class="header-subtitle">
      Mobile-first English program · audio, practice & feedback from your phone
    </div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    access_panel()

    st.markdown(
        """
<div class="section-card">
  <div class="section-title">What you will achieve in this course</div>
  <p>By the end of this A2 English program you will be able to:</p>
  <ul>
    <li>Understand and use <strong>everyday expressions</strong> related to people, work and daily life.</li>
    <li>Talk about your <strong>routine, free time and past experiences</strong> with more confidence.</li>
    <li>Write <strong>short texts</strong> and complete forms in English with correct basic grammar.</li>
    <li>Participate in <strong>simple conversations</strong> at work, in class or when travelling.</li>
  </ul>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="overview-grid">
  <div class="overview-card">
    <div class="overview-icon">🎧</div>
    <strong>Audio-first learning</strong>
    <p>Slow, clear audios with scripts that you can replay as many times as you need.</p>
  </div>
  <div class="overview-card">
    <div class="overview-icon">📱</div>
    <strong>Designed for your phone</strong>
    <p>Short, focused lessons you can complete from your mobile, plus printable booklets if you want.</p>
  </div>
  <div class="overview-card">
    <div class="overview-icon">📈</div>
    <strong>Progress & feedback</strong>
    <p>Writing tasks and exercises that you complete here and I can review from the admin panel.</p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

def levels_page():
    show_logo()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    if st.button("← Back to overview"):
        st.session_state["page"] = "Overview"

    st.title("📊 English levels")

    st.markdown(
        """
### From beginner to independent user

This program focuses on **A2 – Elementary/Pre-intermediate**, connecting A1 (basic) and B1 (intermediate).

- **A1** – Understand and use very basic expressions, introduce yourself and ask simple questions.  
- **A2** – Talk about **daily routines, free time, past experiences and future plans** in a simple way.  
- **B1** – Understand main ideas of clear texts and deal with most situations while travelling.
        """
    )

    st.markdown("#### Where this course is located")
    st.markdown(
        """
- 📍 Entry requirement: **A1+**  
- 🎯 Course target: **A2 / early B1** in real communication  
- ⏱️ Approx. length: **10 units** with continuous assessment
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

def assessment_page_overview():
    show_logo()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    if st.button("← Back to overview"):
        st.session_state["page"] = "Overview"

    st.title("📈 Assessment overview")

    st.markdown(
        """
This platform supports your **continuous assessment**:

- ✅ Unit checks every two units  
- 📌 Mid-course assessment (after Unit 5): listening, reading, writing & speaking  
- 🎯 Final assessment (after Unit 10): integrated skills
        """
    )

    st.markdown(
        """
You will receive:

- comments on your **writing tasks** (inside this platform or via WhatsApp)  
- answer keys or short explanations for grammar & listening tasks  
- speaking feedback during live or recorded sessions
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

def instructor_page():
    show_logo()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    if st.button("← Back to overview"):
        st.session_state["page"] = "Overview"

    st.title("👨‍🏫 Instructor & course style")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            """
<div class="section-card">
  <div class="section-title">Course style</div>
  <ul>
    <li>100% in English (with support in Spanish when you really need it).</li>
    <li>Focus on <strong>communication</strong>, not only grammar.</li>
    <li>Audio, guided writing and simple speaking tasks.</li>
    <li>Personalized feedback on your progress.</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
<div class="section-card-muted">
  <div class="section-title">About your instructor</div>
  <p>
    Your instructor has experience in <strong>language teaching, tourism and training</strong>.
    The goal is that English becomes a tool for work, travel and personal projects – not only a school subject.
  </p>
  <p>
    Classes are designed to be <strong>practical, clear and human</strong>, always connecting content
    with your real context.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )

    show_signature()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# UNIT 1 – SESSIONS (mismas que versión anterior)
# ==========================

def render_unit1_session1_hour1():
    st.subheader("Unit 1 – Session 1 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Meeting people & introductions")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use the verb **be** (am/is/are) to talk about name, country and job.\n"
        "- Use **subject pronouns** (I, you, he, she, we, they).\n"
        "- Write a short introduction about yourself."
    )

    st.markdown("### ✏️ Warm-up – Who are you?")
    st.write("Think about these questions and be ready to share:")
    st.markdown(
        "- What is your name?\n"
        "- Where are you from?\n"
        "- What do you do (study or job)?"
    )

    st.markdown("### 🧩 Grammar – Verb be (am/is/are)")
    st.markdown(
        """
We use **be** to talk about who we are, where we are from and our job.

**Affirmative forms:**

- I **am** (I'm)
- You **are** (You're)
- He/She/It **is** (He's / She's / It's)
- We/They **are** (We're / They're)
        """
    )

    st.markdown("**Examples:**")
    st.markdown(
        """
- I’m Iván. I’m from Mexico.  
- She’s Anna. She’s a teacher.  
- We’re students. We’re from Chiapas.
        """
    )

    st.markdown("### ✍️ Practice – Complete the sentences")
    st.markdown(
        """
1. I ___ Iván. I ___ from Mexico.  
2. She ___ Laura. She ___ a doctor.  
3. We ___ students. We ___ from Chiapas.  
4. They ___ friends. They ___ from Spain.  
        """
    )

    st.markdown("### ✍️ Writing – Introduce yourself")
    st.write("Write **4–5 sentences** to introduce yourself.")

def render_unit1_session1_hour2():
    st.subheader("Unit 1 – Session 1 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Meeting people & introductions")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand introductions in simple conversations.\n"
        "- Practise saying your name, country and job.\n"
        "- Ask and answer basic questions."
    )

    st.markdown("### 🔊 Listening 1 – Introductions at a conference")
    _audio_or_warning("U1_S1_audio1_introductions.mp3")

    st.markdown("### 🔊 Listening 2 – Spelling names")
    _audio_or_warning("U1_S1_audio2_spelling_names.mp3")

    st.markdown("### 🗣️ Speaking task – Introduce yourself")
    st.markdown("Practise with a partner or record yourself.")

def render_unit1_session2_hour1():
    st.subheader("Unit 1 – Session 2 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Describing people & appearance")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use adjectives to describe physical appearance.\n"
        "- Use **have/has** to talk about hair, eyes and accessories.\n"
        "- Write a short description of a person."
    )

    st.markdown("### ✏️ Warm-up – People around you")
    st.write("Think of a person you know well.")
    st.markdown(
        "- What do they look like?\n"
        "- How tall are they?\n"
        "- What kind of hair do they have?"
    )

def render_unit1_session2_hour2():
    st.subheader("Unit 1 – Session 2 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Describing people & appearance")
    _audio_or_warning("U1_S2_audio1_describing_friend.mp3")

def render_unit1_session3_hour1():
    st.subheader("Unit 1 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Personality & describing others")
    st.markdown("Work with personality adjectives and a short description of someone you admire.")

def render_unit1_session3_hour2():
    st.subheader("Unit 1 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Personality & describing others")
    _audio_or_warning("U1_S3_audio1_describing_colleague.mp3")

# ==========================
# UNIT 2 – SESSIONS (con booklet editable)
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

    st.markdown("### 🧩 Grammar – Present simple (affirmative)")
    st.markdown(
        "We use the **present simple** to talk about routines and habits.\n\n"
        "- I/You/We/They + base verb → *I work, They live*\n"
        "- He/She/It + base verb + s/es → *He works, She watches*"
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

    practice_u2_s1_ex1 = st.text_area(
        "✏️ Write your answers for 1–6 here:",
        height=140,
        key="u2_s1_ex1_answers"
    )
    if st.button("💾 Save my answers (Practice – Present simple)", key="save_u2_s1_ex1"):
        save_unit2_answer(
            exercise_id="U2_S1_EX1_PRESENT_SIMPLE",
            answer_text=practice_u2_s1_ex1,
            session="Session 1 – Grammar practice"
        )
        st.success("Your answers for this exercise have been saved ✅")

    st.markdown("### 🧩 Adverbs of frequency")
    st.markdown(
        "- always · usually · often · sometimes · hardly ever · never\n\n"
        "They go **before** the main verb: *I usually get up at 7:00.*"
    )

    st.markdown("### ✍️ Guided writing – My typical day")
    st.info(
        '"On weekdays I usually get up at 6:30. I have coffee and bread, then I go to work.\n'
        'I start work at 8:00 and finish at 4:00. After work I sometimes go to the gym\n'
        'or I meet my friends. I never go to bed late on Monday to Friday."'
    )

    writing_u2_s1 = st.text_area(
        "📝 Write your paragraph here:",
        height=200,
        key="u2_s1_writing"
    )
    if st.button("💾 Save my writing (My typical day)", key="save_u2_s1_writing"):
        save_unit2_answer(
            exercise_id="U2_S1_WRITING_MY_DAY",
            answer_text=writing_u2_s1,
            session="Session 1 – Guided writing"
        )
        st.success("Your writing has been saved ✅")

def render_unit2_session1_hour2():
    st.subheader("Unit 2 – Session 1 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Daily routines (listening & speaking)")

    _audio_or_warning("U2_S1_audio1_intro.mp3")
    _audio_or_warning("U2_S1_audio2_routines_vocab.mp3")
    _audio_or_warning("U2_S1_audio3_two_routines.mp3")

def render_unit2_session2_hour1():
    st.subheader("Unit 2 – Session 2 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Free time & present simple questions")

    st.markdown("### 🧩 Grammar – Questions with do / does")
    st.markdown(
        "- Do + I/you/we/they + base verb → *Do you watch TV in the evening?*\n"
        "- Does + he/she/it + base verb → *Does she like coffee?*"
    )

    st.markdown("### ✍️ Controlled practice – Make questions")
    st.markdown(
        "1. you / watch TV / in the evening?\n"
        "2. your friends / play football / at the weekend?\n"
        "3. your teacher / give / a lot of homework?\n"
        "4. your family / go out / on Sundays?\n"
        "5. your best friend / like / coffee?"
    )

    questions_u2_s2 = st.text_area(
        "📝 Write your 5 questions here:",
        height=160,
        key="u2_s2_questions"
    )
    if st.button("💾 Save my questions (Free time)", key="save_u2_s2_questions"):
        save_unit2_answer(
            exercise_id="U2_S2_EX1_QUESTIONS",
            answer_text=questions_u2_s2,
            session="Session 2 – Controlled practice"
        )
        st.success("Your questions have been saved ✅")

    st.markdown("### ✍️ Guided writing – Survey questions")
    st.info('Example: *"Do you usually watch TV at night?"* / *"Does your best friend play any sport?"*')

    survey_u2_s2 = st.text_area(
        "✏️ Write your final version of the 5 survey questions:",
        height=180,
        key="u2_s2_survey_questions"
    )
    if st.button("💾 Save my survey (Free time)", key="save_u2_s2_survey"):
        save_unit2_answer(
            exercise_id="U2_S2_SURVEY_QUESTIONS",
            answer_text=survey_u2_s2,
            session="Session 2 – Survey writing"
        )
        st.success("Your survey questions have been saved ✅")

def render_unit2_session2_hour2():
    st.subheader("Unit 2 – Session 2 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Free time (listening & survey)")
    _audio_or_warning("U2_S2_audio1_free_time_dialogues.mp3")
    _audio_or_warning("U2_S2_audio2_survey_results.mp3")

def render_unit2_session3_hour1():
    st.subheader("Unit 2 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Habits & lifestyle")

    st.markdown("### 🧩 Vocabulary – Lifestyle")
    st.markdown(
        "**Healthy:** sleep 7–8 hours, drink water, eat vegetables, do exercise, walk every day.\n\n"
        "**Unhealthy:** sleep very late, drink a lot of soda, eat fast food, smoke, many hours on the phone."
    )

    st.markdown("### ✍️ Guided writing – My lifestyle")
    st.info(
        '"I usually get up early on weekdays because I work in the morning.\n'
        'I drink coffee and I sometimes eat fruit for breakfast.\n'
        'I don’t do a lot of exercise, but I walk to work every day.\n'
        'At the weekend I relax and spend time with my family."'
    )

    lifestyle_u2_s3 = st.text_area(
        "📝 Write your paragraph about your lifestyle:",
        height=220,
        key="u2_s3_lifestyle"
    )
    if st.button("💾 Save my writing (My lifestyle)", key="save_u2_s3_lifestyle"):
        save_unit2_answer(
            exercise_id="U2_S3_WRITING_LIFESTYLE",
            answer_text=lifestyle_u2_s3,
            session="Session 3 – Lifestyle writing"
        )
        st.success("Your lifestyle paragraph has been saved ✅")

def render_unit2_session3_hour2():
    st.subheader("Unit 2 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Habits & lifestyle (listening & speaking)")
    _audio_or_warning("U2_S3_audio1_two_lifestyles.mp3")
    _audio_or_warning("U2_S3_audio2_expert_tips.mp3")

# ==========================
# UNIT 3 PLACEHOLDER
# ==========================

def render_unit3_session1_hour1():
    st.subheader("Unit 3 – Session 1 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Talking about last weekend")
    st.write("Content to be expanded – structure ready.")

def render_unit3_session1_hour2():
    st.subheader("Unit 3 – Session 1 · 2nd Hour – Listening & Speaking")
    st.write("Listening and speaking tasks coming soon.")

# ==========================
# ENTER YOUR CLASS
# ==========================

def lessons_page():
    ensure_session_defaults()
    show_logo()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if st.button("← Back to overview"):
        st.session_state["page"] = "Overview"

    role = st.session_state["role"]
    if role == "guest":
        st.warning("Please register as a **student** or login as **admin** in the Overview page before entering your class.")
        access_panel()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.title("📖 Enter your class")

    unit_options = [f"Unit {u['number']} – {u['name']}" for u in UNITS]
    unit_choice = st.selectbox("Choose your unit", unit_options)
    unit_number = UNITS[unit_options.index(unit_choice)]["number"]

    lessons = LESSONS.get(unit_number, [])
    if not lessons:
        st.info("No lessons defined for this unit yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    lesson_titles = [l["title"] for l in lessons]
    lesson_choice = st.selectbox("Choose your lesson", lesson_titles)
    lesson = lessons[lesson_titles.index(lesson_choice)]

    tab_theory, tab_practice, tab_insights = st.tabs(["📘 Theory", "📝 Practice", "💡 Insights"])

    with tab_theory:
        st.markdown("### Key theory")
        for item in lesson["theory"]:
            st.markdown(f"- {item}")

    with tab_practice:
        st.markdown("### Suggested activities")
        for item in lesson["practice"]:
            st.markdown(f"- {item}")

    with tab_insights:
        st.markdown("### Teaching & learning insights")
        for item in lesson["insights"]:
            st.markdown(f"- {item}")

    # Bloques especiales con app interactiva + presentaciones
    if unit_number == 1 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 1 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True)
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True)
        if view_mode == "Interactive app":
            render_unit1_session1_hour1() if hour.startswith("1st") else render_unit1_session1_hour2()
        else:
            render_presentation_html("unit1_session1_hour1.html" if hour.startswith("1st") else "unit1_session1_hour2.html")

    if unit_number == 1 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 2 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u1s2hour")
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u1s2view")
        if view_mode == "Interactive app":
            render_unit1_session2_hour1() if hour.startswith("1st") else render_unit1_session2_hour2()
        else:
            render_presentation_html("unit1_session2_hour1.html" if hour.startswith("1st") else "unit1_session2_hour2.html")

    if unit_number == 1 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 1 – Session 3 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u1s3hour")
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u1s3view")
        if view_mode == "Interactive app":
            render_unit1_session3_hour1() if hour.startswith("1st") else render_unit1_session3_hour2()
        else:
            render_presentation_html("unit1_session3_hour1.html" if hour.startswith("1st") else "unit1_session3_hour2.html")

    if unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s1hour")
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s1view")
        if view_mode == "Interactive app":
            render_unit2_session1_hour1() if hour.startswith("1st") else render_unit2_session1_hour2()
        else:
            render_presentation_html("unit2_session1_hour1.html" if hour.startswith("1st") else "unit2_session1_hour2.html")

    if unit_number == 2 and "Class 2" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 2 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s2hour")
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s2view")
        if view_mode == "Interactive app":
            render_unit2_session2_hour1() if hour.startswith("1st") else render_unit2_session2_hour2()
        else:
            render_presentation_html("unit2_session2_hour1.html" if hour.startswith("1st") else "unit2_session2_hour2.html")

    if unit_number == 2 and "Class 3" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 3 · Mobile class + Presentation")
        hour = st.radio("Choose part:", ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"], horizontal=True, key="u2s3hour")
        view_mode = st.radio("View mode", ["Interactive app", "Slideshow (presentation)"], horizontal=True, key="u2s3view")
        if view_mode == "Interactive app":
            render_unit2_session3_hour1() if hour.startswith("1st") else render_unit2_session3_hour2()
        else:
            render_presentation_html("unit2_session3_hour1.html" if hour.startswith("1st") else "unit2_session3_hour2.html")

    # Panel de teacher/admin SOLO si estás en modo admin
    if unit_number == 2 and st.session_state.get("is_admin", False):
        st.markdown("---")
        st.markdown("### 📒 Teacher view – Unit 2 answers")
        df_u2 = load_unit2_answers()
        if df_u2 is None or df_u2.empty:
            st.info("No saved answers for Unit 2 yet.")
        else:
            exercise_ids = sorted(df_u2["exercise_id"].unique())
            selected_ex = st.multiselect(
                "Filter by exercise (optional):",
                options=exercise_ids,
                default=exercise_ids,
                key="u2_teacher_filter"
            )
            filtered = df_u2[df_u2["exercise_id"].isin(selected_ex)]
            st.dataframe(filtered, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

def assessment_page():
    show_logo()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    if st.button("← Back to overview"):
        st.session_state["page"] = "Overview"

    st.title("📝 Assessment & Progress")

    st.markdown("### Assessment structure")
    st.markdown(
        """
- Unit progress checks every **two units**  
- **Mid-course assessment** (after Unit 5): listening, reading, writing & speaking  
- **Final exam** (after Unit 10): full integrated assessment
        """
    )

    st.markdown("### How feedback works")
    st.markdown(
        """
- You will receive comments on your **writing tasks** directly in this platform or via WhatsApp.  
- Listening and grammar tasks will have **answer keys** or short explanations.  
- Speaking will be practised in live or recorded sessions.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# MAIN
# ==========================

def main():
    inject_global_css()
    if "page" not in st.session_state:
        st.session_state["page"] = "Overview"

    st.sidebar.title("A2 English Master")
    page = st.sidebar.radio(
        "Menu",
        ["Overview", "English levels", "Assessment overview", "Instructor", "Enter your class", "Assessment & Progress"],
        index=["Overview", "English levels", "Assessment overview", "Instructor", "Enter your class", "Assessment & Progress"].index(st.session_state["page"]),
    )
    st.session_state["page"] = page

    if page == "Overview":
        overview_page()
    elif page == "English levels":
        levels_page()
    elif page == "Assessment overview":
        assessment_page_overview()
    elif page == "Instructor":
        instructor_page()
    elif page == "Enter your class":
        lessons_page()
    elif page == "Assessment & Progress":
        assessment_page()

if __name__ == "__main__":
    main()
