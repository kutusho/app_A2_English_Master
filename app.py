import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit.components.v1 as components
import datetime as dt
import csv
import textwrap
import json
import requests

# ==========================
# BASIC CONFIG
# ==========================
st.set_page_config(
    page_title="A2 English Master",
    page_icon="📘",
    layout="wide"
)

# Base paths
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())
AUDIO_DIR = BASE_DIR / "audio"
STATIC_DIR = BASE_DIR / "static"
RESPONSES_DIR = BASE_DIR / "responses"
CONTENT_DIR = BASE_DIR / "content"
PROGRESS_DIR = BASE_DIR / "progress"

RESPONSES_DIR.mkdir(exist_ok=True)
CONTENT_DIR.mkdir(exist_ok=True)
PROGRESS_DIR.mkdir(exist_ok=True)

RESPONSES_FILE = RESPONSES_DIR / "unit2_responses.csv"
PROGRESS_FILE = PROGRESS_DIR / "progress_a2.csv"

# ==========================
# ADMIN / AUTH CONFIG
# ==========================
ADMIN_ACCESS_CODE = os.getenv("ENGLISH_MASTER_ADMIN_CODE", "A2-ADMIN-2025")

# ElevenLabs API
ELEVENLABS_API_KEY = (
    st.secrets.get("ELEVENLABS_API_KEY", None)
    if hasattr(st, "secrets")
    else None
)
if not ELEVENLABS_API_KEY:
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

DEFAULT_TEACHER_VOICE_ID = os.getenv("ELEVENLABS_TEACHER_VOICE_ID", "")
DEFAULT_STUDENT_VOICE_ID = os.getenv("ELEVENLABS_STUDENT_VOICE_ID", "")


# ==========================
# SESSION & AUTH HELPERS
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
# ANSWERS – UNIT 2
# ==========================
def save_unit2_response(user_email, user_name, session, hour, exercise_id, text):
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
# PROGRESS SYSTEM A2
# ==========================
def _ensure_progress_file():
    if not PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "timestamp",
                    "user_email",
                    "user_name",
                    "unit",
                    "class",
                    "status",
                ],
            )
            writer.writeheader()


def save_progress(user_email, user_name, unit, class_number, status="completed"):
    if not user_email:
        st.warning("Please login as student in **Access → Student access** to track progress.")
        return False

    _ensure_progress_file()
    row = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "user_email": user_email,
        "user_name": user_name or user_email,
        "unit": int(unit),
        "class": int(class_number),
        "status": status,
    }
    try:
        with open(PROGRESS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)
        return True
    except Exception as e:
        st.error(f"Error saving progress: {e}")
        return False


def load_progress_for_user(user_email):
    if not PROGRESS_FILE.exists() or not user_email:
        return pd.DataFrame(columns=["unit", "class", "status"])

    try:
        df = pd.read_csv(PROGRESS_FILE)
        df = df[df["user_email"] == user_email]
        return df
    except Exception:
        return pd.DataFrame(columns=["unit", "class", "status"])


def get_completed_classes_for_user(user_email):
    df = load_progress_for_user(user_email)
    if df.empty:
        return set()
    completed = df[df["status"] == "completed"]
    return set(zip(completed["unit"], completed["class"]))


# ==========================
# CONTENT STORAGE HELPERS
# ==========================
def get_content_path(unit: int, class_number: int, content_key: str) -> Path:
    unit_dir = CONTENT_DIR / f"unit{unit}"
    class_dir = unit_dir / f"class{class_number}"
    class_dir.mkdir(parents=True, exist_ok=True)
    return class_dir / f"{content_key}.txt"


def save_content_block(unit: int, class_number: int, content_key: str, text: str) -> Path:
    path = get_content_path(unit, class_number, content_key)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")
    return path


