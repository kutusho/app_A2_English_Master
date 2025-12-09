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

# Data paths
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
  --bg-card: #ffffff;
  --bg-card-soft: #e5edff;
  --accent: #3b82f6;
  --accent-soft: #dbeafe;
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
  :root {
    --bg-main: #020617;
    --bg-soft: #020617;
    --bg-card: #020617;
    --bg-card-soft: #020617;
    --accent: #60a5fa;
    --accent-soft: #1d4ed8;
    --accent-strong: #93c5fd;
    --accent-contrast: #fb923c;
    --navy: #e5e7eb;
    --text-main: #e5e7eb;
    --text-soft: #9ca3af;
    --border-soft: #1f2937;
    --shadow-soft: 0 20px 60px rgba(15, 23, 42, 0.9);
  }

  .stApp {
    background: radial-gradient(circle at top left, #020617 0%, #020617 45%, #020617 100%);
    color: var(--text-main);
  }
}

/* Contenedor principal tipo "glass card" */
.main-container {
  max-width: 1200px;
  margin: 1.5rem auto 3rem auto;
  padding: 1.5rem 1.8rem;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.95), rgba(255,255,255,0.90));
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-soft);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

@media (prefers-color-scheme: dark) {
  .main-container {
    background: radial-gradient(circle at top left, rgba(15,23,42,0.96), rgba(15,23,42,0.96));
    border: 1px solid rgba(148, 163, 184, 0.4);
  }
}

/* Encabezado superior con logo y título */
.header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.header-logo {
  width: 68px;
  height: 68px;
  border-radius: 1.15rem;
  background: radial-gradient(circle at top left, #eff6ff 0%, #dbeafe 40%, #bfdbfe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16px 35px rgba(59, 130, 246, 0.35);
  border: 1px solid rgba(129, 140, 248, 0.5);
  position: relative;
  overflow: hidden;
}
.header-logo::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.7), transparent 55%);
  mix-blend-mode: screen;
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
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.5);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.header-title {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--navy);
}

.header-subtitle {
  font-size: 0.96rem;
  color: var(--text-soft);
}

/* Tarjetas de navegación (Overview, Levels, etc.) */
.nav-card {
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.95), rgba(219, 234, 254, 0.98));
  border-radius: 999px;
  padding: 0.4rem 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  box-shadow: 0 16px 30px rgba(148, 163, 184, 0.6);
  border: 1px solid rgba(129, 140, 248, 0.8);
  margin-bottom: 0.5rem;
  position: relative;
  overflow: hidden;
}
.nav-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.85), transparent 60%);
  opacity: 0.9;
}

/* Pills del menú inferior */
.menu-pill-bar {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 1.5rem;
  background: radial-gradient(circle at top left, rgba(15,23,42,0.98), rgba(15,23,42,0.94));
  border-radius: 999px;
  padding: 0.35rem 0.4rem;
  box-shadow: 0 22px 40px rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  border: 1px solid rgba(148, 163, 184, 0.55);
  z-index: 9999;
}

.menu-pill {
  border-radius: 999px;
  padding: 0.45rem 0.95rem;
  font-size: 0.8rem;
  border: none;
  background: transparent;
  color: #e5e7eb;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
  transition: all 0.18s ease-out;
  white-space: nowrap;
}

.menu-pill-icon {
  font-size: 1rem;
  opacity: 0.9;
}

.menu-pill-active {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.7);
}

.menu-pill:hover {
  background: rgba(148, 163, 184, 0.28);
}

/* Tarjetas de contenido general */
.section-card {
  border-radius: 1.5rem;
  padding: 1.25rem 1.3rem;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.97), rgba(239,246,255,0.98));
  border: 1px solid rgba(191, 219, 254, 0.9);
  box-shadow: 0 18px 36px rgba(148, 163, 184, 0.55);
  margin-bottom: 1rem;
}

.section-card-muted {
  border-radius: 1.3rem;
  padding: 1rem 1.1rem;
  background: rgba(15, 23, 42, 0.96);
  color: #e5e7eb;
  border: 1px solid rgba(148, 163, 184, 0.7);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.92);
  margin-bottom: 1rem;
}

