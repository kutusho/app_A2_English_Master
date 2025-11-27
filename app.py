import streamlit as st
import pandas as pd
import os

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================
st.set_page_config(
    page_title="A2 English Master",
    page_icon="📘",
    layout="wide"
)

# ==========================
# DATOS DEL CURSO
# ==========================

COURSE_INFO = {
    "title": "A2 Elementary English Course",
    "level": "A2 – Elementary",
    "total_hours": 60,
    "units": 10,
    "hours_per_unit": 6,
    "description": (
        "A communicative A2 course based on the Cambridge Empower Second Edition "
        "Student’s Book (A2). The program develops integrated skills in listening, "
        "speaking, reading and writing, with a strong focus on everyday situations "
        "and practical communication."
    ),
    "target_students": (
        "Adult and young adult learners who already master basic A1 structures "
        "and want to consolidate and expand their English up to A2 level."
    ),
    "general_objectives": [
        "Understand and use everyday expressions related to areas of most immediate relevance.",
        "Communicate in simple and routine tasks requiring a simple and direct exchange of information.",
        "Describe in simple terms aspects of their background, immediate environment and matters in areas of immediate need.",
        "Develop confidence in real-life situations: travel, work, study and social interactions."
    ],
    "methodology": [
        "Communicative approach with emphasis on speaking and listening.",
        "Task-based learning: role plays, pair work and group work.",
        "Use of authentic materials, videos and audio tracks.",
        "Continuous feedback and focus on form (grammar and vocabulary in context)."
    ],
    "assessment": [
        "Unit progress checks every 2 units.",
        "Continuous assessment through class participation and short tasks.",
        "Mid-course written and oral assessment.",
        "Final integrated exam (listening, reading, writing and speaking)."
    ]
}

# ==========================
# UNIDADES (SYLLABUS)
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
# CLASES POR UNIDAD
# ==========================
# 3 clases por unidad: Class 1, Class 2, Class 3
# Cada clase tiene teoría, práctica e insights (tips).

