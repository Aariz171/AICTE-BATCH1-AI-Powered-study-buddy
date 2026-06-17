from dotenv import load_dotenv
import os
import re
import html
import streamlit as st
import google.genai as genai

# Load environment variables from project.env using absolute path
env_path = os.path.join(os.path.dirname(__file__), 'project.env')
load_dotenv(env_path)

# Configure the API key for GenAI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY not found in environment variables. Add it to project.env.")
    st.stop()

# Initialize the GenAI client
client = genai.Client(api_key=api_key)

# Page configuration and custom styling
st.set_page_config(page_title="AI-Powered Study Buddy", page_icon="📘", layout="wide")

# Initialize theme session state (default to dark/black background)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Light mode CSS
light_mode_css = """
<style>
    * {
        margin: 0;
        padding: 0;
    }
    html, body {
        background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 50%, #f0fdfa 100%) !important;
        min-height: 100vh;
    }
    .stApp {
        background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 50%, #f0fdfa 100%) !important;
        color: #0f172a !important;
    }
    .css-1adrfps, .css-1lcbmhc, .css-1r6slb0, .css-18ni7ap {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 24px !important;
        box-shadow: 0 25px 50px rgba(99, 102, 241, 0.12), 0 10px 20px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.1) !important;
        padding: 2rem !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.35) !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 20px 45px rgba(99, 102, 241, 0.45) !important;
    }
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div>select {
        border-radius: 12px !important;
        border: 2px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #0f172a !important;
        padding: 0.85rem 1rem !important;
        font-weight: 500 !important;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    .stSidebar {
        background: linear-gradient(180deg, #f3f4f6 0%, #ffffff 100%) !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3f4f6 0%, #ffffff 100%) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #3b0764 !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
    }
    .stTabs [role='tab'] {
        border-radius: 12px 12px 0 0 !important;
        padding: 0.95rem 1.5rem !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        background: rgba(99, 102, 241, 0.05) !important;
    }
    .stTabs [role='tab'][aria-selected='true'] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2) !important;
    }
    .stMarkdown h1 {
        color: #3b0764 !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
    }
    .stMarkdown h2 {
        color: #4c1d95 !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    .stMarkdown h3 {
        color: #1e40af !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    .stMarkdown h4 {
        color: #5b21b6 !important;
        font-weight: 700 !important;
    }
    .stMarkdown p, .stMarkdown div {
        color: #1f2937 !important;
        font-weight: 500 !important;
        line-height: 1.7 !important;
    }
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
        color: #065f46 !important;
        border: 2px solid #6ee7b7 !important;
        border-radius: 14px !important;
    }
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        color: #78350f !important;
        border: 2px solid #fcd34d !important;
        border-radius: 14px !important;
    }
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
        color: #991b1b !important;
        border: 2px solid #fca5a5 !important;
        border-radius: 14px !important;
    }
    .stInfo {
        background: linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%) !important;
        color: #164e63 !important;
        border: 2px solid #67e8f9 !important;
        border-radius: 14px !important;
    }
    table { border-radius: 12px !important; }
    thead tr { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; color: #ffffff !important; }
    thead th { color: #ffffff !important; font-weight: 700 !important; }
    tbody tr:hover { background: rgba(99, 102, 241, 0.05) !important; }
    tbody td { color: #0f172a !important; font-weight: 500 !important; }
</style>
"""

