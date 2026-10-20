
import sqlite3
from pathlib import Path

import streamlit as st

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="Bharatiya Jnana Digital Heritage",
    page_icon="📚",
    layout="wide"
)

DB_PATH = Path(__file__).parent / "knowledge.db"

SAMPLE_DATA = [
    (
        "Aryabhata and Indian Mathematics",
        "Mathematics",
        "Aryabhata was an Indian mathematician and astronomer "
        "associated with the work Aryabhatiya, composed around "
        "499 CE. His work discusses arithmetic, algebra and astronomy.",
        "https://en.wikipedia.org/wiki/Aryabhata",
        ""
    ),
    (
        "Yoga Sutras of Patanjali",
        "Yoga",
        "The Yoga Sutras are a classical text traditionally "
        "attributed to Patanjali. They present ideas and practices "
        "concerning yoga, concentration and the mind.",
        "https://www.ignca.gov.in/",
        ""
    ),
    (
        "Vedic Heritage",
        "Literature",
        "The Vedic tradition includes the Rigveda, Samaveda, "
        "Yajurveda and Atharvaveda. Digital resources help people "
        "explore texts, recitation traditions and related heritage.",
        "https://culture.gov.in/sanskriti/vedic-heritage-portal",
        ""
    ),
    (
        "Indian Manuscript Preservation",
        "Manuscripts",
        "Manuscripts preserve historical, literary, scientific "
        "and cultural knowledge. Digitization can support access, "
        "documentation and long-term preservation.",
        "https://ignca.gov.in/online-digital-resources/manuscripts/manuscripts-in-india/",
        ""
    ),
    (
        "Traditional Indian Knowledge Systems",
        "Knowledge Systems",
        "Indian Knowledge Systems include diverse textual, oral "
        "and practical traditions. Their study involves documenting "
        "sources and understanding them in historical context.",
        "https://iks.aicte-india.org/",
        ""
    )
]

CATEGORIES = [
    "Mathematics",
    "Astronomy",
    "Yoga",
    "Ayurveda",
    "Literature",
    "Philosophy",
    "Art and Architecture",
    "Music and Dance",
    "Manuscripts",
    "Knowledge Systems",
    "Other"
]


# ---------------- DATABASE ----------------

def connect_db():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                source TEXT NOT NULL,
                image_url TEXT DEFAULT ''
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM knowledge"
        ).fetchone()[0]

        if count == 0:
            conn.executemany("""
                INSERT INTO knowledge
                (title, category, description, source, image_url)
                VALUES (?, ?, ?, ?, ?)
            """, SAMPLE_DATA)


def get_entries():
    with connect_db() as conn:
        return conn.execute("""
            SELECT id, title, category, description,
                   source, image_url
            FROM knowledge
            ORDER BY title COLLATE NOCASE
        """).fetchall()


