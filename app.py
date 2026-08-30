import streamlit as st
import google.generativeai as genai
import json

# Page Setup
st.set_page_config(page_title="Mmuta Quiz Game.", page_icon="🟢", layout="centered")

# Custom Brand Styling (Ink, Paper, Green Accent, Space Grotesk & EB Garamond)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

    /* Global Theme & Canvas */
    html, body, .stApp {
        background-color: #0B0F0D !important;
        color: #F2F1EA !important;
        font-family: 'EB Garamond', Georgia, serif;
    }
    
    /* Typography Overrides */
    h1, h2, h3, h4, h5, h6, .stTitle {
        font-family: 'Space Grotesk', system-ui, sans-serif !important;
        font-weight: 600 !important;
        color: #F2F1EA !important;
        letter-spacing: -0.02em !important;
    }

    p, li, label, .stMarkdown {
        font-family: 'EB Garamond', Georgia, serif;
        color: #F2F1EA;
        font-size: 1.05rem;
    }

    /* Muted Text */
    .stCaption, .muted-text {
        color: #A7B0A9 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.85rem !important;
    }

    /* Primary Buttons & Choice Targets */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.85rem 1.4rem;
        background-color: #5FBF87 !important;
        color: #06110B !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: 1.5px solid transparent !important;
        transition: background-color 0.18s ease, color 0.18s ease, transform 0.06s ease;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: #82D6A3 !important;
        color: #06110B !important;
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(1px);
    }

    .stButton > button:disabled {
        background-color: #161E1A !important;
        color: #8B948D !important;
        border-color: rgba(255, 255, 255, 0.06) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111714 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    section[data-testid="stSidebar"] * {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Text Area & Input Styling */
    .stTextArea textarea, .stTextInput input {
        background-color: #111714 !important;
        color: #F2F1EA !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 14px !important;
        font-family: 'EB Garamond', serif !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #5FBF87 !important;
        box-shadow: none !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #5FBF87 !important;
    }
    
    /* Alert / Status Boxes */
    div[data-baseweb="notification"] {
        border-radius: 14px !important;
        background-color: #111714 !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Header (Brand Wordmark Style)
st.title("Mmuta Quiz Game.")
st.caption("Strategy. Stories. Impact.")

# Sidebar Setup
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Enter Google AI Studio API Key", type="password")
    
    uploaded_files = st.file_uploader(
        "Upload lecture slides or notes (PDF or TXT)", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
    
    st.write("---")
    mode = st.radio("Select mode", ["Quiz sprint", "Case study simulator"])
    
    if st.button("Reset session"):
        st.session_state.clear()
        st.rerun()

# Initialize Session States
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "missed_questions" not in st.session_state:
    st.session_state.missed_questions = []
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 10
if "case_study" not in st.session_state:
    st.session_state.case_study = None

# Extract Text Function
def extract_text_from_multiple(files):
    combined_text = ""
    for file in files:
        if file.type == "text/plain":
            combined_text += file.read().decode("utf-8") + "\n\n"
        else:
            import pypdf
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                combined_text += page.extract_text() or ""
            combined_text += "\n\n"
    return combined_text

# AI Prompt Generators
def generate_quiz(content, api_key, num_q=10):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert Professor in Strategic Communications, Marketing, and Brand Strategy.
    Based on the following lecture material, generate EXACTLY {num_q} randomized multiple-choice quiz questions across all provided topics.
    
    Lecture Material:
    {content[:30000]}
    
    Format output strictly as JSON list of objects. No markdown code blocks.
    Each object must have:
    - "question": string
    - "options": list of 4 strings (e.g. ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"])
    - "answer": string (matching one option exactly)
    - "explanation": string (1-sentence concept explanation)
    - "topic_ref": string (specific concept/topic area from notes to review)
    """
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

def generate_case_study(content, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Based on the following lecture notes, create 1 realistic strategic business case study scenario.
    
    Lecture Material:
    {content[:30000]}
    
    Format output strictly as JSON object with:
    - "title": string
    - "scenario": string (2-3 paragraphs describing a real-world company challenge)
    - "question": string (the strategic prompt for the student to solve)
    - "key_concepts": list of strings (concepts they should apply)
    """
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

def evaluate_case_solution(scenario, student_response, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Analyze this student's case study solution based on the scenario.
    
    Scenario & Question: {scenario}
    Student Answer: {student_response}
    
    Provide a constructive review:
    1. Score out of 10.
    2. Strategic strengths in their answer.
    3. Missing elements based on course principles.
    4. Two actionable steps to improve.
    """
    response = model.generate_content(prompt)
    return response.text

# ----------------- MODE 1: QUIZ SPRINT -----------------
if mode == "Quiz sprint":
    if not uploaded_files or not api_key:
        st.info("Enter your Google AI Studio API key and upload your lecture notes in the sidebar to start.")
    elif not st.session_state.questions:
        if st.button(f"Start {st.session_state.num_questions}-question sprint"):
            with st.spinner("Analyzing lecture files and building quiz..."):
                try:
                    text = extract_text_from_multiple(uploaded_files)
                    st.session_state.questions = generate_quiz(text, api_key, st.session_state.num_questions)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        q_idx = st.session_state.current_q
        total_q = len(st.session_state.questions)
        
        # Finished Quiz Screen
        if q_idx >= total_q:
            score = st.session_state.score
            
            if score < 7:
                st.warning("Didn't you say you were studying hard?")
                st.write(f"**Your Score:** {score} / {total_q}")
                st.write("---")
                st.subheader("Where to focus your reading")
                for item in st.session_state.missed_questions:
                    st.markdown(f"* **Question:** {item['question']}")
                    st.markdown(f"  * **Topic to review:** `{item['topic']}`")
                    st.markdown(f"  * **Explanation:** {item['explanation']}")
                    st.write("")

            elif score in [8, 9]:
                st.info("Looks like someone's been hitting the books. Great job, but let's shoot for a perfect score next time.")
                st.write(f"**Your Score:** {score} / {total_q}")
                st.write("---")
                st.subheader("Focus area for a perfect score")
                for item in st.session_state.missed_questions:
                    st.markdown(f"* **Question missed:** {item['question']}")
                    st.markdown(f"  * **Topic to review:** `{item['topic']}`")
                    st.markdown(f"  * **Key takeaway:** {item['explanation']}")

            elif score == 10:
                st.balloons()
                st.snow()
                st.success("Okay, superstar, you killed it. Let's see if you can get another perfect score.")
                st.write(f"**Perfect Score:** {score} / {total_q}")
                
                if st.button("Accept challenge: start 15-question quiz"):
                    text = extract_text_from_multiple(uploaded_files)
                    st.session_state.clear()
                    st.session_state.num_questions = 15
                    st.session_state.questions = generate_quiz(text, api_key, 15)
                    st.rerun()

            if st.button("Try another 10-question sprint"):
                st.session_state.clear()
                st.session_state.num_questions = 10
                st.rerun()

        else:
            # Active Question Screen
            st.progress((q_idx + 1) / total_q)
            st.caption(f"Score: {st.session_state.score} of {q_idx}")
            
            curr_q = st.session_state.questions[q_idx]
            st.subheader(f"Question {q_idx + 1} of {total_q}")
            st.write(f"### {curr_q['question']}")
            
            st.write("---")
            for option in curr_q['options']:
                if st.button(option, key=option, disabled=st.session_state.answered):
                    st.session_state.answered = True
                    st.session_state.selected_option = option
                    if option == curr_q['answer']:
                        st.session_state.score += 1
                    else:
                        st.session_state.missed_questions.append({
                            "question": curr_q['question'],
                            "topic": curr_q['topic_ref'],
                            "explanation": curr_q['explanation']
                        })
                    st.rerun()

            if st.session_state.answered:
                selected = st.session_state.selected_option
                correct = curr_q['answer']
                
                if selected == correct:
                    st.success(f"Correct. {curr_q['explanation']}")
                else:
                    st.error(f"Incorrect. Correct answer: {correct}")
                    st.info(f"Takeaway: {curr_q['explanation']}")
                    
                if st.button("Next question"):
                    st.session_state.current_q += 1
                    st.session_state.answered = False
                    st.session_state.selected_option = None
                    st.rerun()

# ----------------- MODE 2: CASE STUDY SIMULATOR -----------------
elif mode == "Case study simulator":
    if not uploaded_files or not api_key:
        st.info("Enter your API key and upload course notes to generate a case study.")
    else:
        if not st.session_state.case_study:
            if st.button("Generate practical case study"):
                with st.spinner("Analyzing files and generating a real-world scenario..."):
                    text = extract_text_from_multiple(uploaded_files)
                    st.session_state.case_study = generate_case_study(text, api_key)
                    st.rerun()
        else:
            case = st.session_state.case_study
            st.header(f"Case Study: {case['title']}")
            st.write(case['scenario'])
            st.subheader("Strategic prompt")
            st.write(f"**{case['question']}**")
            
            st.write("---")
            student_ans = st.text_area("Type your strategic recommendations here:", height=200)
            
            if st.button("Submit solution for evaluation"):
                if student_ans.strip():
                    with st.spinner("Evaluating against course frameworks..."):
                        evaluation = evaluate_case_solution(case['scenario'] + "\n" + case['question'], student_ans, api_key)
                        st.markdown("### Evaluation")
                        st.write(evaluation)
                else:
                    st.warning("Please enter your solution before submitting.")
            
            if st.button("Generate another case study"):
                st.session_state.case_study = None
                st.rerun()
