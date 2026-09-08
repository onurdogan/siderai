import streamlit as st
from pathlib import Path

from ollama import chat

from rag.retrieve import retrieve_context
from rag.interpret import interpret

# -------------------------
# SiderAI style
# -------------------------

st.markdown(
    """
    <style>

    .stMarkdown {
        font-size: 1.25rem;
    }

    h1 {
        font-size: 3rem !important;
    }

    h2 {
        font-size: 2rem !important;
    }

    textarea {
        font-size: 1.2rem !important;
    }

    div.stButton > button {
        width: 100%;
        height: 3.5em;
        font-size: 1.4rem;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# siderai configuration
# -------------------------

st.set_page_config(
    page_title="siderai",
    page_icon="🌀",
    layout="wide"
)


PAPER_DIR = Path("papers")
UPLOAD_DIR = PAPER_DIR / "uploaded"

PAPER_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# -------------------------
# Header
# -------------------------

st.markdown(
    """
    <h1 style="font-size:3rem;">
    🌀 siderai
    </h1>

    <p style="font-size:1.5rem;">
    from desire to consideration
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


st.markdown(
"""
**Local AI assistant for scientific literature interpretation**

Designed for:

- 📄 Scientific literature interpretation
- 🧬 eDNA / metabarcoding workflows
- 📊 Biodiversity data exploration
- 💡 New aspects & known aspects discovery
- 🌀 Research gap interpretation
"""
)



# -------------------------
# Sidebar
# -------------------------

st.sidebar.header(
    "🌀 Knowledge Space"
)



# -------------------------
# Upload
# -------------------------

st.sidebar.subheader(
    "Add knowledge"
)


uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or XLSX",
    type=["pdf", "xlsx"],
    accept_multiple_files=True
)


if uploaded_files:

    for file in uploaded_files:

        save_path = UPLOAD_DIR / file.name

        with open(save_path, "wb") as f:

            f.write(
                file.getbuffer()
            )


    st.sidebar.success(
        f"{len(uploaded_files)} document(s) added"
    )



# -------------------------
# Document workspace
# -------------------------

st.sidebar.subheader(
    "Available documents"
)


if st.sidebar.button(
    "🔄 Refresh"
):

    st.rerun()



documents = []


for item in PAPER_DIR.rglob("*"):

    if item.suffix.lower() in [".pdf", ".xlsx"]:

        documents.append(
            item.name
        )


selected_documents = st.sidebar.multiselect(
    "Select documents",
    documents
)



if st.sidebar.button(
    "📚 Load"
):

    st.session_state[
        "active_documents"
    ] = selected_documents


    st.sidebar.success(
        f"{len(selected_documents)} document(s) loaded"
    )



st.sidebar.subheader(
    "Active context"
)


if "active_documents" in st.session_state:

    for doc in st.session_state["active_documents"]:

        st.sidebar.write(
            f"🌀 {doc}"
        )

else:

    st.sidebar.info(
        "No documents loaded"
    )



# -------------------------
# Question
# -------------------------

st.divider()


st.markdown(
    """
    <h2 style="font-size:2.2rem;">
    What do you desire to learn?
    </h2>
    """,
    unsafe_allow_html=True
)

question = st.text_area(
    "",
    placeholder=
    "Example: What sequencing information is reported in MIEM?"
)


st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        font-size: 1.3rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Buttons
# -------------------------

st.markdown(
    """
    🌱 **With hope**  
    ↓  
    🌀 **Consider**

    *Consider the author's expectations, claims, and contributions*
    """
)

consider_button = st.button(
    "🌀 Consider the author's expectations"
)


st.markdown(
    """
    🌌 **Without hope**  
    ↓  
    🧐 **Interpret the literature**

    *Explore meaning beyond the authors' claims*
    """
)

interpret_button = st.button(
    "🧐 Interpret the literature"
)

# =====================================================
# CONSIDER
# =====================================================

if consider_button:


    if not question:

        st.warning(
            "Please enter a question."
        )


    else:


        with st.spinner(
            "🌀 Considering..."
        ):

            active_documents = st.session_state.get(
                "active_documents",
                []
            )


            docs = retrieve_context(
                question,
                active_documents
            )


            context = "\n\n".join(
                [
                    d.content
                    for d in docs
                ]
            )
            context = "\n\n".join(
                [
                    d.content
                    for d in docs
                ]
            )


            response = chat(

                model="qwen3:8b",

                messages=[

                    {
                        "role":"system",

                        "content":
"""
You are siderai.

Answer scientific questions using
only the provided documents.

If information is missing,
state that clearly.
"""
                    },

                    {
                        "role":"user",

                        "content":
f"""
Context:

{context}


Question:

{question}
"""
                    }

                ]
            )


            answer = response["message"]["content"]



        with st.expander(
            "🌀 Consideration result",
            expanded=True
        ):

            st.markdown(
                answer
            )



# =====================================================
# INTERPRET
# =====================================================

if interpret_button:

    with st.spinner(
        "🧐 Interpreting scientific structure..."
    ):

        active_documents = st.session_state.get(
            "active_documents",
            []
        )

        docs = retrieve_context(
            "scientific contribution novelty research gaps methods",
            active_documents
        )

        context = "\n\n".join(
            [
                d.content
                for d in docs
            ]
        )

        interpretation = interpret(
            context
        )


    with st.expander(
        "🧐 Interpretation result",
        expanded=True
    ):

        st.markdown(
            interpretation
        )