def load_content_block(unit: int, class_number: int, content_key: str) -> str:
    path = get_content_path(unit, class_number, content_key)
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def scan_content_structure():
    """
    Returns a dict:
    {
      unit_number: {
        class_number: [list_of_keys]
      }
    }
    """
    structure = {}
    if not CONTENT_DIR.exists():
        return structure

    for unit_dir in sorted(CONTENT_DIR.glob("unit*")):
        try:
            unit_num = int(unit_dir.name.replace("unit", ""))
        except ValueError:
            continue
        structure[unit_num] = {}
        for class_dir in sorted(unit_dir.glob("class*")):
            try:
                class_num = int(class_dir.name.replace("class", ""))
            except ValueError:
                continue
            keys = []
            for f in class_dir.glob("*.txt"):
                keys.append(f.stem)
            structure[unit_num][class_num] = sorted(keys)
    return structure


# ==========================
# ELEVENLABS HELPERS
# ==========================
def has_elevenlabs():
    return bool(ELEVENLABS_API_KEY)


def elevenlabs_tts_to_file(text: str, voice_id: str, filename: str, model_id="eleven_multilingual_v2"):
    """
    Simple helper to generate one audio file via ElevenLabs TTS.
    """
    if not ELEVENLABS_API_KEY:
        st.error("ElevenLabs API key not configured.")
        return None

    AUDIO_DIR.mkdir(exist_ok=True)
    out_path = AUDIO_DIR / filename

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
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
        if resp.status_code != 200:
            st.error(f"ElevenLabs error {resp.status_code}: {resp.text}")
            return None
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return out_path
    except Exception as e:
        st.error(f"Error calling ElevenLabs API: {e}")
        return None


def render_dynamic_dialog_with_voices(unit: int, class_number: int, content_key: str,
                                      teacher_voice_id: str, student_voice_id: str,
                                      audio_basename: str):
    """
    Simple pattern:
    - Loads a script from content/unitX/classY/<content_key>.txt
    - Expects lines like:
        TEACHER: ...
        STUDENT: ...
    - Generates two separate audios or one joined per speaker (simplificado).
    """
    st.markdown("### 🎧 Dynamic dialog")

    script = load_content_block(unit, class_number, content_key)
    if not script:
        st.info("No dialog script found yet in Content Admin for this key.")
        return

    st.code(script, language="text")

    if not has_elevenlabs():
        st.warning("ElevenLabs API key not configured. Audio generation is disabled.")
        return

    if st.button("Generate dialog audio with ElevenLabs", key=f"gen_dialog_{unit}_{class_number}_{content_key}"):
        # Simplificación: un solo audio con voz de teacher,
        # o puedes extender para separar por speaker.
        voice_id = teacher_voice_id or DEFAULT_TEACHER_VOICE_ID
        if not voice_id:
            st.error("No teacher voice ID configured.")
            return

        filename = f"{audio_basename}.mp3"
        path = elevenlabs_tts_to_file(script, voice_id, filename)
        if path:
            st.success(f"Audio generated: {filename}")
            st.audio(str(path))