# Dark mode CSS
dark_mode_css = """
<style>
    * {
        margin: 0;
        padding: 0;
    }
    html, body {
        background: #000000 !important;
        min-height: 100vh;
    }
    .stApp {
        background: #000000 !important;
        color: #ffffff !important;
    }
    .css-1adrfps, .css-1lcbmhc, .css-1r6slb0, .css-18ni7ap {
        background: rgba(0, 0, 0, 0.85) !important;
        border-radius: 24px !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 10px 20px rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 2rem !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a78bfa 100%) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.4) !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 20px 45px rgba(99, 102, 241, 0.5) !important;
    }
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div>select {
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.06) !important;
        background: rgba(255,255,255,0.02) !important;
        color: #ffffff !important;
        padding: 0.85rem 1rem !important;
        font-weight: 500 !important;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.2) !important;
    }
    .stSidebar {
        background: #000000 !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #a78bfa !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background: rgba(255,255,255,0.02) !important;
        color: #ffffff !important;
        border: 2px solid rgba(167,139,250,0.08) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #a78bfa 0%, #6366f1 100%) !important;
        color: #1e293b !important;
        border: none !important;
        font-weight: 700 !important;
    }
    .stTabs [role='tab'] {
        border-radius: 12px 12px 0 0 !important;
        padding: 0.95rem 1.5rem !important;
        color: #e5e7eb !important;
        font-weight: 700 !important;
        background: rgba(255,255,255,0.02) !important;
    }
    .stTabs [role='tab'][aria-selected='true'] {
        background: linear-gradient(135deg, #6366f1 0%, #a78bfa 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3) !important;
    }
    .stMarkdown h1 {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
    }
    .stMarkdown h2 {
        color: #e5e7eb !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    .stMarkdown h3 {
        color: #dbeafe !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    .stMarkdown h4 {
        color: #e879f9 !important;
        font-weight: 700 !important;
    }
    .stMarkdown p, .stMarkdown div {
        color: #e5e7eb !important;
        font-weight: 500 !important;
        line-height: 1.7 !important;
    }
    .stSuccess {
        background: rgba(6, 95, 70, 0.3) !important;
        color: #86efac !important;
        border: 2px solid #4ade80 !important;
        border-radius: 14px !important;
    }
    .stWarning {
        background: rgba(120, 53, 15, 0.3) !important;
        color: #facc15 !important;
        border: 2px solid #fbbf24 !important;
        border-radius: 14px !important;
    }
    .stError {
        background: rgba(127, 29, 29, 0.3) !important;
        color: #f87171 !important;
        border: 2px solid #ef4444 !important;
        border-radius: 14px !important;
    }
    .stInfo {
        background: rgba(6, 78, 99, 0.3) !important;
        color: #67e8f9 !important;
        border: 2px solid #22d3ee !important;
        border-radius: 14px !important;
    }
    table { border-radius: 12px !important; }
    thead tr { background: linear-gradient(135deg, #6366f1 0%, #a78bfa 100%) !important; color: #ffffff !important; }
    thead th { color: #ffffff !important; font-weight: 700 !important; }
    tbody tr:hover { background: rgba(99, 102, 241, 0.1) !important; }
    tbody td { color: #e5e7eb !important; font-weight: 500 !important; }
</style>
"""

# Apply the appropriate CSS based on theme
if st.session_state.theme == "light":
    st.markdown(light_mode_css, unsafe_allow_html=True)
else:
    st.markdown(dark_mode_css, unsafe_allow_html=True)

# Helper to render text with theme-appropriate color and proper heading tags
def themed_text(s: str):
    color = "#0f172a" if st.session_state.theme == "light" else "#cbd5e1"
    # Render markdown-like headings as HTML headings so styles apply and size is visible
    if s.startswith("## "):
        content = html.escape(s[3:])
        st.markdown(f'<h2 style="color: {color}; margin: 0;">{content}</h2>', unsafe_allow_html=True)
    elif s.startswith("### "):
        content = html.escape(s[4:])
        st.markdown(f'<h3 style="color: {color}; margin: 0;">{content}</h3>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color: {color};">{html.escape(s)}</div>', unsafe_allow_html=True)

# Initialize session state for storing the generated content
if "study_profile" not in st.session_state:
    st.session_state.study_profile = {
        "Target": "Score 90+ in my next exam",
        "Level": "Intermediate",
        "Learning Preferences": "Detailed step-by-step",
        "Study Routine": "Two hours daily study",
    }

if "study_response" not in st.session_state:
    st.session_state.study_response = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = 5

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