LESSONS = {
    1: [
        {
            "title": "Class 1 – Personal information",
            "theory": [
                "Verb *to be* in the present (affirmative, negative and questions).",
                "Subject pronouns (I, you, he, she, it, we, they).",
                "Basic word order in English sentences."
            ],
            "practice": [
                "Completar diálogos con *am / is / are*.",
                "Presentarte y presentar a un compañero: *This is...*",
                "Juego de tarjetas con países y nacionalidades."
            ],
            "insights": [
                "En inglés casi siempre necesitas sujeto: evita frases sin *I / you / he...*.",
                "Practica decir tu nombre, país y profesión en menos de 20 segundos."
            ]
        },
        {
            "title": "Class 2 – Countries & jobs",
            "theory": [
                "Countries and nationalities (Mexico – Mexican, Brazil – Brazilian, etc.).",
                "Questions with *Where are you from?* and *What do you do?*"
            ],
            "practice": [
                "Encuesta en clase sobre países y trabajos.",
                "Role-play: primera conversación en una conferencia internacional."
            ],
            "insights": [
                "Aprende las nacionalidades de los países que recibes como turistas.",
                "Usa siempre mayúscula en países y nacionalidades."
            ]
        },
        {
            "title": "Class 3 – People you know",
            "theory": [
                "Review of verb *be* and Wh-questions.",
                "Adjetivos básicos para describir personas (friendly, funny, quiet...)."
            ],
            "practice": [
                "Hablar de tres personas importantes en tu vida.",
                "Escribir notas simples sobre amigos o familia."
            ],
            "insights": [
                "Con 10 adjetivos bien dominados puedes describir a casi cualquier persona.",
                "Piensa siempre en ejemplos reales: familia, colegas, turistas."
            ]
        }
    ],
    2: [
        {
            "title": "Class 1 – Daily routines",
            "theory": [
                "Present simple: estructura básica.",
                "Adverbs of frequency (always, usually, sometimes, never)."
            ],
            "practice": [
                "Completar un horario diario con rutinas.",
                "Entrevista en parejas: *What time do you…?*"
            ],
            "insights": [
                "Los adverbios de frecuencia van normalmente antes del verbo principal.",
                "Relaciona tu rutina real para recordar mejor."
            ]
        },
        {
            "title": "Class 2 – Free time",
            "theory": [
                "Present simple in questions and short answers.",
                "Free-time activities vocabulary."
            ],
            "practice": [
                "Encuesta de actividades favoritas.",
                "Crear un pequeño gráfico de barras con resultados (hablando de ellos en inglés)."
            ],
            "insights": [
                "Practicar respuestas cortas ayuda mucho en listening y speaking.",
                "Usa *I like / I love / I don’t like* para sonar más natural."
            ]
        },
        {
            "title": "Class 3 – Habits & lifestyle",
            "theory": [
                "Revisión de expresiones de frecuencia.",
                "Conectores simples: *and, but, because*."
            ],
            "practice": [
                "Escribir un párrafo sobre tu día típico.",
                "Comparar rutinas con un compañero: *We both..., but I..., and he...*"
            ],
            "insights": [
                "Los conectores simples dan fluidez aunque el nivel sea A2.",
                "Piensa en tu verdadero día, no en ejemplos inventados."
            ]
        }
    ],
    3: [
        {
            "title": "Class 1 – Food vocabulary",
            "theory": [
                "Countable vs uncountable nouns.",
                "A / an / some / any."
            ],
            "practice": [
                "Clasificar alimentos en contables e incontables.",
                "Juegos de *shopping list* en parejas."
            ],
            "insights": [
                "No intentes traducir todo: memoriza alimentos directamente en inglés.",
                "Piensa en menús reales de restaurantes donde trabajas o visitas."
            ]
        },
        {
            "title": "Class 2 – At the restaurant",
            "theory": [
                "Questions in restaurants: *Can I have…?*, *Would you like…?*",
                "Polite expressions: *please, thank you, here you are*."
            ],
            "practice": [
                "Role-play mesero/cliente.",
                "Crear un mini-menú para practicar pedidos."
            ],
            "insights": [
                "Ideal para contextos de turismo: usa vocabulario de tu ciudad.",
                "Las expresiones corteses cambian mucho la experiencia del cliente."
            ]
        },
        {
            "title": "Class 3 – Talking about food you like",
            "theory": [
                "Like / love / don’t like + noun or + -ing.",
                "Adjetivos de comida: spicy, sweet, salty, bitter."
            ],
            "practice": [
                "Encuesta sobre comida favorita del grupo.",
                "Escribir un párrafo breve sobre tu platillo favorito."
            ],
            "insights": [
                "Con este vocabulario puedes describir gastronomía local a turistas.",
                "Usa ejemplos típicos de Chiapas para conectar con tu realidad."
            ]
        }
    ],
    4: [
        {
            "title": "Class 1 – My home",
            "theory": [
                "There is / there are.",
                "Some / any con lugares y objetos."
            ],
            "practice": [
                "Dibujar un plano simple de tu casa y describirlo.",
                "Juego de *spot the difference* con dos casas."
            ],
            "insights": [
                "Usa este lenguaje para describir alojamientos a turistas.",
                "Empieza siempre por lo general y luego ve a los detalles."
            ]
        },
        {
            "title": "Class 2 – In the city",
            "theory": [
                "Places in a city.",
                "Prepositions of place (next to, opposite, between...)."
            ],
            "practice": [
                "Dar indicaciones en un mapa sencillo.",
                "Role-play: turista pide direcciones en la ciudad."
            ],
            "insights": [
                "Esta clase es oro puro para guías y personal turístico.",
                "Practica con mapas reales de Tuxtla o San Cristóbal."
            ]
        },
        {
            "title": "Class 3 – Describing places",
            "theory": [
                "Adjetivos de lugares: quiet, busy, modern, traditional.",
                "Structura básica de un párrafo descriptivo."
            ],
            "practice": [
                "Escribir sobre tu barrio o tu ciudad.",
                "Presentar oralmente un lugar turístico de Chiapas."
            ],
            "insights": [
                "Llevar fotos impresas o en el móvil ayuda a activar vocabulario.",
                "Reutiliza este texto como base para guiones de tours."
            ]
        }
    ],
    5: [
        {
            "title": "Class 1 – Regular past",
            "theory": [
                "Past simple regular: afirmativa.",
                "Pronunciación de -ed (/t/, /d/, /ɪd/)."
            ],
            "practice": [
                "Transformar oraciones de presente a pasado.",
                "Juego de *timeline* con eventos personales."
            ],
            "insights": [
                "La pronunciación de -ed marca mucho la diferencia en la fluidez.",
                "Relaciona verbos con momentos importantes de tu vida."
            ]
        },
        {
            "title": "Class 2 – Past questions",
            "theory": [
                "Did + base form.",
                "Short answers: *Yes, I did* / *No, I didn’t*."
            ],
            "practice": [
                "Entrevistas sobre el fin de semana pasado.",
                "Encuesta: *When did you first…?* (travel, work, study English)."
            ],
            "insights": [
                "Aprender preguntas comunes te ayuda a mantener conversaciones reales.",
                "Úsalo en tours para conectar con tus visitantes."
            ]
        },
        {
            "title": "Class 3 – Family stories",
            "theory": [
                "Review of regular past.",
                "Time expressions: yesterday, last week, two years ago."
            ],
            "practice": [
                "Escribir una breve historia familiar.",
                "Contar una anécdota en parejas."
            ],
            "insights": [
                "Las historias personales hacen que el idioma se vuelva significativo.",
                "Usa este tipo de narración para storytelling en turismo."
            ]
        }
    ],
    6: [
        {
            "title": "Class 1 – Free time in the past",
            "theory": [
                "Past simple irregular verbs (go, have, do, see…).",
                "Contraste con presente."
            ],
            "practice": [
                "Tarjetas de matching: base form – past form.",
                "Jugar *Yesterday I...* en círculo."
            ],
            "insights": [
                "Memoriza primero los verbos irregulares más frecuentes.",
                "Crea tus propias tarjetas de estudio."
            ]
        },
        {
            "title": "Class 2 – Days out",
            "theory": [
                "Past simple questions with irregular verbs.",
                "Review of time expressions."
            ],
            "practice": [
                "Hablar de una excursión o viaje reciente.",
                "Role-play: contar tu día libre perfecto."
            ],
            "insights": [
                "Ideal para hablar de experiencias turísticas con clientes.",
                "Usa fotos reales de excursiones que has guiado."
            ]
        },
        {
            "title": "Class 3 – Leisure texts",
            "theory": [
                "Identificar idea general y detalles en textos sencillos.",
                "Conectores básicos para narrar."
            ],
            "practice": [
                "Leer un texto corto sobre tiempo libre y responder preguntas.",
                "Escribir un mini blog entry de fin de semana."
            ],
            "insights": [
                "Leer en voz alta ayuda a fijar estructuras.",
                "Combinar lectura y escritura acelera el progreso."
            ]
        }
    ],
    7: [
        {
            "title": "Class 1 – Jobs & routines",
            "theory": [
                "Job vocabulary.",
                "Present simple vs present continuous (uso básico)."
            ],
            "practice": [
                "Describir tu trabajo actual o ideal.",
                "Juego: adivinar la profesión."
            ],
            "insights": [
                "Conecta vocabulario laboral con tu realidad (guía, hotel, agencia...).",
                "Practica describir lo que haces durante un día de trabajo típico."
            ]
        },
        {
            "title": "Class 2 – Comparisons",
            "theory": [
                "Comparative adjectives: *bigger, more interesting, cheaper*.",
                "Than + noun."
            ],
            "practice": [
                "Comparar ciudades, lugares turísticos o trabajos.",
                "Encuesta: *Which is better…?*"
            ],
            "insights": [
                "Genial para comparar destinos en ventas turísticas.",
                "Aprende bien el patrón: *X is more ... than Y*."
            ]
        },
        {
            "title": "Class 3 – Work profile",
            "theory": [
                "Structura básica de un perfil profesional.",
                "Review of present tenses."
            ],
            "practice": [
                "Escribir tu mini CV en inglés (versión simple).",
                "Presentarte oralmente como profesional."
            ],
            "insights": [
                "Te sirve directamente para LinkedIn o presentaciones con clientes.",
                "Mantén frases cortas pero claras."
            ]
        }
    ],
    8: [
        {
            "title": "Class 1 – Travel plans",
            "theory": [
                "Going to for plans.",
                "Expressions for future time (next week, this weekend...)."
            ],
            "practice": [
                "Hablar de planes de viaje.",
                "Planear un viaje en parejas (destino, transporte, actividades)."
            ],
            "insights": [
                "Muy útil para explicar itinerarios a turistas.",
                "Piensa en viajes reales que ofreces con Bioventura."
            ]
        },
        {
            "title": "Class 2 – At the airport / station",
            "theory": [
                "Common travel questions and answers.",
                "Vocabulary: ticket, boarding pass, platform, gate..."
            ],
            "practice": [
                "Role-play en aeropuerto/estación.",
                "Escuchar anuncios ficticios y completar información."
            ],
            "insights": [
                "Estos diálogos son excelentes para turismo internacional.",
                "Puedes grabar audios propios para practicar listening."
            ]
        },
        {
            "title": "Class 3 – Travel blog",
            "theory": [
                "Paragraph structure for narratives.",
                "Linkers: first, then, after that, finally."
            ],
            "practice": [
                "Leer una entrada de blog de viajes sencilla.",
                "Escribir sobre tu viaje favorito."
            ],
            "insights": [
                "Perfecto para contenido de redes o blogs de agencia.",
                "Piensa en un tour real y conviértelo en historia."
            ]
        }
    ],
    9: [
        {
            "title": "Class 1 – Parts of the body",
            "theory": [
                "Body vocabulary.",
                "Have got (uso básico) si lo necesitas."
            ],
            "practice": [
                "Juegos de señalar partes del cuerpo.",
                "Describir dolores: *My back hurts.*"
            ],
            "insights": [
                "Útil para emergencias con turistas.",
                "Practica frases clave como *Do you need a doctor?*"
            ]
        },
        {
            "title": "Class 2 – Health problems",
            "theory": [
                "Should / shouldn’t for advice.",
                "Common health problems vocabulary."
            ],
            "practice": [
                "Role-play médico/paciente.",
                "Dar consejos a partir de síntomas."
            ],
            "insights": [
                "Ten siempre algunas frases de emergencia memorizadas.",
                "La cortesía y calma son parte del lenguaje también."
            ]
        },
        {
            "title": "Class 3 – Healthy lifestyle",
            "theory": [
                "Review of advice and habits.",
                "Frequency expressions in lifestyle."
            ],
            "practice": [
                "Escribir recomendaciones para una vida saludable.",
                "Debate simple: *What is healthy / unhealthy?*"
            ],
            "insights": [
                "Tema que conecta muy bien con cualquier grupo.",
                "Combina vocabulario de comida, rutinas y salud."
            ]
        }
    ],
    10: [
        {
            "title": "Class 1 – Countries & continents",
            "theory": [
                "Country and continent vocabulary.",
                "Question: *Have you ever been to…?* (introducción ligera al present perfect)."
            ],
            "practice": [
                "Mapa del mundo: marcar países visitados o que quieres visitar.",
                "Preguntas en parejas sobre viajes."
            ],
            "insights": [
                "No necesitas dominar el present perfect, solo usarlo en frases clave.",
                "Enfócate en escucharlo y producirlo en estructuras cortas."
            ]
        },
        {
            "title": "Class 2 – World cultures",
            "theory": [
                "Adjetivos para culturas y lugares (interesting, diverse, ancient...).",
                "Review of past and present."
            ],
            "practice": [
                "Hablar de una cultura que admires.",
                "Comparar tradiciones entre países."
            ],
            "insights": [
                "Conecta esta clase con tu pasión por culturas originarias.",
                "Perfecto para preparar contenido de tours culturales."
            ]
        },
        {
            "title": "Class 3 – My country",
            "theory": [
                "Paragraph structure for descriptions of a country.",
                "Review of key A2 grammar."
            ],
            "practice": [
                "Escribir un texto sobre México para extranjeros.",
                "Presentación oral tipo mini-tour del país."
            ],
            "insights": [
                "Este texto puede servir para tu web, folletos o guiones.",
                "Cierra el curso mostrando todo lo que ya puedes decir en inglés."
            ]
        }
    ]
}

