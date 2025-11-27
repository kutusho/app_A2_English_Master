
import streamlit as st
import pandas as pd

# =========================
# BASIC CONFIG
# =========================
st.set_page_config(
    page_title="A2 English Course Program",
    page_icon="📘",
    layout="wide"
)

# =========================
# DATA
# =========================

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

UNITS = [
    {
        "number": 1,
        "name": "People",
        "focus": "Personal information, countries, jobs and everyday objects.",
        "grammar": [
            "Verb be: present",
            "Wh-questions"
        ],
        "vocabulary": [
            "Countries and nationalities",
            "Jobs",
            "Everyday things"
        ],
        "skills": {
            "speaking": [
                "Ask and answer basic personal questions",
                "Talk about people you know"
            ],
            "listening": [
                "Understand short conversations about people",
                "Recognise common introductions"
            ],
            "reading": [
                "Notes about people",
                "A simple country profile"
            ],
            "writing": [
                "Simple notes and introductions"
            ]
        }
    },
    {
        "number": 2,
        "name": "Daily Life",
        "focus": "Routines, free time and frequency.",
        "grammar": [
            "Present simple",
            "Adverbs of frequency"
        ],
        "vocabulary": [
            "Daily routines",
            "Free-time activities"
        ],
        "skills": {
            "speaking": [
                "Talk about what you do every day",
                "Talk about free time"
            ],
            "listening": [
                "Conversations about routines",
                "A conversation about time"
            ],
            "reading": [
                "An article about habits"
            ],
            "writing": [
                "Write an email about your routine"
            ]
        }
    },
    {
        "number": 3,
        "name": "Food",
        "focus": "Food, drink and eating out.",
        "grammar": [
            "Countable and uncountable nouns",
            "Some / any",
            "A / an"
        ],
        "vocabulary": [
            "Food and drink",
            "Restaurants"
        ],
        "skills": {
            "speaking": [
                "Talk about food you like",
                "Order a meal in a restaurant"
            ],
            "listening": [
                "A conversation in a restaurant"
            ],
            "reading": [
                "A restaurant review"
            ],
            "writing": [
                "Write about food you like"
            ]
        }
    },
    {
        "number": 4,
        "name": "Places",
        "focus": "Homes, furniture and the city.",
        "grammar": [
            "There is / there are",
            "Prepositions of place"
        ],
        "vocabulary": [
            "Buildings and furniture",
            "Places in a city"
        ],
        "skills": {
            "speaking": [
                "Describe your home",
                "Talk about your neighbourhood"
            ],
            "listening": [
                "A conversation about a new home"
            ],
            "reading": [
                "An article about a town"
            ],
            "writing": [
                "Short descriptions of places"
            ]
        }
    },
    {
        "number": 5,
        "name": "Past",
        "focus": "Life events and family history.",
        "grammar": [
            "Past simple (regular verbs)",
            "Past simple: positive/negative"
        ],
        "vocabulary": [
            "Regular verbs",
            "Life events"
        ],
        "skills": {
            "speaking": [
                "Talk about your past",
                "Talk about your family"
            ],
            "listening": [
                "A life story"
            ],
            "reading": [
                "Notes about childhood"
            ],
            "writing": [
                "Write about your family history"
            ]
        }
    },
    {
        "number": 6,
        "name": "Leisure",
        "focus": "Free time, days out and past experiences.",
        "grammar": [
            "Past simple (irregular verbs)",
            "Past simple questions"
        ],
        "vocabulary": [
            "Free-time activities",
            "Days out"
        ],
        "skills": {
            "speaking": [
                "Make future arrangements based on past experiences"
            ],
            "listening": [
                "Conversations about plans"
            ],
            "reading": [
                "An article about leisure"
            ],
            "writing": [
                "Short messages about plans"
            ]
        }
    },
    {
        "number": 7,
        "name": "Work",
        "focus": "Jobs, work routines and comparisons.",
        "grammar": [
            "Comparative adjectives",
            "Present continuous"
        ],
        "vocabulary": [
            "Jobs",
            "Workplace language"
        ],
        "skills": {
            "speaking": [
                "Talk about jobs and studies",
                "Compare people, places and things"
            ],
            "listening": [
                "Conversations at work"
            ],
            "reading": [
                "A work profile"
            ],
            "writing": [
                "Write about your job or studies"
            ]
        }
    },
    {
        "number": 8,
        "name": "Travel",
        "focus": "Trips, geography and future plans.",
        "grammar": [
            "Future: going to",
            "Travel questions"
        ],
        "vocabulary": [
            "Geography",
            "Travel and holiday vocabulary"
        ],
        "skills": {
            "speaking": [
                "Talk about future plans",
                "Plan a trip"
            ],
            "listening": [
                "A conversation about a trip"
            ],
            "reading": [
                "A travel blog"
            ],
            "writing": [
                "Write about travel plans"
            ]
        }
    },
    {
        "number": 9,
        "name": "Health",
        "focus": "Health, body and lifestyle.",
        "grammar": [
            "Should / shouldn’t",
            "Imperatives"
        ],
        "vocabulary": [
            "Parts of the body",
            "Health problems"
        ],
        "skills": {
            "speaking": [
                "Give advice",
                "Talk about lifestyle and routines"
            ],
            "listening": [
                "A conversation at the doctor’s"
            ],
            "reading": [
                "An article about sports and health"
            ],
            "writing": [
                "Write basic health advice"
            ]
        }
    },
    {
        "number": 10,
        "name": "The World",
        "focus": "Countries, geography and world cultures.",
        "grammar": [
            "Present perfect (ever/never)",
            "Present vs past"
        ],
        "vocabulary": [
            "Countries and geography",
            "Continents"
        ],
        "skills": {
            "speaking": [
                "Talk about places you have visited",
                "Talk about world cultures"
            ],
            "listening": [
                "A conversation about world travel"
            ],
            "reading": [
                "An article about unusual places"
            ],
            "writing": [
                "Write about your country"
            ]
        }
    }
]


