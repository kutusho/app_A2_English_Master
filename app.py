import streamlit as st
import pandas as pd
import os
from pathlib import Path
import streamlit.components.v1 as components  # Para embeber las presentaciones HTML
import datetime as dt
import csv
import textwrap
import requests  # <-- NEW: para llamar a la API de ElevenLabs
import base64
import json
from typing import Optional
from helpers.pexels_client import fetch_pexels_image

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
# Carpeta para contenido dinámico (textos, scripts, etc.)
CONTENT_DIR = BASE_DIR / "content"
CONTENT_DIR.mkdir(exist_ok=True)

# Fallback visual (used when no hero image is available)
_FLUNEX_GRADIENT_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 900' preserveAspectRatio='xMidYMid slice'>
  <defs>
    <linearGradient id='flx' x1='0%' y1='0%' x2='100%' y2='100%'>
      <stop offset='0%' stop-color='#1f4b99' stop-opacity='0.95'/>
      <stop offset='50%' stop-color='#274b8f' stop-opacity='0.9'/>
      <stop offset='100%' stop-color='#0f172a' stop-opacity='0.92'/>
    </linearGradient>
  </defs>
  <rect width='1600' height='900' fill='url(#flx)'/>
  <circle cx='450' cy='280' r='180' fill='rgba(255,255,255,0.08)'/>
  <circle cx='1250' cy='620' r='260' fill='rgba(255,255,255,0.05)'/>
</svg>
""".strip()
FLUNEX_GRADIENT_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(_FLUNEX_GRADIENT_SVG.encode("utf-8")).decode("ascii")

# ElevenLabs API key desde secrets
ELEVEN_API_KEY = st.secrets.get("ELEVEN_API_KEY", None)

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


def logout_user():
    st.session_state["auth"] = {
        "logged_in": False,
        "role": "guest",
        "name": "",
        "email": "",
    }


def ensure_admin_access(
    prefix: str,
    prompt_label: str = "Admin access code",
    button_label: str = "Enter as admin",
    show_gate: bool = True,
) -> bool:
    """
    Shared admin gate to keep auth consistent across pages.
    """
    name, email, role = get_current_user()
    if role == "admin":
        return True

    if show_gate:
        st.error("This area is only for admin.")

    code = st.text_input(prompt_label, type="password", key=f"{prefix}_code")
    if st.button(button_label, key=f"{prefix}_btn"):
        if code == ADMIN_ACCESS_CODE:
            st.session_state["auth"]["logged_in"] = True
            st.session_state["auth"]["role"] = "admin"
            st.session_state["auth"]["name"] = "Admin"
            st.session_state["auth"]["email"] = "admin@local"
            st.success("✅ Admin access granted.")
            st.rerun()
        else:
            st.error("Invalid code")
    return False


def render_user_status_bar():
    """Show current session info on the top-right corner with a logout option."""
    auth = st.session_state.get("auth", {})
    logged_in = auth.get("logged_in", False)
    name = auth.get("name") or auth.get("email") or "Invitado"

    container = st.container()
    _, col_status = container.columns([0.62, 0.38])
    with col_status:
        if logged_in:
            st.markdown(
                f"<div style='text-align:right; margin-bottom:0.2rem;'>"
                f"<span class='status-pill'>Iniciaste sesión como {name}</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            logout_col1, logout_col2 = st.columns([0.3, 0.7])
            with logout_col2:
                if st.button("Cerrar sesión", key="topbar_logout", use_container_width=True):
                    logout_user()
                    st.success("Sesión cerrada.")
                    st.rerun()
        else:
            st.markdown(
                "<div style='text-align:right; margin-bottom:0.2rem;'>"
                "<span class='status-pill'>No has iniciado sesión</span></div>",
                unsafe_allow_html=True,
            )
            st.caption("Ve a Access para registrarte o iniciar sesión.")


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
# CONTENT STORAGE HELPERS
# ==========================

def _normalize_content_key(content_key: str) -> str:
    """
    Normalize and validate the filename/key used for dynamic content.
    Only letters, numbers, underscores and dashes are allowed.
    """
    if not content_key:
        raise ValueError("content_key is required")
    safe_key = "".join(c for c in content_key if c.isalnum() or c in ("_", "-")).strip()
    if not safe_key:
        raise ValueError("content_key is invalid")
    return safe_key


def _content_file_path(unit: int, lesson: int, content_key: str) -> Path:
    """
    Build the path where a content block should be stored.
    Example: content/unit3/class1/audio_intro.txt
    """
    safe_key = _normalize_content_key(content_key)
    return CONTENT_DIR / f"unit{unit}" / f"class{lesson}" / f"{safe_key}.txt"


def save_content_block(unit: int, lesson: int, content_key: str, text: str) -> Path:
    """
    Guarda un bloque de contenido en:
      content/unit<unit>/class<lesson>/<content_key>.txt
    """
    file_path = _content_file_path(unit, lesson, content_key)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text or "")
    return file_path


def load_content_block(unit: int, lesson: int, content_key: str) -> Optional[str]:
    """
    Carga un bloque de contenido. Regresa None si no existe o si la llave es inválida.
    """
    try:
        file_path = _content_file_path(unit, lesson, content_key)
    except ValueError:
        return None

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def structured_content_path(unit: int, lesson: int) -> Path:
    return CONTENT_DIR / f"unit{unit}" / f"class{lesson}" / "content.json"


def load_structured_content(unit: int, lesson: int) -> dict:
    """
    Carga contenido estructurado (JSON) para una clase.
    """
    path = structured_content_path(unit, lesson)
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_structured_content(unit: int, lesson: int, payload: dict) -> Path:
    """
    Guarda contenido estructurado (JSON) para una clase.
    """
    path = structured_content_path(unit, lesson)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = payload or {}
    payload["updated_at"] = dt.datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path

# ==========================
# ElevenLabs helper
# ==========================

def generate_audio_elevenlabs(text: str, voice_id: str, filename: str):
    """
    Genera audio con ElevenLabs (una voz) y lo guarda en AUDIO_DIR/filename.
    Retorna la ruta completa del archivo o None si falla.
    """
    if not ELEVEN_API_KEY:
        st.error("ELEVEN_API_KEY no está configurado en .streamlit/secrets.toml o en Streamlit Cloud.")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": "eleven_turbo_v2",
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            st.error(f"Error ElevenLabs: {resp.status_code} – {resp.text}")
            return None

        AUDIO_DIR.mkdir(exist_ok=True)
        audio_path = AUDIO_DIR / filename
        with open(audio_path, "wb") as f:
            f.write(resp.content)

        return audio_path
    except Exception as e:
        st.error(f"Error llamando a ElevenLabs: {e}")
        return None


# ==========================
# GLOBAL STYLES (BRANDING + DARK MODE FRIENDLY)
# ==========================

def inject_global_css():
    st.markdown(
        """
<style>
:root {
    --flx-primary: #1f4b99;
    --flx-primary-strong: #274b8f;
    --flx-ink: #0f172a;
    --flx-surface: #ffffff;
    --flx-surface-glass: rgba(255, 255, 255, 0.86);
}

body {
    background: #f8fafc;
    color: var(--flx-ink);
}

.flx-shell {
    position: relative;
    padding: 1.25rem;
    border-radius: 1.4rem;
    background-size: cover;
    background-position: center;
    overflow: hidden;
    box-shadow: 0 30px 80px rgba(15, 23, 42, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.24);
    margin-bottom: 1.4rem;
}

.flx-shell::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(140deg, rgba(15, 23, 42, 0.75), rgba(31, 75, 153, 0.55));
    pointer-events: none;
}

.flx-shell__header {
    position: sticky;
    top: 0.6rem;
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.85rem 1rem;
    background: rgba(255, 255, 255, 0.82);
    border-radius: 999px;
    border: 1px solid rgba(31, 75, 153, 0.2);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(12px);
}

.flx-brand {
    display: inline-flex;
    align-items: center;
    gap: 0.85rem;
}

.flx-brand img {
    width: 58px;
    height: 58px;
    object-fit: contain;
    filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.15));
}

.flx-brand__title {
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    color: var(--flx-ink);
}

.flx-brand__subtitle {
    color: #475569;
    font-weight: 600;
    font-size: 0.9rem;
}

.flx-level-pill {
    background: linear-gradient(135deg, var(--flx-primary), var(--flx-primary-strong));
    color: #ffffff;
    padding: 0.4rem 0.85rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.92rem;
    box-shadow: 0 10px 24px rgba(31, 75, 153, 0.35);
}

.flx-shell__card {
    position: relative;
    z-index: 2;
    margin-top: 1.6rem;
    padding: 1.6rem;
    border-radius: 1.2rem;
    background: var(--flx-surface-glass);
    border: 1px solid rgba(31, 75, 153, 0.18);
    box-shadow: 0 25px 60px rgba(15, 23, 42, 0.25);
    backdrop-filter: blur(14px);
    max-width: 780px;
}

.flx-shell__eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #0f172a;
    font-size: 0.82rem;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

.flx-shell__headline {
    font-size: 2rem;
    font-weight: 900;
    color: var(--flx-ink);
    margin-bottom: 0.4rem;
}

.flx-shell__copy {
    font-size: 1.02rem;
    color: #1f2937;
    margin-bottom: 0.8rem;
}

.flx-shell__actions {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
    margin-top: 1.2rem;
}

.flx-action-form {
    margin: 0;
}

.flx-cta {
    width: 100%;
    border: none;
    border-radius: 0.95rem;
    padding: 0.95rem 1rem;
    font-size: 1.05rem;
    font-weight: 800;
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.18s ease, filter 0.18s ease;
}

.flx-cta--primary {
    background: linear-gradient(135deg, var(--flx-primary), var(--flx-primary-strong));
    color: #ffffff;
    box-shadow: 0 16px 35px rgba(31, 75, 153, 0.35);
}

.flx-cta--ghost {
    background: rgba(255, 255, 255, 0.88);
    color: var(--flx-primary);
    border: 1px solid rgba(31, 75, 153, 0.2);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.18);
}

.flx-cta:hover {
    transform: translateY(-1px);
    filter: brightness(1.02);
}

.flx-cta:active {
    transform: translateY(0);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.flx-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.9rem;
    margin: 0.2rem 0 1rem 0;
}