# ==========================
# LOGO Y FIRMA
# ==========================

def show_logo():
    """Show logo in the sidebar if available."""
    logo_path = os.path.join("assets", "logo-english-classes.png")
    if os.path.exists(logo_path):
        try:
            st.sidebar.image(logo_path, use_column_width=True)
        except Exception:
            st.sidebar.warning("El archivo 'logo-english-classes.png' no es una imagen válida.")
    else:
        st.sidebar.info("Coloca el archivo 'logo-english-classes.png' en la carpeta /assets.")

def show_signature():
    """Show signature at the bottom if available."""
    sig_path = os.path.join("assets", "firma-ivan-diaz.png")
    if os.path.exists(sig_path):
        try:
            st.image(sig_path, width=220)
        except Exception:
            st.warning("El archivo 'firma-ivan-diaz.png' no es una imagen válida.")
    else:
        st.info("Coloca el archivo 'firma-ivan-diaz.png' en la carpeta /assets para mostrar tu firma.")

# ==========================
# PÁGINAS
# ==========================

def overview_page():
    st.title("📘 A2 English Master – Course Overview")
    st.subheader(COURSE_INFO["level"])

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Course title:** {COURSE_INFO['title']}")
        st.markdown(f"**Number of units:** {COURSE_INFO['units']}")
        st.markdown(f"**Total hours:** {COURSE_INFO['total_hours']}")
        st.markdown("### Description")
        st.write(COURSE_INFO["description"])

    with col2:
        st.markdown("### Target students")
        st.write(COURSE_INFO["target_students"])

    st.markdown("### General objectives")
    for obj in COURSE_INFO["general_objectives"]:
        st.markdown(f"- {obj}")

    st.markdown("### Methodology")
    for item in COURSE_INFO["methodology"]:
        st.markdown(f"- {item}")

    st.markdown("### Assessment")
    for item in COURSE_INFO["assessment"]:
        st.markdown(f"- {item}")


