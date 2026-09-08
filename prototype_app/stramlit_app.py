import streamlit as st

# Define pages
home = st.Page("pages/home.py", default=True)
new_session = st.Page("pages/new_session.py")
quiz = st.Page("pages/quiz.py")
result = st.Page("pages/result.py")

# Group pages into navigation categories
pg = st.navigation(
    [home, new_session, quiz, result],
    position="hidden"
)

# Configure and run navigation
st.set_page_config(
    page_title="PromptPrep", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

pg.run()