/* Títulos dentro de las tarjetas */
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 0.3rem;
}

.section-subtitle {
  font-size: 0.9rem;
  color: var(--text-soft);
  margin-bottom: 0.2rem;
}

/* Etiquetas pequeñas */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.1rem 0.55rem;
  border-radius: 999px;
  font-size: 0.8rem;
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: radial-gradient(circle at top left, rgba(15,23,42,1), rgba(15,23,42,0.85));
  color: #e5e7eb;
}

/* Ajustes de tipografía generales */
h1, h2, h3 {
  letter-spacing: -0.02em;
}

p, li {
  font-size: 0.94rem;
}

/* Ajustes para el sidebar */
section[data-testid="stSidebar"] {
  background: radial-gradient(circle at top left, #020617, #020617);
  border-right: 1px solid rgba(51, 65, 85, 0.9);
}

/* Quitar bordes de los bloques de Streamlit para que se vea más limpio */
.block-container {
  padding-top: 1.5rem;
}

/* Botones primarios */
.stButton>button {
  border-radius: 999px;
  border: none;
  padding: 0.5rem 1.15rem;
  font-weight: 600;
  font-size: 0.9rem;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.6);
  transition: all 0.16s ease-out;
}
.stButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.85);
}

/* Selects, radios, etc. */
.stSelectbox>div>div, .stRadio>div {
  font-size: 0.9rem;
}

/* Tab styling */
.stTabs [role="tablist"] {
  gap: 0.3rem;
}
.stTabs [role="tab"] {
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
}

/* Cards for features on Overview page */
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
  background: radial-gradient(circle at top left, rgba(255,255,255,0.96), rgba(219,234,254,0.97));
  border: 1px solid rgba(191, 219, 254, 0.9);
  box-shadow: 0 18px 35px rgba(148, 163, 184, 0.48);
}

/* Icon inside overview cards */
.overview-icon {
  font-size: 1.4rem;
  margin-bottom: 0.35rem;
}

/* Instructor card */
.instructor-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

/* Clase card */
.class-card {
  border-radius: 1.1rem;
  padding: 0.9rem 1rem;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.97), rgba(239,246,255,0.98));
  border: 1px solid rgba(191, 219, 254, 0.95);
  box-shadow: 0 18px 36px rgba(148, 163, 184, 0.6);
}

/* Pequeño sutil brillo en los títulos principales */
.glow-text {
  text-shadow: 0 0 1px rgba(129, 140, 248, 0.8), 0 0 9px rgba(59, 130, 246, 0.7);
}

/* Ajuste de ancho en mobile */
@media (max-width: 768px) {
  .main-container {
    margin: 0.8rem 0.3rem 4rem 0.3rem;
    padding: 1rem 0.9rem;
  }

  .header-title {
    font-size: 1.35rem;
  }

  .header-logo {
    width: 60px;
    height: 60px;
  }

  .header-logo-inner {
    font-size: 1.35rem;
  }
}

/* Ocultar footer de Streamlit (opcional) */
footer {
  visibility: hidden;
}
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
]