def levels_page():
    st.title("🎯 English Levels (CEFR)")
    st.markdown("Esta app trabaja el nivel **A2 – Elementary**, dentro del marco **CEFR (Common European Framework of Reference for Languages)**.")

    data = [
        ["A1", "Beginner", "Puede usar expresiones cotidianas muy básicas, presentarse y hacer preguntas simples."],
        ["A2", "Elementary", "Puede hablar de rutina diaria, familia, trabajo sencillo, compras y situaciones inmediatas."],
        ["B1", "Intermediate", "Puede manejar la mayoría de situaciones en viajes, describir experiencias y opiniones simples."],
        ["B2", "Upper-Intermediate", "Puede interactuar con fluidez razonable, entender ideas principales de textos complejos."],
        ["C1", "Advanced", "Puede expresarse con soltura y flexibilidad en contextos académicos y profesionales."],
        ["C2", "Proficiency", "Tiene un dominio del idioma similar al de un hablante nativo culto."]
    ]
    df = pd.DataFrame(data, columns=["Level", "Name", "Description"])
    st.table(df)

    st.markdown("---")
    st.markdown("### 📌 ¿Dónde se ubica este curso?")
    st.success(
        "Este programa corresponde al nivel **A2 – Elementary**.\n\n"
        "- Consolida estructuras básicas de A1.\n"
        "- Amplía vocabulario para la vida diaria, trabajo sencillo y viajes.\n"
        "- Prepara al estudiante para avanzar a **B1 – Intermediate**."
    )