# ==========================
# GLOBAL STYLES (BRANDING + UI/UX)
# ==========================
def inject_global_css():
    st.markdown(
        """
<style>
/* Background and typography */
body, .stApp {
  background: radial-gradient(circle at top left, #f3f6ff 0, #eef2f7 40%, #e7edf5 100%);
}

/* Floating menu */
.floating-menu-wrapper {
    position: fixed;
    top: 4.5rem;
    left: 1.4rem;
    z-index: 2000;
    animation: fadeInMenu 0.45s ease-out;
}

@keyframes fadeInMenu {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
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
    gap: 0.35rem;
}

.floating-menu-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.32);
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
    min-width: 230px;
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
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
    color: #4b5563;
}

/* Enlaces */
.menu-link-btn {
    width: 100%;
    display: block;
    text-align: left;
    padding: 0.45rem 0.7rem;
    border-radius: 0.55rem;
    border: none;
    background: transparent;
    cursor: pointer;
    color: #111827;
    font-size: 0.9rem;
    text-decoration: none;
    transition: background 0.12s ease-out, transform 0.1s ease-out;
}

.menu-link-btn:hover {
    background-color: #f1f4fb;
    transform: translateX(1px);
}

.menu-link-btn.active {
    background-color: #1f4b99;
    color: white;
    font-weight: 600;
}

/* Cards / panels */
.block-card {
    background: rgba(255, 255, 255, 0.92);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.18);
    backdrop-filter: blur(8px);
    margin-bottom: 1rem;
}

/* Modo oscuro */
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
}

# (UNITS y LESSONS iguales a tu versión anterior, omitidos por brevedad en comentario.
# Aquí pego la misma estructura que ya tenías, sin cambios en contenido.)

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

# Para no hacer el mensaje infinito, asumimos que la estructura LESSONS
# es la misma que ya tienes (Unit 1–10 con 3 clases cada una).
# Pega aquí tu dict LESSONS completo, sin cambios:


LESSONS = {
    # Pega exactamente tu LESSONS previo aquí
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
# NAVIGATION
# ==========================
PAGES = [
    {"id": "Overview", "label": "Overview", "icon": "🏠"},
    {"id": "English Levels", "label": "Levels", "icon": "📊"},
    {"id": "Assessment & Progress", "label": "Assessment", "icon": "📝"},
    {"id": "Instructor", "label": "Instructor", "icon": "👨‍🏫"},
    {"id": "Enter your class", "label": "Class", "icon": "🎓"},
    {"id": "Access", "label": "Access", "icon": "🔐"},
    {"id": "Teacher Panel", "label": "Teacher", "icon": "📂"},
    {"id": "Admin Dashboard", "label": "Dashboard", "icon": "📊"},
    {"id": "Content Admin", "label": "Content", "icon": "⚙️"},
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
# UNIT 2 – SESSIONS
# (pega aquí tus funciones render_unit2_session* si las necesitas igual)
# ==========================

# ... (tus funciones render_unit2_session1_hour1, etc., sin cambiar) ...


# ==========================
# UNIT 3 – Example of dynamic content + ElevenLabs
# ==========================
def unit3_class1_food_vocabulary():
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
            placeholder="For breakfast I usually eat eggs and tortillas...",
            key="u3c1_warmup",
        )

    with tab2:
        st.subheader("2. Vocabulary – Food words")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Fruits**\n\n- apple\n- banana\n- orange\n- grape\n- pineapple\n- mango")
        with col2:
            st.markdown("**Vegetables**\n\n- tomato\n- carrot\n- onion\n- lettuce\n- potato\n- cucumber")
        with col3:
            st.markdown("**Drinks**\n\n- water\n- juice\n- soda\n- coffee\n- tea\n- milk")
        with col4:
            st.markdown("**Other food**\n\n- bread\n- rice\n- pasta\n- eggs\n- cheese\n- chicken\n- fish")

    with tab3:
        st.subheader("3. Pronunciation – Dynamic script")
        st.markdown("You can store the pronunciation script in **Content Admin** as:")
        st.code("unit = 3, class = 1, key = food_pronunciation", language="text")

        script = load_content_block(3, 1, "food_pronunciation")
        if script:
            st.markdown("#### Current pronunciation script:")
            st.code(script, language="text")
        else:
            st.info("No pronunciation script found yet. Add one in Content Admin.")

        if has_elevenlabs():
            if st.button("Generate pronunciation audio with ElevenLabs (teacher voice)", key="u3c1_gen_audio"):
                voice_id = DEFAULT_TEACHER_VOICE_ID or DEFAULT_STUDENT_VOICE_ID
                if not voice_id:
                    st.error("No voice ID configured (teacher or student).")
                else:
                    filename = "U3_C1_pronunciation_dynamic.mp3"
                    path = elevenlabs_tts_to_file(script or "Food vocabulary.", voice_id, filename)
                    if path:
                        st.success(f"Audio generated: {filename}")
                        st.audio(str(path))
        else:
            st.warning("ElevenLabs API key not configured. Audio generation disabled.")

    with tab4:
        st.subheader("4. Practice – Likes and dislikes")
        st.text_input("1) I like ______ (fruit).", key="u3c1_p1")
        st.text_input("2) I don’t like ______ (vegetable).", key="u3c1_p2")

    with tab5:
        st.subheader("5. Listening – Dynamic dialog")
        st.markdown("Dialog script stored as: key = `supermarket_dialog` (Unit 3, Class 1).")
        render_dynamic_dialog_with_voices(
            unit=3,
            class_number=1,
            content_key="supermarket_dialog",
            teacher_voice_id=DEFAULT_TEACHER_VOICE_ID,
            student_voice_id=DEFAULT_STUDENT_VOICE_ID,
            audio_basename="U3_C1_supermarket_dialog",
        )

    with tab6:
        st.subheader("6. Speaking & wrap-up")
        st.text_area(
            "Write your reflection about what you learned today:",
            key="u3c1_reflection2"
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
            "- Real-world topics: travel, work, culture and health"
        )

    st.markdown("---")
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


def levels_page():
    show_logo()
    st.title("🎯 English Levels (CEFR)")

    data = [
        ["A1", "Beginner", "Can use very basic everyday expressions."],
        ["A2", "Elementary", "Can talk about daily routines, family, simple work, shopping."],
        ["B1", "Intermediate", "Can deal with most situations while travelling."],
        ["B2", "Upper-Intermediate", "Can interact with a good degree of fluency."],
        ["C1", "Advanced", "Can express ideas fluently and spontaneously."],
        ["C2", "Proficiency", "Can understand practically everything."],
    ]
    df = pd.DataFrame(data, columns=["Level", "Name", "Description"])
    st.table(df)


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

    name, email, role = get_current_user()
    if role == "student" and email:
        st.markdown("### Your progress in A2")
        dfp = load_progress_for_user(email)
        if dfp.empty:
            st.info("No progress recorded yet. Mark classes as completed inside each lesson.")
        else:
            summary = (
                dfp[dfp["status"] == "completed"]
                .groupby("unit")["class"]
                .nunique()
                .reset_index()
                .rename(columns={"class": "classes_completed"})
            )
            st.dataframe(summary, use_container_width=True)


def instructor_page():
    show_logo()
    st.title("👨‍🏫 Instructor")
    st.markdown(
        """
**Instructor:** Iván de Jesús Díaz Navarro  
**Profile:** Certified Tourist Guide & English Instructor  

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
            st.success("You are logged in as admin. Go to **Teacher Panel**, **Dashboard** or **Content admin** from the menu.")


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

    with st.expander("Session debug (solo para ti)"):
        st.json(st.session_state.get("auth", {}))

    name, email, role = get_current_user()

    if role != "admin":
        st.error("This area is only for admin.")
        st.markdown(
            "If you are the admin, please enter your **admin access code** here "
            "so you don't need to go back to the Access page."
        )

        code_local = st.text_input(
            "Admin access code",
            type="password",
            key="content_admin_code",
        )

        if st.button("Enter as admin here", key="content_admin_btn"):
            if code_local == ADMIN_ACCESS_CODE:
                if "auth" not in st.session_state:
                    st.session_state["auth"] = {
                        "logged_in": False,
                        "role": "guest",
                        "name": "",
                        "email": "",
                    }

                st.session_state["auth"]["logged_in"] = True
                st.session_state["auth"]["role"] = "admin"
                st.session_state["auth"]["name"] = "Admin"
                st.session_state["auth"]["email"] = "admin@local"
                st.success("✅ Admin access granted from Content Admin.")
                _rerun()
            else:
                st.error("Invalid admin code.")
        return

    # Panel de contenido
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


def admin_dashboard_page():
    show_logo()
    st.title("📊 Admin Dashboard – A2 Platform")

    name, email, role = get_current_user()
    if role != "admin":
        st.error("This area is only for admin. Please login in Access → Admin.")
        return

    col_top1, col_top2, col_top3 = st.columns(3)

    # Stats from progress
    if PROGRESS_FILE.exists():
        dfp = pd.read_csv(PROGRESS_FILE)
        total_students = dfp["user_email"].nunique()
        total_records = len(dfp)
    else:
        dfp = pd.DataFrame(columns=["user_email", "unit", "class", "status"])
        total_students = 0
        total_records = 0

    with col_top1:
        st.markdown("#### 👥 Students tracked")
        st.metric(label="Unique students", value=total_students)
    with col_top2:
        st.markdown("#### ✅ Progress records")
        st.metric(label="Records", value=total_records)
    with col_top3:
        st.markdown("#### 📦 Content blocks")
        structure = scan_content_structure()
        total_blocks = sum(len(keys) for unit_data in structure.values() for keys in unit_data.values())
        st.metric(label="Content files", value=total_blocks)

    st.markdown("---")
    st.markdown("### Content overview per unit/class")

    structure = scan_content_structure()
    rows = []
    for unit_num, classes in structure.items():
        for class_num, keys in classes.items():
            rows.append([unit_num, class_num, ", ".join(keys)])

    if rows:
        df_struct = pd.DataFrame(rows, columns=["Unit", "Class", "Content keys"])
        st.dataframe(df_struct.sort_values(["Unit", "Class"]), use_container_width=True)
    else:
        st.info("No content files saved yet in the Content Admin.")

    st.markdown("---")
    st.markdown("### Progress by unit (completed classes)")

    if not dfp.empty:
        dfp_completed = dfp[dfp["status"] == "completed"]
        summary = (
            dfp_completed.groupby("unit")["class"]
            .nunique()
            .reset_index()
            .rename(columns={"class": "classes_completed"})
        )
        st.dataframe(summary, use_container_width=True)
    else:
        st.info("No progress data yet.")

    st.markdown("---")
    st.markdown("### Recent progress records (last 20)")
    if not dfp.empty:
        st.dataframe(
            dfp.sort_values("timestamp", ascending=False).head(20),
            use_container_width=True
        )


def lessons_page():
    show_logo()
    st.title("📖 Enter your class")

    name, email, role = get_current_user()
    completed = get_completed_classes_for_user(email) if email else set()

    unit_options = [f"Unit {u['number']} – {u['name']}" for u in UNITS]
    unit_choice = st.selectbox("Choose your unit", unit_options)
    unit_number = UNITS[unit_options.index(unit_choice)]["number"]

    st.markdown(f"### {unit_choice}")
    if email:
        st.caption(f"Progress for {email}: completed classes highlighted below.")

    lessons = LESSONS.get(unit_number, [])
    if not lessons:
        st.info("No lessons defined for this unit yet.")
        return

    lesson_titles = [l["title"] for l in lessons]
    lesson_choice = st.selectbox("Choose your lesson", lesson_titles)
    lesson_index = lesson_titles.index(lesson_choice) + 1  # Class number (1–3)

    # Show progress chips
    st.markdown("#### Your classes in this unit:")
    cols = st.columns(len(lessons))
    for i, l in enumerate(lessons, start=1):
        label = f"Class {i}"
        if (unit_number, i) in completed:
            cols[i - 1].success(label)
        else:
            cols[i - 1].button(label, disabled=True, key=f"chip_{unit_number}_{i}")

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

    # Bloques especiales:
    if unit_number == 2 and "Class 1" in lesson_choice:
        # Aquí llamarías a tus render_unit2_session1_hour1 / hour2
        pass
    elif unit_number == 3 and "Class 1" in lesson_choice:
        st.markdown("---")
        unit3_class1_food_vocabulary()

    # Botón de progreso
    st.markdown("---")
    if role == "student" and email:
        if st.button("✅ Mark this class as completed", key=f"complete_{unit_number}_{lesson_index}"):
            ok = save_progress(email, name, unit_number, lesson_index, "completed")
            if ok:
                st.success("Progress saved. This class is now marked as completed.")
                _rerun()
    else:
        st.info("Login as student in **Access → Student access** to track your progress.")


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
    elif page_id == "Admin Dashboard":
        admin_dashboard_page()
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
