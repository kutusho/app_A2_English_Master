import streamlit as st
import pandas as pd
import os

# ==========================
# BASIC CONFIG
# ==========================
st.set_page_config(
    page_title="A2 English Master",
    page_icon="📘",
    layout="wide"
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
# LESSONS BY UNIT (ENGLISH ONLY)
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
    """Show logo at the top if available."""
    logo_path = os.path.join("assets", "logo-english-classes.png")
    if os.path.exists(logo_path):
        try:
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(logo_path, use_column_width=True)
            with cols[1]:
                st.markdown(" ")  # spacer
        except Exception:
            st.warning("The file 'logo-english-classes.png' exists but is not a valid image.")
    else:
        st.info("Add your logo as 'assets/logo-english-classes.png' to display it here.")

def show_signature():
    """Show signature on instructor page if available."""
    sig_path = os.path.join("assets", "firma-ivan-diaz.png")
    if os.path.exists(sig_path):
        try:
            st.image(sig_path, width=220)
        except Exception:
            st.warning("The file 'firma-ivan-diaz.png' exists but is not a valid image.")
    else:
        st.info("Add your signature as 'assets/firma-ivan-diaz.png' to display it here.")

# ==========================
# NAVIGATION CONFIG
# ==========================

PAGES = [
    {"id": "Overview", "label": "Overview", "icon": "🏠"},
    {"id": "English Levels", "label": "Levels", "icon": "📊"},
    {"id": "Assessment & Progress", "label": "Assessment", "icon": "📝"},
    {"id": "Instructor", "label": "Instructor", "icon": "👨‍🏫"},
    {"id": "Enter your class", "label": "Class", "icon": "🎓"},
]

def _get_query_params():
    """Safe wrapper to get query params for different Streamlit versions."""
    try:
        # Newer versions
        params = dict(st.query_params)
    except Exception:
        # Older experimental API
        params = st.experimental_get_query_params()
    return params

def get_current_page_id() -> str:
    """Read current page from URL query params (?page=...)."""
    params = _get_query_params()
    page = params.get("page")

    # page may be a list (old API) or a string (new API)
    if isinstance(page, list):
        page = page[0] if page else None

    valid_ids = [p["id"] for p in PAGES]

    if not page or page not in valid_ids:
        return "Overview"
    return page

def _rerun():
    """Compatibility wrapper for rerun."""
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

def go_to_page(page_id: str):
    """Programmatically navigate to a page by updating query params."""
    valid_ids = [p["id"] for p in PAGES]
    if page_id not in valid_ids:
        page_id = "Overview"

    try:
        # New-style API
        st.query_params["page"] = page_id
    except Exception:
        # Older API
        st.experimental_set_query_params(page=page_id)

    _rerun()

def render_floating_menu(current_page_id: str):
    """Render a fixed floating menu in the top-left corner, clearly visible."""
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
    <style>
    .floating-menu-wrapper {{
        position: fixed;
        /* Lo bajamos más para que no se recorte con el header de Streamlit */
        top: 4.5rem;
        left: 1.5rem;
        z-index: 2000;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .floating-menu-toggle {{
        display: none;
    }}

    .floating-menu-button {{
        background: linear-gradient(135deg, #1f4b99, #274b8f);
        color: #ffffff;
        border-radius: 999px;
        padding: 0.55rem 1.4rem;
        font-size: 0.95rem;
        font-weight: 600;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        border: none;
        user-select: none;
        white-space: nowrap;
    }}

    .floating-menu-button:hover {{
        filter: brightness(1.05);
    }}

    .floating-menu-panel {{
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
    }}

    .floating-menu-header {{
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #555;
        margin-bottom: 0.4rem;
        padding: 0 0.2rem;
    }}

    .menu-link {{
        display: block;
        padding: 0.4rem 0.5rem;
        border-radius: 0.55rem;
        text-decoration: none;
        font-size: 0.9rem;
        color: #222;
        margin-bottom: 0.15rem;
    }}

    .menu-link:hover {{
        background-color: #f1f4fb;
    }}

    .menu-link.active {{
        background-color: #1f4b99;
        color: #ffffff;
        font-weight: 600;
    }}

    /* Toggle behaviour */
    .floating-menu-toggle:checked ~ .floating-menu-panel {{
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0);
    }}

    /* Small screens */
    @media (max-width: 600px) {{
        .floating-menu-wrapper {{
            top: 4rem;
            left: 1rem;
        }}
        .floating-menu-button {{
            padding: 0.45rem 1.1rem;
            font-size: 0.9rem;
        }}
        .floating-menu-panel {{
            min-width: 200px;
        }}
    }}
    </style>

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
# PAGES
# ==========================

def overview_page():
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

def syllabus_page():
    st.title("📚 Syllabus by Unit")

    unit_names = [f"Unit {u['number']}: {u['name']}" for u in UNITS]
    selected = st.selectbox("Select a unit", unit_names)
    unit = UNITS[unit_names.index(selected)]

    st.markdown(f"## Unit {unit['number']} – {unit['name']}")
    st.markdown(f"**Main focus:** {unit['focus']}")

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
    st.markdown("### Suggested time distribution per unit")
    df = pd.DataFrame(
        [
            ["Warm-up & presentation", 30],
            ["Grammar & vocabulary input", 60],
            ["Controlled practice", 60],
            ["Communication tasks", 60],
            ["Review & mini-assessment", 30],
        ],
        columns=["Stage", "Minutes"]
    )
    st.table(df)

def lessons_page():
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

def assessment_page():
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
    show_logo()

    current_page = get_current_page_id()
    render_page(current_page)

    # Floating fixed menu bottom-right
    render_floating_menu(current_page)

if __name__ == "__main__":
    main()