LESSONS = {
    1: [
        {
            "title": "Class 1 – Meeting people & introductions",
            "theory": [
                "Verb **be** (am/is/are) in affirmative, negative and questions.",
                "Subject pronouns (I, you, he, she, we, they).",
                "Short introductions and personal information (name, country, job).",
            ],
            "practice": [
                "Introduce yourself to a partner and exchange basic information.",
                "Write a short paragraph about a new friend.",
            ],
            "insights": [
                "Focus on clear pronunciation of names and countries.",
                "Encourage students to ask follow-up questions to keep the conversation going.",
            ],
        },
        {
            "title": "Class 2 – Describing people & appearance",
            "theory": [
                "Adjectives for physical description (tall, short, young, etc.).",
                "Verb **be** with adjectives.",
                "Using **have/has** for hair, eyes and accessories.",
            ],
            "practice": [
                "Describe a person in a picture.",
                "Guessing game: Who is it? (students describe someone and others guess).",
            ],
            "insights": [
                "Use real photos or magazine images to make descriptions more meaningful.",
                "Review word order with adjectives.",
            ],
        },
        {
            "title": "Class 3 – Personality & describing others",
            "theory": [
                "Adjectives of personality (friendly, shy, funny, etc.).",
                "Using **be** and **have** for personality and habits.",
                "Linking appearance and personality in a short description.",
            ],
            "practice": [
                "Write a short description of a friend or famous person.",
                "Class game: Match descriptions to photos.",
            ],
            "insights": [
                "Highlight cultural differences in how we describe people.",
                "Reinforce positive language and avoid stereotypes.",
            ],
        },
    ],
    2: [
        {
            "title": "Class 1 – Daily routines & frequency",
            "theory": [
                "Present simple for routines (affirmative).",
                "Adverbs of frequency (always, usually, sometimes, never).",
                "Daily routine vocabulary (get up, go to work, have lunch, etc.).",
            ],
            "practice": [
                "Talk about your routine using adverbs of frequency.",
                "Write a paragraph about a typical weekday.",
            ],
            "insights": [
                "Encourage students to connect the language with their real schedules.",
                "Use timelines or clocks to visualize routines.",
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
                "Highlight the difference between routine (weekdays) and free time (weekends).",
                "Use surveys to create real data from the group.",
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
                "Encourage students to give examples from their real life.",
                "Integrate simple well-being vocabulary (exercise, sleep, food).",
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


# ==========================
# LOGO & SIGNATURE
# ==========================
# ==========================
# DATA HELPERS – UNIT 2 ANSWERS
# ==========================

def save_unit2_answer(exercise_id, answer_text, session=None, unit=2, user_id=None):
    """
    Append a new answer for Unit 2 to a local CSV file
    so you can review it later from the teacher view.
    """
    if not answer_text:
        return  # nothing to save

    row = {
        "unit": unit,
        "session": session or "",
        "exercise_id": exercise_id,
        "answer": answer_text,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_id": user_id or "anonymous",
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
    """Load all saved answers for Unit 2 (for teacher review)."""
    if not UNIT2_ANSWERS_FILE.exists():
        return None
    try:
        return pd.read_csv(UNIT2_ANSWERS_FILE)
    except Exception:
        return None


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
            st.image(sig_path, width=180)
        except Exception:
            st.warning("The file 'firma-ivan-diaz.png' exists but is not a valid image.")


# ==========================
# AUDIO HELPERS
# ==========================

def _audio_or_warning(filename: str):
    """
    Helper to load audio from the /audio folder or show a warning if not present.
    """
    audio_path = AUDIO_DIR / filename
    if audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.warning(f"Audio file not found: `{filename}`. Please check the audio folder.")


def render_presentation_html(filename: str):
    """
    Render a pre-exported HTML presentation (e.g., from PowerPoint or Canva) stored in /static.
    """
    html_path = STATIC_DIR / filename
    if not html_path.exists():
        st.warning(f"Presentation not found: `{filename}` in /static.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=600, scrolling=True)


# ==========================
# OVERVIEW PAGE
# ==========================

def overview_page():
    show_logo()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="header">
  <div class="header-logo">
    <div class="header-logo-inner">
      A2
    </div>
  </div>
  <div class="header-text">
    <div class="header-title glow-text">A2 English Master</div>
    <div class="header-subtitle">
      Mobile-first English course · 100% in English · Designed for busy professionals
    </div>
  </div>
</div>

<div class="nav-card">
  <span>🚀</span>
  <span><strong>Autonomous platform</strong> · Audio, practice & progress from your phone</span>
</div>
        """,
        unsafe_allow_html=True,
    )

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
    <p>Listen to every topic with <strong>extra slow</strong>, student-friendly audio tracks and clear scripts.</p>
  </div>

  <div class="overview-card">
    <div class="overview-icon">📱</div>
    <strong>Designed for your phone</strong>
    <p>Study from WhatsApp and this platform: no heavy books, just focused, <strong>bite-sized lessons</strong>.</p>
  </div>

  <div class="overview-card">
    <div class="overview-icon">📈</div>
    <strong>Track your progress</strong>
    <p>Follow your units, listen again to audios and complete tasks that will be reviewed by your instructor.</p>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================
# LEVELS PAGE
# ==========================

def levels_page():
    show_logo()
    st.title("📊 English levels")

    st.markdown(
        """
### From beginner to independent user

This program focuses on **A2 – Elementary/Pre-intermediate** level, but it connects with A1 (basic) and B1 (intermediate).

- **A1** – You can understand and use very basic expressions, introduce yourself and ask simple questions.
- **A2** – You can talk about **daily routines, free time, past experiences and future plans** in a simple way.
- **B1** – You can understand main ideas of clear texts and deal with most situations while travelling.
        """
    )

    st.markdown("#### Where this course is located")
    st.markdown(
        """
- 📍 Entry requirement: **A1+** (you understand basic English and simple phrases).
- 🎯 Course target: **A2 / Early B1** in real communication.
- ⏱️ Duration: **10 units** with continuous assessment.
        """
    )


# ==========================
# ASSESSMENT & PROGRESS PAGE
# ==========================

def assessment_page_overview():
    show_logo()
    st.title("📈 Assessment & progress")

    st.markdown(
        """
This platform supports your **continuous assessment**. You will have:

- **Unit checks** every two units (listening, grammar and short writing).
- A **mid-course assessment** after Unit 5.
- A **final assessment** after Unit 10.
        """
    )


# ==========================
# INSTRUCTOR PAGE
# ==========================

def instructor_page():
    show_logo()
    st.title("👨‍🏫 Instructor & course style")

    col1, col2 = st.columns([1, 2], vertical_alignment="center")

    with col1:
        st.markdown(
            """
<div class="section-card">
  <div class="section-title">Course style</div>
  <ul>
    <li>100% in English (with support when needed).</li>
    <li>Focus on <strong>communication</strong>, not only grammar.</li>
    <li>Use of audio, repetition and real-life examples.</li>
    <li>Personalized feedback on your writing tasks.</li>
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
    Your instructor has experience in <strong>language teaching, tourism and training</strong>,
    with a strong focus on helping professionals use English in **real contexts**: work, travel and study.
  </p>
  <p>
    The goal is that you feel more <strong>confident</strong> using English every week, not only in class,
    but also in your daily life.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )


# ==========================
# UNIT 1 – SESSION 1
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
    st.write("Write **4–5 sentences** to introduce yourself. Use **be** and some basic information:")
    st.markdown(
        """
- Your name
- Your country or city
- Your job or what you study
- One extra detail (your hobbies, your family, etc.)
        """
    )

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
    st.markdown(
        """
Listen to two people meeting at a conference.  
Then answer:

1. What is their name?
2. Where are they from?
3. What is their job?
        """
    )

    st.markdown("### 🔊 Listening 2 – Spelling names")
    _audio_or_warning("U1_S1_audio2_spelling_names.mp3")
    st.markdown("Listen and repeat the names. Practise spelling your own name in English.")

    st.markdown("### 🗣️ Speaking task – Introduce yourself")
    st.markdown(
        """
Work in pairs (or imagine a partner if you are studying alone):

- Say your name, where you are from and what you do.
- Ask your partner: *“What do you do?”* / *“Where are you from?”*
        """
    )


# ==========================
# UNIT 1 – SESSION 2
# ==========================

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
    st.write("Think of a person you know well (friend, family, colleague).")
    st.markdown(
        "- What do they look like?\n"
        "- How tall are they?\n"
        "- What kind of hair do they have?"
    )

    st.markdown("### 🧩 Vocabulary – Physical appearance")
    st.markdown(
        """
**Height:**
- tall
- short
- of medium height

**Build:**
- slim
- thin
- strong
- a little heavy

**Hair:**
- long / short
- straight / curly / wavy
- dark / light / blonde / brown
        """
    )

    st.markdown("### ✍️ Practice – Describe a person")
    st.markdown(
        """
Write 4–5 sentences describing a person you know. Use:

- verb **be** with adjectives
- verb **have/has** with hair, eyes, etc.
        """
    )

def render_unit1_session2_hour2():
    st.subheader("Unit 1 – Session 2 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Describing people & appearance")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short descriptions of people.\n"
        "- Identify key words for appearance.\n"
        "- Describe people in photos."
    )

    st.markdown("### 🔊 Listening 1 – Describing a friend")
    _audio_or_warning("U1_S2_audio1_describing_friend.mp3")
    st.markdown(
        """
Listen to the description of a friend.

Then answer:

1. Is the friend tall or short?
2. What kind of hair do they have?
3. What are two adjectives that describe their personality?
        """
    )

    st.markdown("### 🗣️ Speaking – Who is it?")
    st.markdown(
        """
In pairs or in class:

- One person describes a photo.
- The other person must guess: *“Is it Ana?”* / *“Is it your brother?”*
        """
    )


# ==========================
# UNIT 1 – SESSION 3
# ==========================

def render_unit1_session3_hour1():
    st.subheader("Unit 1 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Personality & describing others")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use personality adjectives.\n"
        "- Write a short description combining appearance and personality.\n"
        "- Use **be** and **have** to describe people."
    )

    st.markdown("### ✏️ Warm-up – People you admire")
    st.write("Think of someone you admire (a friend, a family member or a famous person).")
    st.markdown(
        "- What do they look like?\n"
        "- What are they like (personality)?\n"
        "- Why do you admire them?"
    )

    st.markdown("### 🧩 Vocabulary – Personality adjectives")
    st.markdown(
        """
- friendly
- funny
- shy
- serious
- talkative
- hard-working
- lazy
- kind
        """
    )

    st.markdown("### ✍️ Writing – A person I admire")
    st.markdown(
        """
Write 5–7 sentences about a person you admire. Include:

- appearance (height, hair, etc.)
- personality (2–3 adjectives)
- why you admire them
        """
    )

def render_unit1_session3_hour2():
    st.subheader("Unit 1 – Session 3 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Personality & describing others")

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand people describing others.\n"
        "- Use adjectives of personality in simple conversations.\n"
        "- Give a short spoken description."
    )

    st.markdown("### 🔊 Listening 1 – Describing a colleague")
    _audio_or_warning("U1_S3_audio1_describing_colleague.mp3")
    st.markdown(
        """
Listen to a person describing their colleague.

Then answer:

1. Is the colleague friendly or shy?
2. Is the colleague hard-working or lazy?
3. What does the colleague look like?
        """
    )

    st.markdown("### 🔊 Listening 2 – Describing a famous person")
    _audio_or_warning("U1_S3_audio2_famous_person.mp3")
    st.markdown("Listen and write 3–4 sentences about the famous person described.")

    st.markdown("### 🗣️ Speaking – Describe someone")
    st.markdown(
        """
Choose a person (real or imaginary) and describe them:

- appearance
- personality
- what they do

Your partner or classmates guess who it is.
        """
    )


# ==========================
# EXTRA: UNIT 1 – MOBILE-FRIENDLY STRUCTURE
# ==========================

def render_unit1_mobile_extra():
    st.subheader("Unit 1 – Extra mobile practice")
    st.markdown("Use this section to continue practising vocabulary and grammar from Unit 1.")


# ==========================
# UNIT 2 – SESSIONS
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

    # Student workspace – present simple practice
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

    # Student writing space – My typical day
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

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short audios about people’s routines.\n"
        "- Identify **times, activities and frequency**.\n"
        "- Speak about your own daily routine."
    )

    st.markdown("### 🔊 Listening 1 – Welcome to Unit 2, Session 1")
    _audio_or_warning("U2_S1_audio1_intro.mp3")
    st.caption(
        "Slow introduction to the topic of daily routines. Listen and repeat some key sentences."
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
        "| Person | Morning | Afternoon | Evening |\n"
        "|--------|---------|-----------|---------|\n"
        "| A      |         |           |         |\n"
        "| B      |         |           |         |"
    )

    st.markdown("### 🗣️ Speaking – My day vs. their day")
    st.markdown(
        """
Talk about your routine and compare it with one person from the audio:

- What time do you get up?
- Do you start work early or late?
- When do you usually have lunch?
- Do you go to bed early?
        """
    )


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

    st.markdown("### 🧩 Grammar – Questions with do / does")
    st.markdown(
        """
We use **do/does** to make questions in the present simple.

**Structure:**

- Do + I/you/we/they + base verb → *Do you work on Saturday?*
- Does + he/she/it + base verb → *Does she like coffee?*
        """
    )

    st.markdown("**Examples:**")
    st.markdown(
        """
- Do you watch TV in the evening?
- Do they play football on Sundays?
- Does he go to the gym after work?
- Does she like reading?
        """
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

    # Student workspace – write your questions
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

    st.markdown("### 🧩 Vocabulary – Free-time activities")
    st.markdown(
        "- watch series / movies\n"
        "- go to the cinema\n"
        "- read books / magazines\n"
        "- listen to music / podcasts\n"
        "- go for a walk\n"
        "- play sports (football, basketball, volleyball, etc.)\n"
        "- go out with friends\n"
        "- play video games"
    )

    st.markdown("### ✍️ Practice – Write about your free time")
    st.write("Write **4–5 sentences** about what you do in your free time.")
    st.markdown(
        "- Use **present simple**.\n"
        "- Include **how often** you do these activities (always, usually, sometimes, never)."
    )

    st.markdown("### ✍️ Guided writing – Survey questions")
    st.write("Write **5 questions** about free time to ask your classmates.")
    st.info(
        'Example: *"Do you usually watch TV at night?"* / *"Does your best friend play any sport?"*'
    )

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

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand people talking about free-time activities.\n"
        "- Practise questions with **do/does**.\n"
        "- Use a survey to collect real information from the group."
    )

    st.markdown("### 🔊 Listening 1 – Free time conversations")
    _audio_or_warning("U2_S2_audio1_free_time_dialogues.mp3")
    st.markdown(
        """
Listen to short conversations about free time and answer:

1. What activities do they mention?
2. How often do they do these activities?
        """
    )

    st.markdown("### 🔊 Listening 2 – Survey results")
    _audio_or_warning("U2_S2_audio2_survey_results.mp3")
    st.write("Listen to the results of a small class survey about free time.")

    st.markdown("### 🗣️ Speaking – Class survey")
    st.markdown(
        """
Use your own questions from the **Guided writing – Survey questions** section:

- Ask at least 3 classmates (or imagine their answers if you are alone).
- Take notes of their answers.
- Share one interesting result with the group.
        """
    )


def render_unit2_session3_hour1():
    st.subheader("Unit 2 – Session 3 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Habits & lifestyle")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Talk about your habits using the present simple.\n"
        "- Use adverbs and expressions of frequency.\n"
        "- Write about healthy and unhealthy lifestyle habits."
    )

    st.markdown("### ✏️ Warm-up – Your lifestyle")
    st.write("Think about your lifestyle now.")
    st.markdown(
        "- Do you sleep well?\n"
        "- Do you do exercise?\n"
        "- Do you eat healthy food?"
    )

    st.markdown("### 🧩 Vocabulary – Lifestyle")
    st.markdown(
        """
**Healthy habits:**
- sleep 7–8 hours
- drink water
- eat fruit and vegetables
- do exercise
- walk every day

**Unhealthy habits:**
- sleep very late
- drink a lot of soda
- eat fast food
- smoke
- spend many hours on the phone
        """
    )

    st.markdown("### 🧩 Grammar – Talking about habits")
    st.markdown(
        """
We use the **present simple** and frequency expressions to talk about habits.

- I usually go to bed late.
- She always drinks coffee in the morning.
- They sometimes eat fast food.
        """
    )

    st.markdown("### ✍️ Practice – Healthy or unhealthy?")
    st.markdown(
        """
Look at the list of habits and write **H** (healthy) or **U** (unhealthy):

1. Drink water every day.
2. Sleep 4 hours per night.
3. Eat vegetables.
4. Smoke every day.
5. Walk to work or school.
        """
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

    st.markdown("### 🎯 Objectives")
    st.markdown(
        "- Understand short texts about healthy and unhealthy lifestyles.\n"
        "- Discuss your own habits.\n"
        "- Give simple advice using English."
    )

    st.markdown("### 🔊 Listening 1 – Two lifestyles")
    _audio_or_warning("U2_S3_audio1_two_lifestyles.mp3")
    st.markdown(
        """
Listen to two people talking about their lifestyle.

Then answer:

1. Who has a healthier lifestyle?
2. What good habits do they have?
3. What bad habits do they have?
        """
    )

    st.markdown("### 🔊 Listening 2 – Expert tips")
    _audio_or_warning("U2_S3_audio2_expert_tips.mp3")
    st.markdown("Listen to simple tips about how to improve your lifestyle.")

    st.markdown("### 🗣️ Speaking – My habits")
    st.markdown(
        """
Talk about your habits:

- Do you sleep well?
- Do you do exercise?
- Do you eat healthy food?

Share **one habit** you want to change and **one habit** you are proud of.
        """
    )


# ==========================
# UNIT 3 – BASIC STRUCTURE (placeholder)
# ==========================

def render_unit3_session1_hour1():
    st.subheader("Unit 3 – Session 1 · 1st Hour – Grammar & Writing")
    st.markdown("### Theme: Talking about last weekend")

    st.markdown("### ✅ Objectives")
    st.markdown(
        "- Use the **past simple (regular verbs)** to talk about last weekend.\n"
        "- Use time expressions like **yesterday**, **last weekend**, **on Saturday**.\n"
        "- Write a short text about your last weekend."
    )


def render_unit3_session1_hour2():
    st.subheader("Unit 3 – Session 1 · 2nd Hour – Listening & Speaking")
    st.markdown("### Theme: Talking about last weekend (listening & speaking)")

    st.markdown("This section will include audios and speaking tasks about last weekend.")


# ==========================
# MAIN PAGES – ENTER YOUR CLASS
# ==========================

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

    # Basic structure info
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
            horizontal=True,
            key="u1_s2_hour",
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True,
            key="u1_s2_view",
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
            horizontal=True,
            key="u1_s3_hour",
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True,
            key="u1_s3_view",
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
    if unit_number == 2 and "Class 1" in lesson_choice:
        st.markdown("---")
        st.markdown("### 🎧 Unit 2 – Session 1 · Mobile class + Presentation")

        hour = st.radio(
            "Choose part:",
            ["1st Hour – Grammar & Writing", "2nd Hour – Listening & Speaking"],
            horizontal=True,
            key="u2_s1_hour",
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True,
            key="u2_s1_view",
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
            horizontal=True,
            key="u2_s2_hour",
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True,
            key="u2_s2_view",
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
            horizontal=True,
            key="u2_s3_hour",
        )

        view_mode = st.radio(
            "View mode",
            ["Interactive app", "Slideshow (presentation)"],
            horizontal=True,
            key="u2_s3_view",
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

    # --- Teacher view – Unit 2 answers ---
    if unit_number == 2:
        st.markdown("---")
        st.markdown("### 📒 Teacher view – Unit 2 answers")

        df_u2 = load_unit2_answers()
        if df_u2 is None or df_u2.empty:
            st.info("No saved answers for Unit 2 yet. When students write in the app and press **Save**, their work will appear here.")
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

    st.markdown("### How feedback works")
    st.markdown(
        """
- You will receive comments on your **writing tasks** directly in this platform or via WhatsApp.  
- Listening and grammar tasks will have **answer keys** or short explanations.  
- Speaking will be practised in live or recorded sessions.
        """
    )


# ==========================
# MAIN APP
# ==========================

def main():
    inject_global_css()

    st.sidebar.title("A2 English Master")
    page = st.sidebar.radio(
        "Menu",
        [
            "Overview",
            "English levels",
            "Assessment overview",
            "Instructor",
            "Enter your class",
            "Assessment & Progress",
        ],
    )

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