.flx-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(247, 249, 255, 0.9));
    border: 1px solid rgba(31, 75, 153, 0.12);
    border-radius: 1rem;
    padding: 0.9rem 1rem;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
    transition: transform 0.12s ease, box-shadow 0.18s ease;
}

.flx-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 46px rgba(15, 23, 42, 0.12);
}

.flx-card h3 {
    margin-bottom: 0.35rem;
    color: var(--flx-ink);
}

.flx-card p {
    color: #1f2937;
    font-size: 0.96rem;
    margin-bottom: 0;
}

.flx-bullet {
    margin-bottom: 0.35rem;
    font-weight: 600;
    color: var(--flx-ink);
}

.flx-bullet span {
    color: #1f2937;
    font-weight: 500;
}

.flx-note {
    background: rgba(31, 75, 153, 0.08);
    border: 1px solid rgba(31, 75, 153, 0.22);
    border-radius: 0.9rem;
    padding: 0.85rem 1rem;
    color: #0f172a;
    margin: 0.9rem 0;
}

.flx-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255, 255, 255, 0.75);
    color: var(--flx-primary);
    border: 1px solid rgba(31, 75, 153, 0.16);
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
}

.flx-sub-banner {
    position: relative;
    overflow: hidden;
    border-radius: 1rem;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0 1.1rem 0;
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(31, 75, 153, 0.18);
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.16);
}

.flx-sub-banner::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.78), rgba(31, 75, 153, 0.5));
}

.flx-sub-banner__text {
    position: relative;
    z-index: 2;
    color: #ffffff;
}

.flx-sub-banner__headline {
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.flx-sub-banner__caption {
    font-size: 0.98rem;
    opacity: 0.9;
}

@media (max-width: 768px) {
    .flx-shell {
        padding: 1rem;
    }
    .flx-shell__header {
        flex-direction: column;
        align-items: flex-start;
        position: sticky;
    }
    .flx-shell__card {
        padding: 1.2rem;
    }
    .flx-shell__headline {
        font-size: 1.6rem;
    }
}

.app-content-wrapper {
    padding-top: 0.5rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    background: rgba(31, 75, 153, 0.1);
    color: #1f4b99;
    font-weight: 600;
    font-size: 0.85rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    padding-bottom: 0.2rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.1);
}

.stTabs [data-baseweb="tab"] {
    background: rgba(15, 23, 42, 0.05);
    border-radius: 0.6rem;
    padding: 0.35rem 0.9rem;
    font-weight: 600;
    color: #0f172a;
    border: 1px solid transparent;
}

.stTabs [aria-selected="true"][data-baseweb="tab"] {
    background: #1f4b99;
    color: #ffffff;
    border-color: rgba(15, 23, 42, 0.15);
}

.audio-card {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 0.75rem;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.75rem;
    background: rgba(255, 255, 255, 0.6);
}

.audio-card h4 {
    margin-bottom: 0.2rem;
}

.info-card {
    border-radius: 0.9rem;
    padding: 0.85rem;
    background: rgba(31, 75, 153, 0.08);
    border: 1px solid rgba(31, 75, 153, 0.15);
    margin-bottom: 0.8rem;
    font-size: 0.92rem;
}

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
# APP SHELL / HERO
# ==========================

def get_logo_data_uri() -> str:
    """
    Returns a data URI for the Flunex logo to embed it in HTML headers.
    """
    logo_path = BASE_DIR / "assets" / "logo-english-classes.png"
    if not logo_path.exists():
        return ""
    try:
        encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        suffix = logo_path.suffix.lower()
        mime = "image/png" if suffix in {".png", ".apng", ".webp"} else "image/jpeg"
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""


def get_shell_media(query: str = "english learning") -> dict:
    """
    Media for the hero area. Uses Pexels if available, otherwise falls back
    to the local gradient.
    """
    media = fetch_pexels_image(
        query=query,
        fallback_url=FLUNEX_GRADIENT_DATA_URI,
        orientation="landscape",
    )
    media["url"] = media.get("url") or FLUNEX_GRADIENT_DATA_URI
    return media


def render_app_shell():
    hero_media = get_shell_media("english learning")
    hero_url = (hero_media.get("url") or FLUNEX_GRADIENT_DATA_URI).replace("'", "%27")
    logo_uri = get_logo_data_uri()
    logo_html = f'<img src="{logo_uri}" alt="Flunex logo" />' if logo_uri else "<div class='flx-level-pill'>Flunex</div>"

    credit = hero_media.get("attribution") or "English learning · classroom"
    shell_html = textwrap.dedent(
        f"""
<div class="flx-shell" style="background-image: linear-gradient(125deg, rgba(15,23,42,0.78), rgba(31,75,153,0.6)), url('{hero_url}');">
  <div class="flx-shell__header">
    <div class="flx-brand">
      {logo_html}
      <div>
        <div class="flx-brand__title">Flunex · A2 English Master</div>
        <div class="flx-brand__subtitle">Learn, teach and track progress with confidence</div>
      </div>
    </div>
    <div class="flx-level-pill">A2 · Elementary</div>
  </div>

  <div class="flx-shell__card">
    <div class="flx-shell__eyebrow">Welcome</div>
    <div class="flx-shell__headline">Communicate clearly in real situations</div>
    <p class="flx-shell__copy">
      Practical lessons, structured progress and bilingual guidance for tourism, work and everyday life.
      Choose your path below.
    </p>
    <div class="flx-shell__actions">
      <form method="get" class="flx-action-form">
        <input type="hidden" name="page" value="Access" />
        <button type="submit" class="flx-cta flx-cta--primary">I am a student</button>
      </form>
      <form method="get" class="flx-action-form">
        <input type="hidden" name="page" value="Content Admin" />
        <button type="submit" class="flx-cta flx-cta--ghost">I am a teacher / admin</button>
      </form>
    </div>
    <div class="flx-tag">{credit}</div>
  </div>
</div>
"""
    )
    st.markdown(shell_html, unsafe_allow_html=True)