def syllabus_page():
    st.title("📚 Syllabus by Unit")
    unit_names = [f"Unit {u['number']}: {u['name']}" for u in UNITS]
    selected = st.selectbox("Select a unit", unit_names)
    unit = UNITS[unit_names.index(selected)]

    st.markdown(f"## Unit {unit['number']} – {unit['name']}")
    st.markdown(f"**Focus:** {unit['focus']}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Grammar")
        for g in unit["grammar"]:
            st.markdown(f"- {g}")

        st.markdown("### Vocabulary")
        for v in unit["vocabulary"]:
            st.markdown(f"- {v}")

    with col2:
        st.markdown("### Skills")
        for skill, items in unit["skills"].items():
            st.markdown(f"**{skill.capitalize()}**")
            for item in items:
                st.markdown(f"- {item}")

    st.markdown("---")
    st.markdown("### Suggested time distribution")
    df = pd.DataFrame(
        [
            ["Warm-up & presentation", 30],
            ["Grammar & vocabulary input", 60],
            ["Controlled practice", 60],
            ["Communication tasks", 60],
            ["Review & assessment", 30],
        ],
        columns=["Stage", "Minutes"]
    )
    st.table(df)


def lessons_page():
    st.title("📖 Entra a tu clase")

    unit_options = [f"Unit {u['number']} – {u['name']}" for u in UNITS]
    unit_choice = st.selectbox("Selecciona tu unidad", unit_options)
    unit_number = UNITS[unit_options.index(unit_choice)]["number"]

    lessons = LESSONS.get(unit_number, [])
    lesson_titles = [l["title"] for l in lessons]
    lesson_choice = st.selectbox("Selecciona tu clase", lesson_titles)

    lesson = next(l for l in lessons if l["title"] == lesson_choice)

    st.markdown(f"## {lesson['title']}")
    st.caption(f"Unidad {unit_number} – {UNITS[unit_number-1]['name']}")

    tab_theory, tab_practice, tab_insights = st.tabs(["📘 Teoría", "📝 Práctica", "💡 Insights"])

    with tab_theory:
        st.markdown("### Contenidos teóricos")
        for item in lesson["theory"]:
            st.markdown(f"- {item}")

    with tab_practice:
        st.markdown("### Actividades sugeridas")
        for item in lesson["practice"]:
            st.markdown(f"- {item}")
        st.info("Puedes adaptar estas actividades a modalidad presencial, online o trabajo autónomo.")

    with tab_insights:
        st.markdown("### Tips e insights")
        for item in lesson["insights"]:
            st.markdown(f"- {item}")
        st.success("Añade aquí tus propios comentarios, ejemplos o anécdotas para cada grupo.")

