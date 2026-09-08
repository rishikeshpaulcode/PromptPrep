# streamlit app for prototype (first version)
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="PromptPrep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom Element Styling
st.markdown(
    """
    <style>
    /* Style for Primary Blue Button */
    .st-key-NewSessionBtn label[data-testid="stWidgetLabel"] div.stButton > button p {
        background-color: #1E88E5;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.2s ease-in-out;
    }

    /* Hover state */
    div.stButton > button:hover p {
        background-color: #1565C0;
        color: white;
    }
    """,
    unsafe_allow_html=True
)


# Top Banner
st.markdown(
    """
    <style>
    /* 1. Define the sticky banner bar */
    .fixed-header {
        padding: 15px 10px 0px;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 70px;
        background-color: #1E293B; /* Dark slate background */
        color: #F8FAFC;            /* Light text */
        display: flex;
        align-items: baseline;
        justify-content: flex-start;
        font-weight: 600;
        font-size: 13px;
        z-index: 999999;          /* Keep it above all Streamlit elements */
        border-bottom: 2px solid #1E293B;
    }

    .app-name {
        margin: 0px 10px;
        font-size: 28px;
    }

    .tagline {
        font-size: 18px;
    }

    /* 2. Adjust Streamlit's default main container padding so content isn't hidden under the banner */
    .stAppHeader {
        z-index: 99999;           /* Keep Streamlit top menu controls usable */
    }
    
    .main .block-container {
        padding-top: 60px !important; /* Offset content equal to header height + padding */
    }
    </style>
    
    <div class="fixed-header">
        <div class="app-name"> 🎯 PromptPrep: </div>
        <div class="tagline"> AI-Driven Quiz Engine </div> 
    </div>
    """,
    unsafe_allow_html=True
)


# Sidebar UI
# get user's Gemini API key
with st.sidebar:
    st.header("Configuration")
    
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Get your API key from Google AI Studio (https://aistudio.google.com/)"
    )

    if api_key:
        st.success("API Key provided!", icon="✅")
    else:
        st.warning("Please enter your API Key to proceed.", icon="⚠️")


# Main Content
st.title(
    "PromptPrep",
    icon="🎯",
    text_alignment="left"
)

col1, col2 = st.columns(2)

with col1:
    st.subheader(":red[Problem:]")
    st.write("""
        :grey[In modern education, many students struggle not from a lack of effort, but from a lack of personalized guidance and adaptive learning tools. One-size-fits-all classroom instruction and static textbooks treat every learner the same, ignoring individual pacing, specific knowledge gaps, and unique learning styles. Without tailored feedback and targeted practice, high school and college students often feel overwhelmed, lose momentum, and find it difficult to master complex concepts effectively.]
    """)

with col2:
    st.subheader(":green[Solution:]")
    st.write("""
        :grey[PromptPrep addresses this by putting a deeply integrated AI tutor at every student's fingertips. The platform leverages advanced artificial intelligence to generate unlimited, subject-agnostic practice questions, while allowing students to fully customize the difficulty level, format, and tone to fit their individual needs. By delivering tailored, low-stakes practice that adapts directly to each learner, PromptPrep makes targeted exam preparation effortless—and as a completely free-of-cost initiative, it ensures quality, personalized learning is accessible to everyone.]
    """)

if api_key:
    pass
    #st.button("Start new quiz session ➡️")
else:
    st.info("👈 Enter your Gemini API Key in the sidebar to start.")


st.button("Start new quiz session ➡️", key="NewSessionBtn")