def render_banner(query: str, title: str, caption: str = ""):
    media = fetch_pexels_image(
        query=query,
        fallback_url=FLUNEX_GRADIENT_DATA_URI,
        orientation="landscape",
    )
    url = (media.get("url") or FLUNEX_GRADIENT_DATA_URI).replace("'", "%27")
    credit = media.get("attribution")
    credit_html = f"<span class='flx-tag'>{credit}</span>" if credit else ""
    caption_html = f"<div class='flx-sub-banner__caption'>{caption}</div>" if caption else ""

    st.markdown(
        textwrap.dedent(
            f"""
<div class="flx-sub-banner" style="background-image: linear-gradient(140deg, rgba(15,23,42,0.78), rgba(31,75,153,0.5)), url('{url}');">
  <div class="flx-sub-banner__text">
    <div class="flx-sub-banner__headline">{title}</div>
    {caption_html}
    {credit_html}
  </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


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
        st.rerun()


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
    """Render audio if file exists, else a gentle warning."""
    audio_path = AUDIO_DIR / filename
    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning(f"Audio file not found: `audio/{filename}`")


def render_audio_card(title: str, filename: str, description: Optional[str] = None):
    """Display an audio block with a title and optional description."""
    st.markdown(f"<div class='audio-card'><h4>{title}</h4></div>", unsafe_allow_html=True)
    if description:
        st.caption(description)
    _audio_or_warning(filename)


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


# ==========================
# UNIT 3 – FOOD
# CLASS 1 – FOOD VOCABULARY
# ==========================

def unit3_class1_food_vocabulary():
    """
    A2 – Unit 3: Food · Class 1 – Food vocabulary
    Audio files expected:
      - audio/U3_C1_audio1_food_words.mp3
      - audio/U3_C1_audio2_at_the_supermarket.mp3
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

        render_audio_card("Audio – Food words", "U3_C1_audio1_food_words.mp3")

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

        render_audio_card("Audio – At the supermarket", "U3_C1_audio2_at_the_supermarket.mp3")

        st.markdown("### 5.2 Comprehension questions")
        dialogue_script = load_content_block(3, 1, "u3_c1_supermarket_dialogue")
        with st.expander("Teacher script – supermarket dialogue (from Content Admin)"):
            if dialogue_script:
                st.text(dialogue_script)
            else:
                st.info(
                    "No dialogue saved yet. Go to **Content Admin** → "
                    "Unit 3, Class 1, key `u3_c1_supermarket_dialogue` "
                    "and paste your script there."
                )        
                    

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

    # --------------------------
    # Admin tools – ElevenLabs
    # --------------------------
    name, email, role = get_current_user()
    if role == "admin":
        st.markdown("---")
        st.markdown("### 👨‍🏫 Admin tools – Generate ElevenLabs audios for this class")

        with st.expander("Generate / regenerate Audio 1 – Food words"):
            script1 = st.text_area(
                "Script for Audio 1 (Food words) – paste or edit your ElevenLabs script here:",
                height=220,
                key="u3_c1_script1"
            )
            if st.button("Generate Audio 1 with ElevenLabs", key="btn_u3_c1_audio1"):
                path = generate_audio_elevenlabs(
                    text=script1,
                    voice_id="RILOU7YmBhvwJGDGjNmP",  # tu voz de teacher
                    filename="U3_C1_audio1_food_words.mp3"
                )
                if path:
                    st.success(f"Audio 1 generated and saved at: {path}")
                    st.audio(str(path))

        with st.expander("Generate / regenerate Audio 2 – At the supermarket"):
            script2 = st.text_area(
                "Script for Audio 2 (At the supermarket) – paste or edit your ElevenLabs script here:",
                height=260,
                key="u3_c1_script2"
            )
            if st.button("Generate Audio 2 with ElevenLabs", key="btn_u3_c1_audio2"):
                path = generate_audio_elevenlabs(
                    text=script2,
                    voice_id="RILOU7YmBhvwJGDGjNmP",  # puedes cambiar la voz si quieres
                    filename="U3_C1_audio2_at_the_supermarket.mp3"
                )
                if path:
                    st.success(f"Audio 2 generated and saved at: {path}")
                    st.audio(str(path))


# ==========================
# UNIT 3 – CLASS 2 – AT THE RESTAURANT (DYNAMIC)
# ==========================

DEFAULT_U3C2_CONTENT = {
    "class_notes": (
        "Target phrases for ordering politely:\n"
        "- Can I have the menu, please?\n"
        "- I would like the chicken soup.\n"
        "- Would you like something to drink?\n"
        "- The bill, please."
    ),
    "listening_dialogue": (
        "Waiter: Good evening. Here is the menu.\n"
        "Customer: Thanks. Can I have the tomato soup and the grilled chicken?\n"
        "Waiter: Of course. Would you like something to drink?\n"
        "Customer: Just water, please.\n"
        "Waiter: Perfect. Anything else?\n"
        "Customer: That's all, thank you."
    ),
    "elevenlabs_script": (
        "[modo: teacher friendly]\n"
        "[velocidad: super extra slow]\n"
        "[pausas largas]\n"
        "[Énfasis en: please]\n"
        "Model a clear restaurant order. Say: Good evening, can I have the menu, please? "
        "Pause. I would like the grilled chicken with vegetables. "
        "Pause. To drink, just water. Finish with a calm thank you."
    ),
    "quiz_json": {
        "questions": [
            {
                "question": "How do you politely ask for the menu?",
                "options": [
                    "Can I have the menu, please?",
                    "Give me the menu.",
                    "Menu now, thanks."
                ],
                "answer": "Can I have the menu, please?"
            },
            {
                "question": "What does the waiter ask about drinks?",
                "options": [
                    "Do you want something to drink?",
                    "You drink now?",
                    "Bring your own drink?"
                ],
                "answer": "Do you want something to drink?"
            }
        ]
    },
}


def _parse_quiz_payload(raw) -> list:
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return []
    if isinstance(raw, dict):
        questions = raw.get("questions") or []
    elif isinstance(raw, list):
        questions = raw
    else:
        return []

    parsed = []
    for item in questions:
        question = item.get("question")
        options = item.get("options") or []
        answer = item.get("answer")
        if question and options and answer:
            parsed.append(
                {
                    "question": question,
                    "options": options,
                    "answer": answer,
                }
            )
    return parsed


def render_unit3_class2_content(content: dict, preview: bool = False):
    notes = content.get("class_notes") or DEFAULT_U3C2_CONTENT["class_notes"]
    dialogue = content.get("listening_dialogue") or DEFAULT_U3C2_CONTENT["listening_dialogue"]
    eleven_script = content.get("elevenlabs_script") or DEFAULT_U3C2_CONTENT["elevenlabs_script"]
    quiz_questions = _parse_quiz_payload(content.get("quiz_json") or DEFAULT_U3C2_CONTENT.get("quiz_json"))
    updated_at = content.get("updated_at")

    st.markdown("### Class notes")
    st.markdown(notes)
    if updated_at:
        st.caption(f"Last updated: {updated_at}")

    tab_dialogue, tab_script, tab_quiz = st.tabs(["🔊 Dialogue & listening", "🎙️ ElevenLabs script", "🧠 Quick quiz"])

    with tab_dialogue:
        st.markdown("#### Dialogue")
        st.text(dialogue)
        st.info("Play your audio file or read this dialogue aloud for listening practice.")

    with tab_script:
        st.markdown("#### Teacher narration script")
        st.text(eleven_script)
        st.caption("Use this script with ElevenLabs. Tags include mode, speed, pauses and emphasis.")

    with tab_quiz:
        if not quiz_questions:
            st.info("No quiz saved yet. Go to Content Admin to add one.")
        else:
            for idx, question in enumerate(quiz_questions):
                key_suffix = "_preview" if preview else ""
                choice = st.radio(
                    question["question"],
                    question["options"],
                    key=f"u3c2_quiz_{idx}{key_suffix}",
                )
                if choice:
                    if choice == question["answer"]:
                        st.success("Correct!")
                    else:
                        st.warning(f"Suggested answer: {question['answer']}")


def unit3_class2_at_restaurant():
    st.title("Unit 3 – Food")
    st.subheader("Class 2 – At the restaurant")
    st.caption("A2 English Master · Flunex")
    render_banner(
        query="food",
        title="At the restaurant",
        caption="Polite requests, menus and clear pronunciation.",
    )

    stored_content = load_structured_content(3, 2)
    has_custom_content = bool(stored_content)
    content = stored_content if has_custom_content else DEFAULT_U3C2_CONTENT

    if not has_custom_content:
        st.info("Custom content is not saved yet. Using the default template below.")
        if st.button("Open Content Admin", key="btn_open_admin_u3c2"):
            go_to_page("Content Admin")

    render_unit3_class2_content(content)


# ==========================
# A2 PROGRAM – CURRICULUM SELECTOR + UNIT 3 CLASS 2 (SNIPPET INTEGRATION)
# ==========================

def get_a2_curriculum():
    return {
        "Unit 1 – Introductions & Routines": {
            "Class 1 – Everyday life": {"renderer": render_placeholder_lesson},
            "Class 2 – Describing people": {"renderer": render_placeholder_lesson},
            "Class 3 – Talking about habits": {"renderer": render_placeholder_lesson},
        },
        "Unit 2 – Travel & Plans": {
            "Class 1 – Getting around": {"renderer": render_placeholder_lesson},
            "Class 2 – Making plans": {"renderer": render_placeholder_lesson},
            "Class 3 – At the hotel": {"renderer": render_placeholder_lesson},
        },
        "Unit 3 – Food": {
            "Class 1 – Food preferences": {"renderer": render_placeholder_lesson},
            "Class 2 – At the restaurant": {"renderer": render_u3_c2_at_the_restaurant},
            "Class 3 – Talking about food you like": {"renderer": render_u3_c3_talking_about_food_you_like},
        },
    }


def render_a2_unit_lesson(default_unit="Unit 3 – Food", default_lesson="Class 2 – At the restaurant"):
    curriculum = get_a2_curriculum()
    units = list(curriculum.keys())
    unit_index = units.index(default_unit) if default_unit in units else 0

    st.markdown("### Choose your unit")
    selected_unit = st.selectbox(
        label="Choose your unit",
        options=units,
        index=unit_index,
        label_visibility="collapsed",
        key="a2_selector_unit",
    )

    lessons = list(curriculum[selected_unit].keys())
    lesson_index = lessons.index(default_lesson) if default_lesson in lessons else 0

    st.markdown("### Choose your lesson")
    selected_lesson = st.selectbox(
        label="Choose your lesson",
        options=lessons,
        index=lesson_index,
        label_visibility="collapsed",
        key="a2_selector_lesson",
    )

    st.divider()
    renderer = curriculum[selected_unit][selected_lesson].get("renderer", render_placeholder_lesson)
    renderer(unit_title=selected_unit, lesson_title=selected_lesson)


def render_placeholder_lesson(unit_title: str, lesson_title: str):
    st.subheader(f"{unit_title} • {lesson_title}")
    st.info("This lesson is not developed yet. Add content by creating a new renderer function like Unit 3 • Class 2.")


def render_u3_c2_at_the_restaurant(unit_title: str, lesson_title: str):
    st.subheader(f"{unit_title} • {lesson_title}")
    render_banner(
        query="food",
        title="At the restaurant",
        caption="Polite requests, menus and clear pronunciation.",
    )

    st.markdown(
        """
**Lesson outcomes (A2):**
- Order food and drinks politely in a restaurant.
- Ask about ingredients, prices, and recommendations.
- Handle common situations (requests, problems, paying the bill).

**Target language:**
- Polite requests: *Could I have…? / Can I get…? / I’d like…*
- Questions: *What do you recommend? / Does it have…? / How much is…?*
- Restaurant phrases: *starter, main course, dessert, bill/check, tip, table for two*
        """
    )

    tabs = st.tabs(
        ["Warm-up", "Vocabulary", "Grammar & Functional Language", "Listening", "Speaking", "Reading", "Writing", "Homework"]
    )

    with tabs[0]:
        st.markdown("#### Warm-up (5–7 min)")
        st.write("Answer these questions:")
        st.checkbox("1) Do you prefer eating at home or eating out?", key="u3c2_warm_1")
        st.checkbox("2) What’s your favorite restaurant? Why?", key="u3c2_warm_2")
        st.checkbox("3) What do you usually order: starter, main course, dessert?", key="u3c2_warm_3")
        st.markdown("**Quick task:** Choose one situation and say one sentence.")
        st.write("- You want a table.\n- You want to order.\n- You want the bill/check.")

    with tabs[1]:
        st.markdown("#### Vocabulary: Restaurant words & phrases")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Menu sections**")
            st.write("- starter / appetizer\n- main course\n- side dish\n- dessert\n- drinks / beverages")
            st.markdown("**People & places**")
            st.write("- waiter / waitress / server\n- chef\n- table / booth\n- reservation")
        with col2:
            st.markdown("**Actions**")
            st.write("- order\n- recommend\n- pay\n- tip\n- split the bill")
            st.markdown("**Useful phrases**")
            st.write("- *A table for two, please.*\n- *Could we see the menu?*\n- *Could I have the bill/check, please?*")
        with st.expander("Mini-practice (matching)"):
            st.write("Match the phrases to the meaning (say them out loud).")
            st.write("1) *I’d like…* → (A) asking for the price / (B) requesting an item")
            st.write("2) *What do you recommend?* → (A) asking for a suggestion / (B) asking for the bill")
            st.write("3) *Could we have the bill/check?* → (A) paying / (B) ordering")

    with tabs[2]:
        st.markdown("#### Grammar & Functional Language: Polite requests")
        st.markdown(
            """
Use polite forms to sound friendly and professional:

- **Can I get…?** (common, polite)
- **Could I have…?** (more polite)
- **I’d like…** (very common)
- **Could you…?** (requests to the server)

Examples:
- *Could I have the grilled chicken, please?*
- *Can I get a glass of water?*
- *I’d like the vegetable soup.*
- *Could you bring some extra napkins, please?*
            """
        )
        with st.expander("Controlled practice (fill the gaps)"):
            st.write("Complete the sentences:")
            st.write("1) ______ I have the menu, please?")
            st.write("2) I’d ______ the pasta, please.")
            st.write("3) Can I ______ a coffee?")
            st.write("4) Could you ______ the bill/check, please?")

    with tabs[3]:
        st.markdown("#### Listening (8–10 min)")
        st.write("If you have an audio file, place it here. Otherwise, read the dialogue first, then role-read it.")
        st.markdown("**Dialogue (model):**")
        st.markdown(
            """
**Server:** Good evening. Do you have a reservation?  
**Customer:** No, we don’t. A table for two, please.  
**Server:** Of course. This way, please. Here are the menus.  
**Customer:** Thank you. What do you recommend?  
**Server:** Our grilled fish is very popular.  
**Customer:** Sounds good. Could I have the grilled fish, please?  
**Server:** Sure. And to drink?  
**Customer:** Can I get a lemonade, please?  
**Server:** Absolutely.  
**Customer:** Excuse me—does the fish have any nuts?  
**Server:** No, it doesn’t.  
**Customer:** Great. And could we have the bill/check, please?  
**Server:** Certainly.
            """
        )
        with st.expander("Comprehension questions"):
            st.write("1) How many people are there?")
            st.write("2) What does the customer order?")
            st.write("3) What allergy question does the customer ask?")
            st.write("4) What does the customer ask at the end?")

    with tabs[4]:
        st.markdown("#### Speaking (10–15 min): Juego de roles")
        st.write("Do 2 rounds. Switch roles.")
        st.markdown("**Role A (Customer):**")
        st.write("- You want a table.\n- Ask for a recommendation.\n- Order a main course and a drink.\n- Ask one question about ingredients.\n- Ask for the bill/check.")
        st.markdown("**Role B (Server):**")
        st.write("- Greet the customer.\n- Offer a table.\n- Recommend a dish.\n- Confirm the order.\n- Answer the ingredients question.\n- Bring the bill/check.")
        with st.expander("Useful sentence starters"):
            st.write("- *A table for…, please.*")
            st.write("- *What do you recommend?*")
            st.write("- *Could I have…?*")
            st.write("- *Does it have…?*")
            st.write("- *Could we have the bill/check, please?*")

    with tabs[5]:
        st.markdown("#### Reading (7–10 min): Mini-menu")
        st.markdown(
            """
**Today’s Menu**

**Starters**
- Tomato soup — $4.50  
- Mixed salad — $5.00  

**Main courses**
- Grilled chicken with rice — $10.50  
- Pasta primavera (vegetarian) — $9.80  
- Grilled fish with vegetables — $12.00  

**Desserts**
- Chocolate cake — $4.90  
- Fruit salad — $4.20  

**Drinks**
- Water — $1.50  
- Lemonade — $2.80  
- Coffee — $2.00  
            """
        )
        with st.expander("Questions"):
            st.write("1) Which main course is vegetarian?")
            st.write("2) How much is the grilled fish?")
            st.write("3) Choose a full meal (starter + main + drink). What’s the total?")

    with tabs[6]:
        st.markdown("#### Writing (8–10 min): Short restaurant dialogue")
        st.write("Write a short dialogue (6–8 lines). Include:")
        st.write("- greeting\n- order (food + drink)\n- one question (ingredients/price)\n- asking for the bill/check")
        st.text_area("Your dialogue:", height=180, key="u3c2_writing_dialogue")

    with tabs[7]:
        st.markdown("#### Homework (10–15 min)")
        st.write("1) Memorize 10 restaurant words from the vocabulary list.")
        st.write("2) Record yourself saying 6 polite requests (your choice).")
        st.write("3) Write a 5-line restaurant review (A2 level):")
        st.write("- Where you went\n- What you ate\n- Price (cheap/expensive)\n- Service (good/bad)\n- Would you recommend it?")

    st.markdown("---")
    st.markdown("### Content Admin: dynamic materials")
    stored_content = load_structured_content(3, 2)
    has_custom_content = bool(stored_content)
    content = stored_content if has_custom_content else DEFAULT_U3C2_CONTENT
    if not has_custom_content:
        st.info("Custom content is not saved yet. Using the default template below.")
        if st.button("Open Content Admin", key="btn_open_admin_u3c2_selector"):
            go_to_page("Content Admin")
    render_unit3_class2_content(content, preview=True)
    st.success("Unit 3 • Class 2 is ready. Add your audio file path later where indicated.")


def render_u3_c3_talking_about_food_you_like(
    unit_title: str = "Unit 3 – Food",
    lesson_title: str = "Class 3 – Talking about food you like"
):
    st.subheader(f"{unit_title} • {lesson_title}")

    st.markdown(
        """
**Lesson outcomes (A2):**
- Talk about food you like and dislike (with reasons).
- Use **love/like/don’t mind/don’t like/hate** + nouns and verbs.
- Ask and answer questions about food preferences politely.

**Target language:**
- *I love sushi.* / *I don’t like spicy food.* / *I don’t mind vegetables.*
- *I like cooking.* / *I hate waiting for food.*
- *My favorite… is… because…* / *I prefer… to…*
        """
    )

    tabs = st.tabs(
        ["Warm-up", "Vocabulary", "Grammar", "Pronunciation", "Listening", "Speaking", "Reading", "Writing", "Homework"]
    )

    with tabs[0]:
        st.markdown("#### Warm-up (5–7 min)")
        st.write("Choose quick answers. Then say a full sentence for each one.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.radio("Sweet or savory?", ["Sweet", "Savory"], key="u3c3_warm_1")
        with c2:
            st.radio("Tea or coffee?", ["Tea", "Coffee"], key="u3c3_warm_2")
        with c3:
            st.radio("Eat out or cook at home?", ["Eat out", "Cook at home"], key="u3c3_warm_3")

        st.markdown("**Speaking prompt (30 seconds):**")
        st.write("Tell me your favorite food and one reason you like it.")

    with tabs[1]:
        st.markdown("#### Vocabulary: Food adjectives + preference verbs")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Taste & texture**")
            st.write("- spicy / mild\n- sweet / salty / sour / bitter\n- crunchy / soft\n- creamy\n- fresh\n- greasy / oily")
            st.markdown("**Cooking methods**")
            st.write("- grilled\n- fried\n- baked\n- boiled\n- steamed")
        with col2:
            st.markdown("**Preference verbs**")
            st.write("- love\n- like\n- enjoy\n- don’t mind\n- don’t like\n- hate")
            st.markdown("**Useful phrases**")
            st.write("- *My favorite dish is…*\n- *I’m not a fan of…*\n- *It’s too… (spicy/salty/sweet).*")

        with st.expander("Quick practice (categorize)"):
            st.write("Put these words into two groups: taste / texture.")
            st.write("**spicy, crunchy, creamy, salty, soft, bitter, fresh, sweet**")

    with tabs[2]:
        st.markdown("#### Grammar (A2): love/like/hate + nouns & -ing")
        st.markdown(
            """
**1) Verb + noun**
- *I love tacos.*  
- *I don’t like onions.*  

**2) Verb + -ing (activity)**
- *I like cooking.*  
- *I hate waiting.*  

**3) Prefer / Would rather**
- *I prefer tea to coffee.*  
- *I’d rather eat at home today.* (more natural for “today/now”)

**4) Because + reason**
- *I like mango because it’s sweet and fresh.*  
            """
        )

        with st.expander("Controlled practice (fill the gaps)"):
            st.write("Complete the sentences with **love / like / don’t mind / don’t like / hate**:")
            st.write("1) I ______ spicy food, but I love mild food.")
            st.write("2) I ______ vegetables. They’re healthy.")
            st.write("3) I ______ cooking at home on weekends.")
            st.write("4) I ______ waiting for a table at restaurants.")

        with st.expander("Error correction"):
            st.write("Fix the mistakes:")
            st.write("1) *I like to eating pizza.*")
            st.write("2) *I prefer coffee than tea.*")
            st.write("3) *I don’t mind eat spicy food.*")

    with tabs[3]:
        st.markdown("#### Pronunciation (5 min): /sp/ and word stress")
        st.write("Repeat and focus on the first sound:")
        st.write("- **sp**icy, **sp**oon, **sp**aghetti")
        st.write("Now stress the strong syllable:")
        st.write("- VE-ge-ta-bles\n- CHO-co-late\n- DES-sert\n- a-PPE-ti-zer")

    with tabs[4]:
        st.markdown("#### Listening (8–10 min)")
        st.write("Option A: Use this dialogue as a listening/role-read. Option B: Add your audio and play it here.")

        st.markdown("**Dialogue (model):**")
        st.markdown(
            """
**A:** What food do you like?  
**B:** I love Mexican food, especially tacos.  
**A:** Nice. Do you like spicy food?  
**B:** I like it, but not too spicy. I don’t like very hot sauces.  
**A:** What’s your favorite drink?  
**B:** I prefer lemonade to soda because it’s refreshing.  
**A:** Do you enjoy cooking?  
**B:** Yes, I like cooking at home on weekends. I hate waiting in long lines at restaurants.
            """
        )

        with st.expander("Comprehension questions"):
            st.write("1) What food does B love?")
            st.write("2) Does B like very hot sauces?")
            st.write("3) What drink does B prefer and why?")
            st.write("4) What does B hate?")

    with tabs[5]:
        st.markdown("#### Speaking (10–15 min): Juego de roles + mini-interview")
        st.write("Round 1: Interview your partner. Round 2: Switch roles.")

        st.markdown("**Questions to ask:**")
        st.write("- What food do you love?")
        st.write("- What food don’t you like? Why?")
        st.write("- Do you prefer sweet or savory food?")
        st.write("- Do you like cooking? What do you like cooking?")
        st.write("- What’s your favorite drink?")

        with st.expander("Answer frames (A2 support)"):
            st.write("- *I love… because…*")
            st.write("- *I don’t like… because it’s too…*")
            st.write("- *I prefer… to…*")
            st.write("- *My favorite… is…*")

        st.markdown("**Challenge:** Use 3 adjectives (spicy, sweet, crunchy, etc.).")

    with tabs[6]:
        st.markdown("#### Reading (7–10 min): Short food post")
        st.markdown(
            """
**Food post**

Hi! My name is Alex. I love Italian food because it’s simple and delicious.  
My favorite dish is pasta with tomato sauce. I also like salads and fresh fruit.  
I don’t like very spicy food, and I hate oily snacks.  
On weekends, I enjoy cooking at home, but I prefer eating out with friends on my birthday.
            """
        )

        with st.expander("Questions"):
            st.write("1) Why does Alex love Italian food?")
            st.write("2) What is Alex’s favorite dish?")
            st.write("3) What food doesn’t Alex like?")
            st.write("4) When does Alex enjoy cooking at home?")

    with tabs[7]:
        st.markdown("#### Writing (8–10 min): My food profile (A2)")
        st.write("Write 6–8 sentences. Include:")
        st.write("- favorite food + reason")
        st.write("- one food you don’t like + reason")
        st.write("- one drink you prefer")
        st.write("- one cooking activity you like/don’t like")

        st.text_area("Write here:", height=220, key="u3c3_writing_profile")

        with st.expander("Model answer (A2)"):
            st.markdown(
                """
I love Mexican food because it’s flavorful. My favorite dish is tacos.  
I like sweet fruit, especially mango. I don’t like very spicy food because it hurts my mouth.  
I prefer lemonade to soda because it’s refreshing.  
I like cooking at home on weekends, but I hate washing a lot of dishes.
                """
            )

    with tabs[8]:
        st.markdown("#### Homework (10–15 min)")
        st.write("1) Vocabulary: Choose 10 words from today and write 10 sentences.")
        st.write("2) Speaking: Record yourself for 45–60 seconds: “My food preferences.”")
        st.write("3) Challenge: Use **prefer…to…** and **because** at least once.")

    st.success("Unit 3 • Class 3 is ready. Add audio with st.audio() when you have the file path.")


# ==========================
# INTERACTIVE CLASS CONFIG (Units 1 & 2)
# ==========================

INTERACTIVE_CLASS_CONTENT = {
    (1, "Class 1 – Personal information"): {
        "unit_number": 1,
        "class_number": 1,
        "class_title": "Class 1 – Personal information",
        "key_prefix": "u1c1",
        "learning_goals": [
            "Use verb be (am / is / are) to introduce yourself and other people.",
            "Ask and answer basic personal questions about name, country and job.",
            "Spell important words such as names or email addresses."
        ],
        "warmup": {
            "title": "Warm-up – Meet & greet",
            "intro": "Imagine you meet a new classmate. Answer the questions:",
            "questions": [
                "What is your full name?",
                "Where are you from?",
                "What do you do (job or studies)?"
            ],
            "placeholder": "Example: My name is Iván. I am from Tuxtla. I am a tourist guide."
        },
        "language_focus": [
            {
                "title": "Verb be – forms",
                "items": [
                    "I am / You are / He is / She is / We are / They are",
                    "Questions: Are you...? Is he...? Where are you from?",
                    "Short answers: Yes, I am. / No, I’m not."
                ]
            },
            {
                "title": "Useful introductions",
                "items": [
                    "Hi, I’m ___ / Nice to meet you!",
                    "This is my friend ___",
                    "I’m from ___ / I live in ___",
                    "I’m a ___ (job/student)."
                ]
            }
        ],
        "practice_prompts": [
            "Write a short introduction (name + city).",
            "Describe one friend or colleague.",
            "Create one question to continue a conversation."
        ],
        "multiple_choice": [
            {
                "question": "Choose the correct sentence.",
                "options": [
                    "She are from Brazil.",
                    "She is from Brazil.",
                    "She am from Brazil."
                ],
                "answer": "She is from Brazil."
            },
            {
                "question": "Complete: ___ you from Mérida?",
                "options": ["Is", "Are", "Do"],
                "answer": "Are"
            }
        ],
        "listening": {
            "title": "Listening – First day in class",
            "description": (
                "Use these audios to model introductions, pronunciation and speaking tasks. "
                "Play them in order to guide students through the activity."
            ),
            "audio_sections": [
                {"title": "Audio 1 – Welcome & instructions", "file": "unit1_hour2_welcome.mp3"},
                {"title": "Audio 2 – Sample introductions", "file": "unit1_hour2_sample_intro.mp3"},
                {"title": "Audio 3 – Verb be pronunciation", "file": "unit1_hour2_be_pronunciation.mp3"},
                {"title": "Audio 4 – Speaking task guidance", "file": "unit1_hour2_speaking_task.mp3"},
                {"title": "Audio 5 – Final listening practice", "file": "unit1_hour2_final_listening.mp3"},
                {"title": "Audio 6 – Wrap-up message", "file": "unit1_hour2_wrapup.mp3"},
            ],
            "script_key": "u1_c1_introductions_dialogue",
            "questions": [
                {
                    "question": "Where is Miguel from?",
                    "options": ["Colombia", "Mexico City", "Lima"],
                    "answer": "Mexico City"
                },
                {
                    "question": "What is Ana’s job?",
                    "options": ["Tour guide", "Designer", "Student"],
                    "answer": "Tour guide"
                }
            ],
            "writing_prompt": "Write two sentences introducing Ana and Miguel."
        },
        "speaking": {
            "prompts": [
                "Role play: introduce yourself to a partner.",
                "Present a friend to the group: “This is… He/She is from…”.",
                "Practise spelling your name and email slowly."
            ],
            "reflection": [
                "Today I can introduce myself using verb **be**.",
                "I feel more confident asking basic questions.",
                "One sentence I can use with tourists is..."
            ]
        }
    },
    (1, "Class 2 – Countries & jobs"): {
        "unit_number": 1,
        "class_number": 2,
        "class_title": "Class 2 – Countries & jobs",
        "key_prefix": "u1c2",
        "learning_goals": [
            "Remember at least 12 countries and nationalities.",
            "Use Wh-questions: Where are you from? What do you do?",
            "Talk about different jobs in tourism and services."
        ],
        "warmup": {
            "title": "Warm-up – Around the world",
            "intro": "Write three countries you have visited or want to visit.",
            "questions": [
                "Which countries receive tourists in your city?",
                "Which job is popular in your family?",
                "What job would you like to try in the future?"
            ],
            "placeholder": "Example: I want to visit Canada, Peru and Spain."
        },
        "language_focus": [
            {
                "title": "Countries & nationalities",
                "items": [
                    "Mexico – Mexican · Brazil – Brazilian",
                    "Canada – Canadian · United States – American",
                    "Japan – Japanese · France – French"
                ]
            },
            {
                "title": "Jobs",
                "items": [
                    "tour guide · receptionist · chef · driver",
                    "teacher · student · entrepreneur",
                    "I work as a ___ / I’m between jobs."
                ]
            }
        ],
        "practice_prompts": [
            "Write one sentence: 'I’m ___ and I’m from ___.'",
            "Describe a person you know (name, nationality, job).",
            "Create a short survey question for the class."
        ],
        "multiple_choice": [
            {
                "question": "Choose the correct nationality:",
                "options": ["Spainish", "Spanish", "Spannish"],
                "answer": "Spanish"
            },
            {
                "question": "Complete: What ___ you do?",
                "options": ["do", "are", "does"],
                "answer": "do"
            }
        ],
        "listening": {
            "title": "Listening – At a travel fair",
            "description": "Play these audios to guide students from model introductions to the final group task.",
            "audio_sections": [
                {"title": "Audio 1 – Welcome", "file": "U1_S2_audio1_welcome.mp3"},
                {"title": "Audio 2 – Question patterns", "file": "U1_S2_audio2_question_patterns.mp3"},
                {"title": "Audio 3 – Short dialogues", "file": "U1_S2_audio3_short_dialogues.mp3"},
                {"title": "Audio 4 – Group introduction", "file": "U1_S2_audio4_group_introduction.mp3"},
                {"title": "Audio 5 – Final task instructions", "file": "U1_S2_audio5_final_task.mp3"},
                {"title": "Bonus audio – Countries practice", "file": "unit1_hour2_countries.mp3"},
                {"title": "Bonus audio – Jobs vocabulary", "file": "unit1_hour2_jobs.mp3"},
            ],
            "script_key": "u1_c2_travel_fair_script",
            "questions": [
                {
                    "question": "Where is Elena from?",
                    "options": ["Chile", "Spain", "Argentina"],
                    "answer": "Chile"
                },
                {
                    "question": "What does Ken do?",
                    "options": ["Pilot", "Hotel manager", "Photographer"],
                    "answer": "Photographer"
                }
            ],
            "writing_prompt": "Write one dialogue with a tourist: ask country + job."
        },
        "speaking": {
            "prompts": [
                "Play 'Find someone who...' (find a colleague with a specific job).",
                "Explain what jobs are important in your company.",
                "Compare two nationalities that visit your area."
            ],
            "reflection": [
                "New words I learned today...",
                "I can now ask tourists about their job/country.",
                "One strategy to remember nationalities is..."
            ]
        }
    },
    (1, "Class 3 – People you know"): {
        "unit_number": 1,
        "class_number": 3,
        "class_title": "Class 3 – People you know",
        "key_prefix": "u1c3",
        "learning_goals": [
            "Review verb be and adjectives to describe people.",
            "Write a short description about friends or family members.",
            "Use Wh-questions (Who, What, Where) to get details."
        ],
        "warmup": {
            "title": "Warm-up – Important people",
            "intro": "Think of three important people in your life.",
            "questions": [
                "Who are they?",
                "Where do they live?",
                "Why are they important to you?"
            ],
            "placeholder": "Example: My brother Luis lives in Cancún. He is funny and patient."
        },
        "language_focus": [
            {
                "title": "Adjectives for people",
                "items": [
                    "friendly · funny · hard-working · creative",
                    "quiet · outgoing · patient · organized"
                ]
            },
            {
                "title": "Question review",
                "items": [
                    "Who is he/she?",
                    "What does he/she do?",
                    "Where is he/she from?"
                ]
            }
        ],
        "practice_prompts": [
            "Describe a family member in two sentences.",
            "Write three adjectives for a colleague.",
            "Make one question to learn more about a classmate."
        ],
        "multiple_choice": [
            {
                "question": "Choose the best adjective: 'My boss is very organized and ___.'",
                "options": ["late", "punctual", "messy"],
                "answer": "punctual"
            },
            {
                "question": "Which sentence is correct?",
                "options": [
                    "Where he is from?",
                    "Where is he from?",
                    "Where from he is?"
                ],
                "answer": "Where is he from?"
            }
        ],
        "listening": {
            "title": "Listening – Talking about family",
            "description": "Use the following audios (intro, description models and final task) to guide your class.",
            "audio_sections": [
                {"title": "Audio 1 – Intro", "file": "U1_S3_audio1_intro.mp3"},
                {"title": "Audio 2 – Adjectives drill", "file": "U1_S3_audio2_adjectives_drill.mp3"},
                {"title": "Audio 3 – Short descriptions", "file": "U1_S3_audio3_short_descriptions.mp3"},
                {"title": "Audio 4 – Long description", "file": "U1_S3_audio4_long_description.mp3"},
                {"title": "Audio 5 – Final task", "file": "U1_S3_audio5_final_task.mp3"},
            ],
            "script_key": "u1_c3_family_story",
            "questions": [
                {
                    "question": "What does Daniela’s dad do?",
                    "options": ["Chef", "Engineer", "Driver"],
                    "answer": "Driver"
                },
                {
                    "question": "How does she describe her mom?",
                    "options": ["Serious and intelligent", "Funny and creative", "Quiet and shy"],
                    "answer": "Funny and creative"
                }
            ],
            "writing_prompt": "Write one short paragraph about someone in your family."
        },
        "speaking": {
            "prompts": [
                "Show a photo (phone) and describe the person to a partner.",
                "Tell a short anecdote about a friend.",
                "Ask three questions about another student’s friend."
            ],
            "reflection": [
                "Today I can describe people using 3+ adjectives.",
                "I can ask follow-up questions to continue conversations.",
                "One expression I will reuse is..."
            ]
        }
    },
    (2, "Class 1 – Daily routines"): {
        "unit_number": 2,
        "class_number": 1,
        "class_title": "Class 1 – Daily routines",
        "key_prefix": "u2c1",
        "learning_goals": [
            "Use present simple to talk about your routine.",
            "Use adverbs of frequency (always, usually, sometimes, never).",
            "Write a short paragraph describing a typical day."
        ],
        "warmup": {
            "title": "Warm-up – My day",
            "intro": "Think about your weekday routine and complete the questions.",
            "questions": [
                "What time do you get up?",
                "What do you do in the morning?",
                "When do you finish work or classes?"
            ],
            "placeholder": "Example: I get up at 6:30, I have coffee and check the news."
        },
        "language_focus": [
            {
                "title": "Present simple + frequency",
                "items": [
                    "I get up at 6:00. / She gets up at 6:00.",
                    "Adverbs: I always start at 8. I usually drink coffee.",
                    "Question order: What time do you...? Do you usually...?"
                ]
            },
            {
                "title": "Useful routine verbs",
                "items": [
                    "wake up · get dressed · go to work · have lunch · finish work · relax",
                    "take the bus · cook dinner · study English"
                ]
            }
        ],
        "practice_prompts": [
            "Write 3 sentences about your morning.",
            "Write 2 sentences about your evening.",
            "Write 1 question to ask a partner about routines."
        ],
        "multiple_choice": [
            {
                "question": "Choose the correct sentence.",
                "options": [
                    "She go to work at 9.",
                    "She goes to work at 9.",
                    "She is go to work at 9."
                ],
                "answer": "She goes to work at 9."
            },
            {
                "question": "Adverb position: 'I ___ have breakfast at home.'",
                "options": ["never", "never do", "do never"],
                "answer": "never"
            }
        ],
        "listening": {
            "title": "Listening – Morning radio show",
            "description": "Use the four audios (intro, vocab, sample routines and frequency) to build the full activity.",
            "audio_sections": [
                {"title": "Audio 1 – Intro", "file": "U2_S1_audio1_intro.mp3"},
                {"title": "Audio 2 – Routines vocabulary", "file": "U2_S1_audio2_routines_vocab.mp3"},
                {"title": "Audio 3 – Two routines", "file": "U2_S1_audio3_two_routines.mp3"},
                {"title": "Audio 4 – Frequency practice", "file": "U2_S1_audio4_frequency.mp3"},
            ],
            "script_key": "u2_c1_morning_script",
            "questions": [
                {
                    "question": "What time does the guest wake up?",
                    "options": ["5:30", "6:30", "7:30"],
                    "answer": "5:30"
                },
                {
                    "question": "What does she do after breakfast?",
                    "options": ["Goes running", "Drives to work", "Checks emails"],
                    "answer": "Checks emails"
                }
            ],
            "writing_prompt": "Write a short note: 'In the morning I..., In the afternoon I...'."
        },
        "speaking": {
            "prompts": [
                "Compare routines with a partner: find two similarities and one difference.",
                "Explain your weekend routine vs weekday routine.",
                "Give advice to a busy tourist: 'You should wake up early because...'"
            ],
            "reflection": [
                "I can talk about my day without translating.",
                "I can use adverbs of frequency correctly.",
                "One action to improve my routine vocabulary is..."
            ]
        },
        "answer_boxes": [
            {
                "session": "S1",
                "hour": "H1",
                "exercise_id": "routine_paragraph",
                "label": "Write your daily routine paragraph"
            },
            {
                "session": "S1",
                "hour": "H2",
                "exercise_id": "listening_notes",
                "label": "Listening notes – Morning radio show"
            }
        ]
    },
    (2, "Class 2 – Free time"): {
        "unit_number": 2,
        "class_number": 2,
        "class_title": "Class 2 – Free time",
        "key_prefix": "u2c2",
        "learning_goals": [
            "Talk about free-time activities using present simple.",
            "Ask and answer questions with Do you...?",
            "Express likes/dislikes with I like / I love / I don’t like."
        ],
        "warmup": {
            "title": "Warm-up – Weekend snapshot",
            "intro": "List three things you normally do on weekends.",
            "questions": [
                "Do you prefer indoor or outdoor activities?",
                "Who do you spend your free time with?",
                "What new activity would you like to try?"
            ],
            "placeholder": "Example: On Saturdays I visit my parents and cook."
        },
        "language_focus": [
            {
                "title": "Free-time vocabulary",
                "items": [
                    "go hiking · watch series · play football · read · take photos · travel",
                    "relax at home · visit family · practice yoga · go to the cinema"
                ]
            },
            {
                "title": "Questions & answers",
                "items": [
                    "Do you play any sports? – Yes, I do / No, I don’t.",
                    "What do you like doing on Sundays?",
                    "How often do you go out with friends?"
                ]
            }
        ],
        "practice_prompts": [
            "Write 2 sentences with 'I like / I love / I don’t like'.",
            "Describe a free-time activity in detail.",
            "Write one question to invite someone to do something."
        ],
        "multiple_choice": [
            {
                "question": "Choose the correct short answer: 'Do you watch movies on Fridays?'",
                "options": ["Yes, I am.", "Yes, I do.", "Yes, I watch."],
                "answer": "Yes, I do."
            },
            {
                "question": "Which sentence is correct?",
                "options": [
                    "I enjoy to cook.",
                    "I enjoy cooking.",
                    "I enjoy cook."
                ],
                "answer": "I enjoy cooking."
            }
        ],
        "listening": {
            "title": "Listening – Free-time survey",
            "description": "Introduce the survey with the following audios (intro + interviews + Q&A).",
            "audio_sections": [
                {"title": "Audio 1 – Intro", "file": "U2_S2_audio1_intro.mp3"},
                {"title": "Audio 2 – Three people talk about hobbies", "file": "U2_S2_audio2_three_people.mp3"},
                {"title": "Audio 3 – Questions & answers", "file": "U2_S2_audio3_questions_answers.mp3"},
            ],
            "script_key": "u2_c2_freetime_script",
            "questions": [
                {
                    "question": "What activity is the most popular?",
                    "options": ["Watching TV", "Going to the gym", "Cooking"],
                    "answer": "Watching TV"
                },
                {
                    "question": "How often does Luis play football?",
                    "options": ["Every day", "Twice a week", "Only on holidays"],
                    "answer": "Twice a week"
                }
            ],
            "writing_prompt": "Create a short summary of the survey results."
        },
        "speaking": {
            "prompts": [
                "Plan a weekend with a partner (choose two activities).",
                "Describe a memorable free-time experience.",
                "Interview three classmates: What do you do after work?"
            ],
            "reflection": [
                "I can now keep a conversation about hobbies.",
                "New verbs I can use are...",
                "Next week I will practice by..."
            ]
        },
        "answer_boxes": [
            {
                "session": "S2",
                "hour": "H1",
                "exercise_id": "free_time_email",
                "label": "Write an email about your free time"
            },
            {
                "session": "S2",
                "hour": "H2",
                "exercise_id": "listening_summary",
                "label": "Listening summary – Free-time survey"
            }
        ]
    },
    (2, "Class 3 – Habits & lifestyle"): {
        "unit_number": 2,
        "class_number": 3,
        "class_title": "Class 3 – Habits & lifestyle",
        "key_prefix": "u2c3",
        "learning_goals": [
            "Review frequency expressions and connectors (and, but, because).",
            "Compare routines with another person.",
            "Write a short paragraph about lifestyle habits."
        ],
        "warmup": {
            "title": "Warm-up – Healthy or unhealthy?",
            "intro": "Think about your lifestyle choices.",
            "questions": [
                "Which healthy habit do you have?",
                "Which habit would you like to change?",
                "How do you relax during the week?"
            ],
            "placeholder": "Example: I drink water all day, but I go to bed late."
        },
        "language_focus": [
            {
                "title": "Frequency expressions",
                "items": [
                    "once/twice a week · every day · on weekdays · at weekends",
                    "always · usually · sometimes · rarely · never"
                ]
            },
            {
                "title": "Connectors",
                "items": [
                    "I usually cook at home **because** I like healthy food.",
                    "I go to the gym, **but** I don’t run outside.",
                    "I drink coffee **and** tea every morning."
                ]
            }
        ],
        "practice_prompts": [
            "Write 3 sentences using connectors (and/but/because).",
            "Describe one healthy habit you have.",
            "Compare your routine with another person (We both..., but I...)."
        ],
        "multiple_choice": [
            {
                "question": "Choose the sentence with a connector.",
                "options": [
                    "I go to the park.",
                    "I go to the park because I like fresh air.",
                    "I to the park go."
                ],
                "answer": "I go to the park because I like fresh air."
            },
            {
                "question": "Complete: I ___ eat fast food because I prefer cooking.",
                "options": ["rarely", "rare", "rarely do"],
                "answer": "rarely"
            }
        ],
        "listening": {
            "title": "Listening – Lifestyle podcast",
            "description": "Listen to two friends talking about healthy habits (general story + detail follow-up).",
            "audio_sections": [
                {"title": "Audio 1 – Two lifestyles", "file": "U2_S3_audio1_two_lifestyles.mp3"},
                {"title": "Audio 2 – Details", "file": "U2_S3_audio2_details.mp3"},
            ],
            "script_key": "u2_c3_lifestyle_script",
            "questions": [
                {
                    "question": "How often does Leo meditate?",
                    "options": ["Every morning", "Once a week", "Never"],
                    "answer": "Every morning"
                },
                {
                    "question": "Why does Sofia cook at home?",
                    "options": [
                        "Because it is cheaper",
                        "Because she hates restaurants",
                        "Because she doesn’t have time"
                    ],
                    "answer": "Because it is cheaper"
                }
            ],
            "writing_prompt": "Write tips for a balanced lifestyle."
        },
        "speaking": {
            "prompts": [
                "Debate: Which habit is more important – sleep or exercise?",
                "Give advice to a classmate about stress.",
                "Create a two-person dialogue comparing routines."
            ],
            "reflection": [
                "I can connect ideas using and / but / because.",
                "I can describe lifestyle habits confidently.",
                "Next week I will..."
            ]
        },
        "answer_boxes": [
            {
                "session": "S3",
                "hour": "H1",
                "exercise_id": "habit_paragraph",
                "label": "Write about your lifestyle habits"
            },
            {
                "session": "S3",
                "hour": "H2",
                "exercise_id": "reflection_notes",
                "label": "Reflection – What habit will you change?"
            }
        ]
    }
}


def render_interactive_class(config):
    unit_number = config["unit_number"]
    class_number = config["class_number"]
    unit_name = UNITS[unit_number - 1]["name"]
    prefix = config["key_prefix"]

    st.markdown("---")
    st.markdown(f"### 📱 Unit {unit_number} – {unit_name} · {config['class_title']}")
    with st.expander("🎯 Learning goals for this class"):
        for goal in config.get("learning_goals", []):
            st.markdown(f"- {goal}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Warm-up", "Language", "Practice", "Listening", "Speaking & Wrap-up"]
    )

    warmup = config.get("warmup", {})
    with tab1:
        st.subheader(warmup.get("title", "Warm-up"))
        if warmup.get("intro"):
            st.markdown(warmup["intro"])
        for question in warmup.get("questions", []):
            st.markdown(f"- {question}")
        st.text_area(
            "Write your ideas here:",
            key=f"{prefix}_warmup_text",
            placeholder=warmup.get("placeholder", ""),
        )
        choices = warmup.get("choices")
        if choices:
            st.multiselect(
                warmup.get("choices_label", "Select the options that apply:"),
                choices,
                key=f"{prefix}_warmup_choices"
            )
            if warmup.get("choices_prompt"):
                st.info(warmup["choices_prompt"])

    with tab2:
        st.subheader("Key language")
        for block in config.get("language_focus", []):
            st.markdown(f"### {block.get('title', 'Language focus')}")
            for item in block.get("items", []):
                st.markdown(f"- {item}")

    with tab3:
        st.subheader("Practice")
        for idx, prompt in enumerate(config.get("practice_prompts", []), start=1):
            st.text_input(
                f"{idx}) {prompt}",
                key=f"{prefix}_practice_{idx}"
            )

        mc_questions = config.get("multiple_choice", [])
        if mc_questions:
            st.markdown("---")
            st.markdown("### Multiple choice")
            answers_store = []
            for idx, mc in enumerate(mc_questions, start=1):
                response = st.radio(
                    mc["question"],
                    mc["options"],
                    key=f"{prefix}_mc_{idx}"
                )
                answers_store.append((mc["question"], mc["answer"]))

            if st.button("Check answers – Practice", key=f"{prefix}_mc_check"):
                feedback = "\n".join([f"- {q} → **{ans}**" for q, ans in answers_store])
                st.info(f"Suggested answers:\n{feedback}")

        if config.get("answer_boxes"):
            st.markdown("---")
            st.markdown("### Save your work")
            for box in config["answer_boxes"]:
                unit2_answer_box(
                    session=box["session"],
                    hour=box["hour"],
                    exercise_id=box["exercise_id"],
                    label=box["label"],
                )

    with tab4:
        listening = config.get("listening")
        if listening:
            st.subheader(listening.get("title", "Listening"))
            if listening.get("description"):
                st.markdown(listening["description"])

            audio_sections = listening.get("audio_sections")
            if audio_sections:
                for section in audio_sections:
                    title = section.get("title")
                    file_name = section.get("file")
                    description = section.get("description")
                    if file_name:
                        render_audio_card(title or "Audio", file_name, description)
                    else:
                        st.warning("Audio file not specified.")
            else:
                audio_file = listening.get("audio")
                if audio_file:
                    render_audio_card(listening.get("title", "Audio"), audio_file)
                else:
                    st.info("Add your audio file in the Content Admin panel.")

            script_key = listening.get("script_key")
            if script_key:
                script = load_content_block(unit_number, class_number, script_key)
                with st.expander("Teacher script (from Content Admin)"):
                    if script:
                        st.text(script)
                    else:
                        st.info(
                            "No script saved yet. Add it in Content Admin "
                            f"(Unit {unit_number}, Class {class_number}, key `{script_key}`)"
                        )

            listening_questions = listening.get("questions", [])
            answers_feedback = []
            for idx, q in enumerate(listening_questions, start=1):
                st.radio(
                    f"{idx}) {q['question']}",
                    q["options"],
                    key=f"{prefix}_listening_{idx}"
                )
                answers_feedback.append((q["question"], q["answer"]))

            if listening_questions and st.button("Check answers – Listening", key=f"{prefix}_listening_check"):
                summary = "\n".join([f"- {q} → **{ans}**" for q, ans in answers_feedback])
                st.info(f"Suggested key:\n{summary}")

            if listening.get("writing_prompt"):
                st.markdown("---")
                st.markdown("### Listening follow-up")
                st.text_area(
                    listening["writing_prompt"],
                    key=f"{prefix}_listening_followup"
                )
        else:
            st.info("This class does not have a specific listening activity yet.")

    with tab5:
        speaking = config.get("speaking", {})
        st.subheader(speaking.get("title", "Speaking & Wrap-up"))
        st.markdown("### Speaking prompts")
        for prompt in speaking.get("prompts", []):
            st.markdown(f"- {prompt}")

        reflection = speaking.get("reflection", [])
        if reflection:
            st.markdown("### Reflection")
            for item in reflection:
                st.markdown(f"- {item}")
        st.text_area(
            "Write your reflection here:",
            key=f"{prefix}_reflection"
        )
# ==========================
# PAGES
# ==========================

def overview_page():
    render_app_shell()

    st.markdown("### Course snapshot")
    st.markdown(
        """
<div class="flx-card-grid">
  <div class="flx-card">
    <h3>🎯 For whom?</h3>
    <p>Adults and young adults.<br>Tourism, service and business professionals.<br>Learners who finished A1 and want the next step.</p>
  </div>
  <div class="flx-card">
    <h3>📚 What’s inside?</h3>
    <p>10 carefully structured units.<br>Clear grammar and vocabulary focus.<br>Step-by-step lessons with theory, practice and insights.<br>Progress checks and final assessment.</p>
  </div>
  <div class="flx-card">
    <h3>🌍 Why this course?</h3>
    <p>Based on Cambridge Empower A2 (Second Edition).<br>Strong focus on speaking and listening.<br>Real-world topics: travel, work, culture and health.<br>Designed by Iván Díaz, Tourist Guide & English Instructor.</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### What you gain")
    st.markdown(
        """
- Speak about life, work, studies and travel plans in clear, simple English.  
- Understand real conversations at normal speed in common situations.  
- Write short emails, messages and descriptions with correct grammar.  
- Build a solid base to move confidently to **B1 – Intermediate**.
        """
    )
    st.markdown(
        "<div class='flx-note'>Real content, bilingual guidance and progress-friendly tasks adapted for tourism and service contexts.</div>",
        unsafe_allow_html=True,
    )

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
    if st.button("Start your first class", use_container_width=True, key="cta_start_class"):
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

    if st.session_state.get("registration_success"):
        message = st.session_state.get(
            "registration_message",
            "Registration successful! Welcome to your first class."
        )
        st.success(message)
        st.session_state.pop("registration_success", None)
        st.session_state.pop("registration_message", None)

    unit_options = [f"Unit {u['number']} – {u['name']}" for u in UNITS]
    unit_choice = st.selectbox("Choose your unit", unit_options)
    unit_index = unit_options.index(unit_choice)
    unit_number = UNITS[unit_index]["number"]

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

    interactive_config = INTERACTIVE_CLASS_CONTENT.get((unit_number, lesson_choice))
    if interactive_config:
        render_interactive_class(interactive_config)

    # --- UNIT 3 – Class 1 special mobile class ---
    if unit_number == 3 and lesson_choice == "Class 1 – Food vocabulary":
        st.markdown("---")
        st.markdown("### 📱 Unit 3 – Session 1 · Mobile class")
        unit3_class1_food_vocabulary()
    elif unit_number == 3 and lesson_choice == "Class 2 – At the restaurant":
        st.markdown("---")
        render_u3_c2_at_the_restaurant(
            unit_title=f"Unit {unit_number} – {UNITS[unit_number - 1]['name']}",
            lesson_title=lesson_choice,
        )
    elif unit_number == 3 and lesson_choice == "Class 3 – Talking about food you like":
        st.markdown("---")
        render_u3_c3_talking_about_food_you_like(
            unit_title=f"Unit {unit_number} – {UNITS[unit_number - 1]['name']}",
            lesson_title=lesson_choice,
        )

    with st.expander("Try the A2 program selector (beta)"):
        render_a2_unit_lesson()


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
    render_banner(
        query="study",
        title="Access for students and teachers",
        caption="Keep your progress and admin tools in sync across sessions.",
    )

    st.subheader("Register to start learning")
    st.write(
        "Fill in this quick form to activate your access. Once you finish, we will "
        "show you a success message and take you automatically to your first class."
    )
    st.info("Tus datos se guardan solo en este dispositivo. Puedes actualizar tu nombre o meta cuando entres de nuevo.")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
    with col2:
        goal = st.text_area("Why are you studying English? (optional)", key="reg_goal", height=100)

    if st.button("Create account & go to your first class", key="reg_btn", use_container_width=True):
        if name and email:
            st.session_state["auth"]["logged_in"] = True
            st.session_state["auth"]["role"] = "student"
            st.session_state["auth"]["email"] = email
            st.session_state["auth"]["name"] = name
            st.session_state["registration_success"] = True
            st.session_state["registration_message"] = f"Welcome, {name}! Registration successful."
            go_to_page("Enter your class")
        else:
            st.error("Please write at least your name and email.")

    if st.session_state["auth"]["logged_in"]:
        st.info(
            f"Current user: **{st.session_state['auth']['name']}** "
            f"({st.session_state['auth']['email']})"
        )
        if st.button("Logout", key="logout_btn"):
            logout_user()
            st.success("Logged out.")

    st.markdown("---")
    st.subheader("Admin access (teacher only)")
    st.write("Only for teacher / administrator.")

    if ensure_admin_access(
        prefix="access_admin",
        prompt_label="Admin access code",
        button_label="Enter as admin",
        show_gate=False,
    ):
        st.success("✅ Admin access granted. You can now open Teacher or Content Admin.")


def teacher_panel_page():
    show_logo()
    st.title("📂 Teacher Panel – Unit 2 answers")

    # Estado actual de sesión
    name, email, role = get_current_user()

    # Si NO es admin, pedimos el código AQUÍ MISMO
    if not ensure_admin_access(prefix="teacher_panel"):
        return  # No seguimos dibujando el panel si aún no es admin

    # Si llegamos aquí, YA somos admin
    st.success(f"You are logged in as admin (**{name or 'Admin'}**).")

    st.markdown(
        "Here you can review the answers that students saved for **Unit 2**.\n\n"
        "Data is stored in `responses/unit2_responses.csv` on the server."
    )
    st.markdown(
        "<div class='info-card'>Consejo: Usa los filtros de la barra lateral para enfocarte en "
        "una sesión o estudiante. Los datos nuevos aparecen automáticamente cuando los "
        "estudiantes guardan sus respuestas.</div>",
        unsafe_allow_html=True,
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

        total_answers = len(df)
        total_students = df["user_email"].nunique()
        st.markdown("### Overview")
        col_a, col_b = st.columns(2)
        col_a.metric("Total saved answers", total_answers)
        col_b.metric("Unique students", total_students)

        with st.sidebar:
            st.header("🎯 Teacher filters")
            st.caption("Selecciona la sesión y los estudiantes que quieres revisar.")
            sessions = sorted(df["session"].unique())
            session_options = ["All sessions"] + sessions
            session_choice = st.selectbox("Session", session_options, index=0)

            filtered = df.copy()
            if session_choice != "All sessions":
                filtered = filtered[filtered["session"] == session_choice]

            emails = sorted(filtered["user_email"].unique())
            email_filter = st.multiselect("Filter by student (optional)", emails)

        if email_filter:
            filtered = filtered[filtered["user_email"].isin(email_filter)]

        st.markdown("### Answers table")
        if filtered.empty:
            st.info("No answers match the selected filters.")
        else:
            st.dataframe(
                filtered.sort_values("timestamp", ascending=False),
                use_container_width=True,
            )

            st.markdown("### Individual responses")
            for _, row in filtered.sort_values("timestamp", ascending=False).iterrows():
                header = f"{row.get('timestamp','')} – {row.get('user_name','(no name)')} ({row.get('session','')}/{row.get('hour','')}, {row.get('exercise_id','')})"
                with st.expander(header):
                    st.write(row["response"] or "_(empty response)_")
    except Exception as e:
        st.error(f"Error loading answers: {e}")


# ==========================
# PAGE ROUTER
# ==========================

def render_page(page_id: str):
    render_user_status_bar()
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

def content_admin_page():
    show_logo()
    render_banner(
        query="classroom",
        title="Content Admin",
        caption="Keep scripts, dialogues and quizzes in sync across the app.",
    )
    st.title("⚙️ Content Admin – Dynamic updates")

    # Estado de autenticación actual
    if not ensure_admin_access(prefix="content_admin", button_label="Enter as admin here"):
        return

    name, email, role = get_current_user()
    st.success(
        f"You are logged in as admin (**{name or 'Admin'}**). "
        "Use this panel to manage dynamic content."
    )

    st.markdown(
        """
Use this panel to **paste class content and dialogues**.  
The app will read them automatically from disk.

They are stored as text files in:

`content/unit<unit>/class<class>/<content_key>.txt`

You can use this for:

- ElevenLabs scripts  
- Listening / dialogue texts  
- Extra class content (instructions, quizzes, etc.)
        """
    )

    with st.expander("General text blocks (legacy tools)", expanded=False):
        st.markdown("#### 1. Select where to save / load")
        col1, col2, col3 = st.columns(3)
        with col1:
            unit = st.number_input(
                "Unit number",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
                key="content_unit",
            )
        with col2:
            lesson = st.number_input(
                "Class number",
                min_value=1,
                max_value=3,
                value=1,
                step=1,
                key="content_lesson",
            )
        with col3:
            content_type = st.selectbox(
                "Content type",
                [
                    "elevenlabs_script",
                    "listening_dialogue",
                    "class_notes",
                    "extra_text",
                ],
                index=0,
                help=(
                    "This is only a label to help you organize. "
                    "You can create more keys later if needed."
                ),
                key="content_type",
            )

        content_key = st.text_input(
            "Content key (filename, without .txt)",
            value=content_type,
            key="content_key",
            help="Example: 'u3_c1_supermarket_dialogue' or 'u3_c1_audio_intro'",
        )

        st.markdown("#### 2. Content editor")

        if st.button("🔄 Load existing content (if any)", key="load_dyn_content"):
            existing = load_content_block(int(unit), int(lesson), content_key)
            if existing is not None:
                st.session_state["content_admin_text"] = existing
                st.success("Existing content loaded into the editor.")
            else:
                st.info("No file found for this Unit/Class/Key yet.")

        content_text = st.text_area(
            "Paste or write your content here:",
            value=st.session_state.get("content_admin_text", ""),
            height=320,
            key="content_admin_text",
        )

        if st.button("💾 Save / update content", key="save_dyn_content"):
            path = save_content_block(int(unit), int(lesson), content_key, content_text)
            st.success(f"Content saved successfully in: `{path}`")

    st.markdown("---")
    st.subheader("Unit 3 – Class 2 · Structured content")
    st.caption("Save class_notes, listening_dialogue, elevenlabs_script and quiz_json to feed the class page.")

    existing_structured = load_structured_content(3, 2)
    defaults = existing_structured if existing_structured else DEFAULT_U3C2_CONTENT

    if existing_structured.get("updated_at"):
        st.caption(f"Last saved: {existing_structured.get('updated_at')}")

    if st.button("🔄 Load saved content", key="load_structured_u3c2"):
        st.session_state["u3c2_notes"] = defaults.get("class_notes", "")
        st.session_state["u3c2_dialogue"] = defaults.get("listening_dialogue", "")
        st.session_state["u3c2_script"] = defaults.get("elevenlabs_script", "")
        st.session_state["u3c2_quiz_text"] = json.dumps(
            defaults.get("quiz_json", {}),
            indent=2,
            ensure_ascii=False,
        )
        st.success("Structured content loaded into the form.")
        st.rerun()

    notes_value = st.session_state.get("u3c2_notes", defaults.get("class_notes", ""))
    dialogue_value = st.session_state.get("u3c2_dialogue", defaults.get("listening_dialogue", ""))
    script_value = st.session_state.get("u3c2_script", defaults.get("elevenlabs_script", ""))
    quiz_text_default = st.session_state.get("u3c2_quiz_text")
    if quiz_text_default is None:
        quiz_text_default = json.dumps(defaults.get("quiz_json", {}), indent=2, ensure_ascii=False)

    notes_value = st.text_area(
        "class_notes",
        value=notes_value,
        height=140,
        key="u3c2_notes",
    )
    dialogue_value = st.text_area(
        "listening_dialogue",
        value=dialogue_value,
        height=160,
        key="u3c2_dialogue",
    )
    script_value = st.text_area(
        "elevenlabs_script",
        value=script_value,
        height=160,
        key="u3c2_script",
    )
    quiz_text = st.text_area(
        "quiz_json (JSON)",
        value=quiz_text_default,
        height=200,
        key="u3c2_quiz_text",
        help="Use a JSON structure with a list of questions including question, options and answer.",
    )

    parsed_quiz = None
    quiz_error = None
    if quiz_text.strip():
        try:
            parsed_quiz = json.loads(quiz_text)
        except Exception as exc:
            quiz_error = str(exc)

    if st.button("💾 Save structured content", key="save_structured_u3c2"):
        if quiz_error:
            st.error(f"Quiz JSON is invalid: {quiz_error}")
        else:
            payload = {
                "class_notes": notes_value,
                "listening_dialogue": dialogue_value,
                "elevenlabs_script": script_value,
                "quiz_json": parsed_quiz if parsed_quiz is not None else [],
            }
            path = save_structured_content(3, 2, payload)
            st.success(f"Structured content saved in: `{path}`")

    st.markdown("#### Preview (student view)")
    if parsed_quiz is None and not quiz_text.strip():
        preview_quiz = []
    else:
        preview_quiz = parsed_quiz if parsed_quiz is not None else defaults.get("quiz_json", [])
    if quiz_error:
        st.warning("Quiz preview uses the last valid data because the JSON is invalid.")

    preview_payload = {
        "class_notes": notes_value,
        "listening_dialogue": dialogue_value,
        "elevenlabs_script": script_value,
        "quiz_json": preview_quiz,
        "updated_at": existing_structured.get("updated_at"),
    }
    render_unit3_class2_content(preview_payload, preview=True)

    with st.expander("Quick debug (current auth)"):
        st.json(st.session_state.get("auth", {}))

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