def assessment_page():
    st.title("📝 Assessment & Progress")

    st.markdown("### Assessment Structure")
    st.markdown(
        """
- Unit progress checks every 2 units  
- Mid-course assessment (after Unit 5): listening, reading, writing & speaking  
- Final exam (after Unit 10): full integrated assessment  
"""
    )

    st.markdown("### Weighting")
    df = pd.DataFrame(
        [
            ["Class participation", "20%"],
            ["Progress checks", "30%"],
            ["Mid-course test", "20%"],
            ["Final exam", "30%"],
        ],
        columns=["Component", "Weight"]
    )
    st.table(df)


def teacher_page():
    st.title("👨‍🏫 About the Instructor")

    st.markdown(
        """
**Instructor:** Iván de Jesús Díaz Navarro  
**Profession:** Tourist Guide & English Instructor  

This A2 English program integrates a communicative approach with real-life scenarios for students who need English for travel, work, and personal development.
"""
    )

    st.markdown("### Signature")
    show_signature()

# ==========================
# MAIN
# ==========================

def main():
    show_logo()

    st.sidebar.title("Menu")
    page = st.sidebar.radio(
        "Navigate",
        (
            "Overview",
            "English Levels",
            "Syllabus by Unit",
            "Entra a tu clase",
            "Assessment & Progress",
            "Instructor"
        )
    )

    if page == "Overview":
        overview_page()
    elif page == "English Levels":
        levels_page()
    elif page == "Syllabus by Unit":
        syllabus_page()
    elif page == "Entra a tu clase":
        lessons_page()
    elif page == "Assessment & Progress":
        assessment_page()
    elif page == "Instructor":
        teacher_page()


if __name__ == "__main__":
    main()