if "flash_topic" not in st.session_state:
    st.session_state.flash_topic = ""

# Function to get Gemini response based on user prompt
def get_gemini_response(prompt: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as err:
        st.error(f"Error generating response: {err}")
        return None

# Section header
st.markdown("# 📘 AI-Powered Study Buddy")
st.markdown(
    "Use the sidebar to personalize your profile, then choose a tab to get help with study questions, summaries, quizzes, or flash cards."
)

# Sidebar for profile and tips
with st.sidebar:
    # Theme toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🌓 Theme")
    with col2:
        if st.button("🌙" if st.session_state.theme == "light" else "☀️", key="theme_toggle"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 🎯 Study Profile")

    target = st.text_input(
        "Target",
        value=st.session_state.study_profile["Target"],
        placeholder="Score 90+ in my next exam",
    )
    level = st.text_input(
        "Level",
        value=st.session_state.study_profile["Level"],
        placeholder="Beginner, Intermediate, Advanced",
    )
    preferences = st.text_input(
        "Learning Preferences",
        value=st.session_state.study_profile["Learning Preferences"],
        placeholder="Detailed step-by-step explanations",
    )
    routine = st.text_input(
        "Study Routine",
        value=st.session_state.study_profile["Study Routine"],
        placeholder="Two hours daily study",
    )

    if st.button("Update Profile", key="update_profile"):
        st.session_state.study_profile.update(
            {
                "Target": target,
                "Level": level,
                "Learning Preferences": preferences,
                "Study Routine": routine,
            }
        )
        st.success("Profile updated successfully!")

    st.markdown("---")
    st.markdown("## 💡 Quick Tips")
    st.markdown(
        "- Ask specific study questions for better answers.\n"
        "- Use the Summary tab to compress long notes.\n"
        "- Generate quizzes to test your knowledge.\n"
        "- Create flash cards for active recall practice."
    )

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Study Help", "Summary Generator", "Quiz Generator", "Flash Cards"]
)

with tab1:
    st.markdown("## 📘 Personalized Study Help")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        question = st.text_area(
            "Ask a study question",
            value="",
            placeholder="e.g., How can I remember formulas for physics?",
            height=220,
        )
        if st.button("Generate Response", key="generate_response"):
            if not question.strip():
                st.warning("Please enter a study question to continue.")
            else:
                prompt = (
                    "Create a friendly, personalized study answer based on the user's profile. "
                    f"Goal: {st.session_state.study_profile['Target']}. "
                    f"Level: {st.session_state.study_profile['Level']}. "
                    f"Learning Preferences: {st.session_state.study_profile['Learning Preferences']}. "
                    f"Study Routine: {st.session_state.study_profile['Study Routine']}. "
                    f"Question: {question}"
                )
                with st.spinner("Generating personalized study help..."):
                    response = get_gemini_response(prompt)
                if response:
                    st.session_state.study_response = response
                else:
                    st.error("Unable to generate a response right now.")

        if st.session_state.study_response:
            st.markdown("### ✅ Your AI Study Answer")
            st.success(st.session_state.study_response)
            st.download_button(
                label="Download Answer",
                data=st.session_state.study_response,
                file_name="study_answer.txt",
                mime="text/plain",
                key="download_answer",
            )

    with col_right:
        st.markdown("### 📋 Study Profile")
        profile_table = [
            {"Field": key, "Value": value}
            for key, value in st.session_state.study_profile.items()
        ]
        st.table(profile_table)

        st.markdown("---")
        st.markdown("### 🔎 Why this helps")
        st.write(
            "A tailored profile lets the model match answers to your goal, current level, and study style. "
            "Update it anytime in the sidebar."
        )

with tab2:
    st.markdown("## 📄 Summary Generator")
    st.write("Paste your notes below and choose a summary length.")
    text = st.text_area(
        "Text to summarize",
        value="",
        height=240,
        placeholder="Paste lecture notes, an article, or your study materials here...",
    )

    length = st.selectbox(
        "Summary length",
        ["Short (3-4 lines)", "Medium (6-8 lines)", "Detailed"],
        index=1,
    )

    if st.button("Generate Summary", key="generate_summary"):
        if not text.strip():
            st.warning("Please add some text to summarize.")
        else:
            prompt = (
                "Summarize the following text in a clear and concise way. "
                f"Use a {length.lower()} summary.\n\nText:\n{text}"
            )
            with st.spinner("Generating summary..."):
                summary = get_gemini_response(prompt)
            if summary:
                st.session_state.summary = summary
            else:
                st.error("Summary generation failed.")

    if st.session_state.summary:
        st.markdown("### 📌 Generated Summary")
        st.info(st.session_state.summary)
        st.download_button(
            label="Download Summary",
            data=st.session_state.summary,
            file_name="summary.txt",
            mime="text/plain",
            key="download_summary",
        )

with tab3:
    themed_text("### 🧠 Quiz Generator")
    themed_text("Generate multiple-choice quizzes to practice active recall.")

    quiz_col, preview_col = st.columns([2, 1])
    with quiz_col:
        quiz_topic = st.text_input(
            "Quiz topic",
            value=st.session_state.quiz_topic,
            placeholder="e.g., Chemistry bonding, World War II, Algebra",
            key="quiz_topic_input",
        )
        num_questions = st.slider(
            "Number of questions",
            min_value=1,
            max_value=10,
            value=st.session_state.quiz_questions,
            key="quiz_count",
        )

        if st.button("Generate Quiz", key="generate_quiz"):
            if not quiz_topic.strip():
                st.warning("Please enter a quiz topic.")
            else:
                prompt = (
                    f"Create {num_questions} multiple-choice questions about {quiz_topic}.\n"
                    "For each question, use this exact format: \n"
                    "Q1. Question text\nA) option A\nB) option B\nC) option C\nD) option D\nAnswer: A\nExplanation: brief explanation\n\n"
                    "Start each question block on a new line with `Q<number>.`. Do not include extra text outside the question blocks."
                )
                with st.spinner("Generating quiz..."):
                    quiz_text = get_gemini_response(prompt)
                if quiz_text:
                    st.session_state.quiz_data = quiz_text
                    st.session_state.quiz_topic = quiz_topic
                    st.session_state.quiz_questions = num_questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_score = 0
                else:
                    st.error("Failed to generate quiz.")

    with preview_col:
        themed_text("### 📝 Quiz Preview")
        themed_text(
            "After generating a quiz, answer all questions and submit to see your score and review the correct answers."
        )

    if st.session_state.quiz_data:
        questions = re.split(r"\n(?=(?:Q|q)\d+[\.\)])", st.session_state.quiz_data.strip())
        themed_text(f"### Topic: {st.session_state.quiz_topic}")
        themed_text(f"**Questions generated:** {len(questions)}")
        st.markdown("---")

        with st.form("quiz_form"):
            answers = []
            for index, block in enumerate(questions, start=1):
                # Remove leading Q numbering
                raw = re.sub(r"^(?:Q|q)\d+[\.\)]\s*", "", block).strip()
                # Split off options so question_text doesn't include them
                question_part = re.split(r"\n(?=[A-Za-z][\.|\)])", raw, maxsplit=1)[0].strip()
                # If split failed, fallback to text before 'Answer:'
                if not question_part:
                    question_part = raw.split("Answer:")[0].strip()

                # Match options like 'A) ...' or 'A. ...' (case-insensitive)
                choices = re.findall(r"(?m)^[A-Da-d][\.|\)]\s*.*", raw)
                # Normalize choices (uppercase letter + rest)
                normalized_choices = []
                for ch in choices:
                    m = re.match(r"^([A-Da-d])[\.|\)]\s*(.*)", ch)
                    if m:
                        normalized_choices.append(f"{m.group(1).upper()}) {m.group(2).strip()}")

                correct_match = re.search(r"Answer:\s*([A-Da-d])", block, re.IGNORECASE)
                correct_letter = correct_match.group(1).upper() if correct_match else None
                explanation_match = re.search(r"Explanation:\s*(.*)", block, re.DOTALL | re.IGNORECASE)
                explanation = explanation_match.group(1).strip() if explanation_match else ""

                st.markdown(f"**Q{index}.** {question_part}")
                selected = st.radio(
                    "Choose one",
                    ["-- Select an option --"] + (normalized_choices if normalized_choices else choices),
                    key=f"quiz_q_{index}",
                )
                answers.append((selected, correct_letter, explanation))
                st.markdown("---")

            submit_quiz = st.form_submit_button("Submit Quiz")

        if submit_quiz:
            if any(answer[0] == "-- Select an option --" for answer in answers):
                st.warning("Please answer all questions before submitting.")
            else:
                score = sum(
                    1 for selected, correct_letter, _ in answers
                    if correct_letter and selected and selected.strip().upper().startswith(correct_letter)
                )
                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True

        if st.session_state.quiz_submitted:
            total = len(questions)
            percentage = (st.session_state.quiz_score / total) * 100 if total else 0
            st.success(f"🎯 Score: {st.session_state.quiz_score} / {total}")
            st.info(f"📊 Accuracy: {percentage:.2f}%")
            st.markdown("### ✅ Correct Answers & Explanations")
            for idx, (_, correct_letter, explanation) in enumerate(answers, start=1):
                st.markdown(f"**Q{idx} Correct:** {correct_letter}")
                st.write(explanation)
                st.markdown("---")
            if st.button("Generate a New Quiz", key="new_quiz"):
                st.session_state.quiz_data = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = 0
                st.experimental_rerun()

with tab4:
    themed_text("## 🧾 Flash Cards")
    themed_text("Generate concise flash cards for quick review and an interactive study mode.")

    # Session State Setup
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    topic = st.text_input("Enter Topic", key="flash_topic_input_merged")
    num_cards = st.slider("Number of Flash Cards", 1, 20, 5, key="flash_num_cards")

    # Generate Flash Cards
    if st.button("Generate Flash Cards", key="generate_flashcards_merged"):
        if topic.strip() == "":
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating flash cards..."):
                prompt = f"""
                Generate {num_cards} different flash cards on topic \"{topic}\".

                Format strictly like this:

                Q: Question here
                A: Answer here

                Only provide flash cards. No extra text.
                """
                response = get_gemini_response(prompt)
                if response:
                    cards_text = response.split("Q:")
                    flashcards = []
                    for card in cards_text:
                        if "A:" in card:
                            question = card.split("A:")[0].strip()
                            answer = card.split("A:")[1].strip()
                            flashcards.append((question, answer))

                    st.session_state.flashcards = flashcards
                    st.session_state.current_index = 0
                    st.session_state.show_answer = False
                else:
                    st.error("Unable to generate flash cards.")

    # Display Flash Card
    if st.session_state.flashcards:
        question, answer = st.session_state.flashcards[st.session_state.current_index]

        themed_text("### 📌 Question")
        st.info(question)

        if st.button("Show Answer", key="show_answer_btn"):
            st.session_state.show_answer = True

        if st.session_state.show_answer:
            themed_text("### ✅ Answer")
            st.success(answer)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Previous", key="prev_card"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.session_state.show_answer = False

        with col2:
            if st.button("Next ➡", key="next_card"):
                if st.session_state.current_index < len(st.session_state.flashcards) - 1:
                    st.session_state.current_index += 1
                    st.session_state.show_answer = False

        themed_text(f"Card {st.session_state.current_index + 1} of {len(st.session_state.flashcards)}")
        st.download_button(
            label="Download Flash Cards",
            data="\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.flashcards]),
            file_name="flash_cards.txt",
            mime="text/plain",
            key="download_flashcards",
        )