def show_logo():
    """Show logo in the sidebar if available."""
    import os
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.info("Place your logo file as 'assets/logo.png' to display it here.")


def show_signature():
    """Show signature at the bottom if available."""
    import os
    sig_path = os.path.join("assets", "signature.png")
    if os.path.exists(sig_path):
        st.image(sig_path, width=200)
    else:
        st.info("Place your signature file as 'assets/signature.png' to display it here.")


def overview_page():
    st.title("📘 A2 Elementary English Course Program")
    st.subheader(COURSE_INFO["level"])

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Course title:** {COURSE_INFO['title']}")
        st.markdown(f"**Number of units:** {COURSE_INFO['units']}")
        st.markdown(f"**Approx. hours per unit:** {COURSE_INFO['hours_per_unit']}")
        st.markdown(f"**Total hours (suggested):** {COURSE_INFO['total_hours']}")
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


def syllabus_page():
    st.title("📚 Syllabus by Unit")

    unit_names = [f"Unit {u['number']}: {u['name']}" for u in UNITS]
    selected = st.selectbox("Select a unit", unit_names)
    unit_index = unit_names.index(selected)
    unit = UNITS[unit_index]

    st.markdown(f"## Unit {unit['number']}: {unit['name']}")
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
        for skill_name, skill_list in unit["skills"].items():
            st.markdown(f"**{skill_name.capitalize()}**")
            for s in skill_list:
                st.markdown(f"- {s}")

    st.markdown("---")
    st.markdown("### Suggested time distribution per unit")
    df = pd.DataFrame(
        [
            ["Presentation & warm-up", 30],
            ["Grammar & vocabulary input", 60],
            ["Controlled practice", 60],
            ["Communication & tasks", 60],
            ["Review & assessment", 30],
        ],
        columns=["Stage", "Minutes"]
    )
    st.table(df)


def assessment_page():
    st.title("📝 Assessment & Progress")

    st.markdown("### Suggested assessment structure")
    st.markdown(
        """
- **Unit progress checks** every 2 units (Units 1–2, 3–4, 5–6, 7–8, 9–10).
- **Mid-course assessment** after Unit 5:
  - Short listening
  - Reading comprehension
  - Guided writing
  - Short speaking interview
- **Final exam** after Unit 10:
  - Listening (everyday situations)
  - Reading (two short texts)
  - Writing (email + short paragraph)
  - Speaking (interview + role play)
        """
    )

    st.markdown("### Example weighting")
    df = pd.DataFrame(
        [
            ["Class participation & homework", "20%"],
            ["Unit progress checks", "30%"],
            ["Mid-course assessment", "20%"],
            ["Final exam", "30%"],
        ],
        columns=["Component", "Weight"]
    )
    st.table(df)

    st.markdown("### Notes")
    st.info(
        "You can adapt the weighting and instruments according to the needs of your institution "
        "or specific group."
    )


def teacher_page():
    st.title("👨‍🏫 About the Teacher / Program Owner")

    st.markdown(
        """
**Name:** Iván de Jesús Díaz Navarro  
**Role:** Tourist Guide & English Instructor  

This A2 Elementary English Course Program has been designed to integrate communicative English 
teaching with real-life contexts, especially for tourism, services and professional interaction.
        """
    )

    st.markdown("### Signature")
    show_signature()


def main():
    show_logo()

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ("Overview", "Syllabus by Unit", "Assessment & Progress", "About the Teacher")
    )

    if page == "Overview":
        overview_page()
    elif page == "Syllabus by Unit":
        syllabus_page()
    elif page == "Assessment & Progress":
        assessment_page()
    elif page == "About the Teacher":
        teacher_page()


if __name__ == "__main__":
    main()