def add_entry(title, category, description, source, image_url):
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO knowledge
            (title, category, description, source, image_url)
            VALUES (?, ?, ?, ?, ?)
        """, (title, category, description, source, image_url))


initialize_db()


# ---------------- PAGE HEADER ----------------

st.title("📚 Bharatiya Jnana Digital Heritage")

st.markdown(
    "### Digitization of the Bharatiya Jnana Parampara"
)

st.write(
    "A digital archive prototype for documenting, exploring "
    "and sharing India's traditional knowledge and heritage."
)

entries = get_entries()

col1, col2 = st.columns(2)

with col1:
    st.metric("Knowledge Entries", len(entries))

with col2:
    st.metric(
        "Categories Covered",
        len(set(entry[2] for entry in entries))
    )

st.divider()


# ---------------- NAVIGATION ----------------

page = st.sidebar.radio(
    "Navigation",
    ["Home & Search", "Add Knowledge", "About Project"]
)


# ---------------- HOME AND SEARCH ----------------

if page == "Home & Search":

    st.subheader("Explore the Knowledge Library")

    search_text = st.text_input(
        "🔍 Search by title, topic or keyword",
        placeholder="Try Aryabhata, yoga, manuscripts..."
    )

    available_categories = sorted(
        set(entry[2] for entry in entries)
    )

    selected_category = st.selectbox(
        "Filter by category",
        ["All Categories"] + available_categories
    )

    filtered_entries = []

    for entry in entries:
        entry_id, title, category, description, source, image_url = entry

        matches_search = (
            search_text.strip().lower() in
            f"{title} {category} {description}".lower()
        )

        matches_category = (
            selected_category == "All Categories"
            or category == selected_category
        )

        if matches_search and matches_category:
            filtered_entries.append(entry)

    st.caption(f"{len(filtered_entries)} result(s) found")

    if not filtered_entries:
        st.info("No results found. Try a different keyword.")

    for entry in filtered_entries:
        entry_id, title, category, description, source, image_url = entry

        with st.container(border=True):
            st.subheader(title)
            st.caption(f"Category: {category}")

            if image_url.strip():
                try:
                    st.image(image_url, width=350)
                except Exception:
                    st.warning("The image could not be loaded.")

            st.write(description)

            if source.strip():
                st.markdown(f"[View source / reference]({source})")

            with st.expander("Entry details"):
                st.write(f"Entry ID: {entry_id}")
                st.write(f"Category: {category}")
                st.write(f"Image URL: {image_url or 'Not provided'}")


# ---------------- ADD KNOWLEDGE ----------------

elif page == "Add Knowledge":

    st.subheader("Add a New Knowledge Entry")

    st.write(
        "Contribute a documented topic with a description "
        "and a reference link."
    )

    with st.form("add_knowledge_form"):

        title = st.text_input("Title *")

        category = st.selectbox(
            "Category *",
            CATEGORIES
        )

        description = st.text_area(
            "Description *",
            height=150
        )

        source = st.text_input(
            "Source URL *",
            placeholder="https://..."
        )

        image_url = st.text_input(
            "Image URL (optional)",
            placeholder="https://..."
        )

        submitted = st.form_submit_button("Save Knowledge Entry")

        if submitted:
            if not title.strip():
                st.error("Please enter a title.")

            elif not description.strip():
                st.error("Please enter a description.")

            elif not source.strip().startswith(("https://", "http://")):
                st.error("Please enter a valid-looking HTTP or HTTPS source URL.")

            elif image_url.strip() and not image_url.strip().startswith(
                ("https://", "http://")
            ):
                st.error("The image URL must begin with HTTP or HTTPS.")

            else:
                add_entry(
                    title.strip(),
                    category,
                    description.strip(),
                    source.strip(),
                    image_url.strip()
                )

                st.success("Knowledge entry saved successfully!")
                st.rerun()


# ---------------- ABOUT PROJECT ----------------

elif page == "About Project":

    st.subheader("About the Project")

    st.write(
        "The purpose of this prototype is to demonstrate how "
        "traditional Indian knowledge can be documented and "
        "organized in a searchable digital archive."
    )

    st.markdown("#### Objectives")
    st.markdown("""
    - Preserve information about Indian knowledge traditions.
    - Make documented entries easier to search and explore.
    - Attach reference links to support further research.
    - Allow users to contribute new knowledge entries.
    - Demonstrate the use of digital technology for heritage access.
    """)

    st.markdown("#### Technologies Used")
    st.write("Python, Streamlit and SQLite")

    st.markdown("#### Reference Portals")
    st.markdown("""
    - [Indian Knowledge Systems Division](https://iks.aicte-india.org/)
    - [IGNCA Digital Resources](https://ignca.gov.in/online-digital-resources/)
    - [Vedic Heritage Portal](https://culture.gov.in/sanskriti/vedic-heritage-portal)
    - [National Mission for Manuscripts](https://www.namami.gov.in/manuscript-database)
    """)

st.divider()

st.caption(
    "Bharatiya Jnana Digital Heritage | IKS Working Prototype"
)
