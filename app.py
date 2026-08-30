import streamlit as st
import google.generativeai as genai
import json

# Page Setup
st.set_page_config(page_title="RBSN Strategy Hub", page_icon="🎓", layout="centered")

# Custom Styling (Dark Blue & Chartreuse Theme)
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #105977;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #A8CF45;
        color: #105977;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 RBSN Revision & Case Study Hub")
st.caption("Strategic Communications, Brand Strategy & Marketing Revision Engine")

# Sidebar
with st.sidebar:
    st.header("⚙️ Game Setup")
    api_key = st.text_input("Enter Google AI Studio API Key", type="password")
    uploaded_file = st.file_uploader("Upload Lecture Slides / Notes (PDF or TXT)", type=["pdf", "txt"])
    
    st.write("---")
    mode = st.radio("Select Mode", ["10-Question Quiz", "Case Study Simulator"])
    
    if st.button("Reset / New Session"):
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
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        import pypdf
        pdf_reader = pypdf.PdfReader(file)
        return "".join([page.extract_text() for page in pdf_reader.pages])

# AI Prompt Generators
def generate_quiz(content, api_key, num_q=10):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert Professor in Strategic Communications, Marketing, and Brand Strategy.
    Based on the following lecture material, generate EXACTLY {num_q} randomized multiple-choice quiz questions.
    
    Lecture Material:
    {content[:15000]}
    
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
    Based on the following lecture notes, create 1 realistic strategic business/comms case study scenario.
    
    Lecture Material:
    {content[:15000]}
    
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
    2. What they got right (Strategic Strengths).
    3. Missing elements / Gaps based on lecture principles.
    4. 2-sentence actionable advice.
    """
    response = model.generate_content(prompt)
    return response.text

# ----------------- MODE 1: QUIZ SPRINT -----------------
if mode == "10-Question Quiz":
    if not uploaded_file or not api_key:
        st.info("👈 Enter your Google AI Studio API Key and upload your notes in the sidebar to start!")
    elif not st.session_state.questions:
        if st.button(f"🚀 Start {st.session_state.num_questions}-Question Quiz Sprint"):
            with st.spinner("Building your custom quiz..."):
                try:
                    text = extract_text(uploaded_file)
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
                st.warning("### Didn't you say you were studying hard?")
                st.write(f"**Your Score:** {score} / {total_q}")
                st.write("---")
                st.subheader("📚 Where to Focus Your Reading:")
                for item in st.session_state.missed_questions:
                    st.markdown(f"* **Question:** {item['question']}")
                    st.markdown(f"  * **Topic to Review:** `{item['topic']}`")
                    st.markdown(f"  * **Explanation:** {item['explanation']}")
                    st.write("")

            elif score in [8, 9]:
                st.info("### Looks like someone's been hitting the books. Great job, but let's shoot for a perfect score next time!")
                st.write(f"**Your Score:** {score} / {total_q}")
                st.write("---")
                st.subheader("💡 Focus Area for a Perfect Score:")
                for item in st.session_state.missed_questions:
                    st.markdown(f"* **Question Missed:** {item['question']}")
                    st.markdown(f"  * **Topic to Review:** `{item['topic']}`")
                    st.markdown(f"  * **Key Takeaway:** {item['explanation']}")

            elif score == 10:
                st.balloons()
                st.snow()
                st.success("### Okay, superstar, you killed it! Let's see if you can get another perfect score!")
                st.write(f"**Perfect Score!** {score} / {total_q}")
                
                if st.button("🔥 Accept Challenge: Start 15-Question Quiz"):
                    text = extract_text(uploaded_file)
                    st.session_state.clear()
                    st.session_state.num_questions = 15
                    st.session_state.questions = generate_quiz(text, api_key, 15)
                    st.rerun()

            if st.button("🔄 Try Another 10-Question Sprint"):
                st.session_state.clear()
                st.session_state.num_questions = 10
                st.rerun()

        else:
            # Active Question Screen
            st.progress((q_idx + 1) / total_q)
            st.metric("Current Score", f"{st.session_state.score} / {q_idx}")
            
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
                    st.success(f"✅ **Correct!** {curr_q['explanation']}")
                else:
                    st.error(f"❌ **Incorrect.** Correct answer: **{correct}**")
                    st.info(f"💡 **Takeaway:** {curr_q['explanation']}")
                    
                if st.button("Next Question ➡️"):
                    st.session_state.current_q += 1
                    st.session_state.answered = False
                    st.session_state.selected_option = None
                    st.rerun()

# ----------------- MODE 2: CASE STUDY SIMULATOR -----------------
elif mode == "Case Study Simulator":
    if not uploaded_file or not api_key:
        st.info("👈 Enter your API Key and upload your course notes to generate a Case Study!")
    else:
        if not st.session_state.case_study:
            if st.button("📑 Generate Practical Case Study"):
                with st.spinner("Generating real-world business scenario from notes..."):
                    text = extract_text(uploaded_file)
                    st.session_state.case_study = generate_case_study(text, api_key)
                    st.rerun()
        else:
            case = st.session_state.case_study
            st.header(f"🏢 Case Study: {case['title']}")
            st.write(case['scenario'])
            st.subheader("🎯 Strategic Prompt:")
            st.write(f"**{case['question']}**")
            
            st.write("---")
            student_ans = st.text_area("Type your strategic recommendations / solution here:", height=200)
            
            if st.button("Submit Case Solution for AI Evaluation"):
                if student_ans.strip():
                    with st.spinner("Evaluating against course frameworks..."):
                        evaluation = evaluate_case_solution(case['scenario'] + "\n" + case['question'], student_ans, api_key)
                        st.markdown("### 📊 AI Professor Evaluation:")
                        st.write(evaluation)
                else:
                    st.warning("Please enter your solution before submitting.")
            
            if st.button("Generate Another Case Study"):
                st.session_state.case_study = None
                st.rerun()
