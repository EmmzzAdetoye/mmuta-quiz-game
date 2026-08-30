import streamlit as st
import google.generativeai as genai
import json

# Page Setup
st.set_page_config(page_title="RBSN Strategy Quiz Sprint", page_icon="🎓", layout="centered")

# App Styling (Clean UI with your preferred chartreuse/dark blue tones)
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

st.title("🎓 RBSN Strategy Quiz Sprint")
st.caption("Master's Revision Game: Brand Strategy, Comms, Marketing & Analytics")

# Sidebar for Setup
with st.sidebar:
    st.header("⚙️ Game Setup")
    api_key = st.text_input("Enter Google AI Studio API Key", type="password")
    uploaded_file = st.file_uploader("Upload Lecture Slides / Notes (PDF or TXT)", type=["pdf", "txt"])
    
    if st.button("Reset / Start New Quiz"):
        st.session_state.clear()
        st.rerun()

# Initialize Session State Variables
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

# Function to Generate Questions via Google AI Studio API
def generate_quiz(content, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an expert Professor in Strategic Communications, Marketing, and Brand Strategy.
    Based on the following lecture material, generate EXACTLY 10 randomized multiple-choice quiz questions.
    
    Lecture Material:
    {content[:15000]} # Limit text length for fast response
    
    Format your output strictly as a JSON list of 10 objects. Do not include markdown code block formatting like ```json.
    Each object must have:
    - "question": string
    - "options": list of 4 strings (e.g., ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"])
    - "answer": string (must match one of the exact string options, e.g., "A) Option 1")
    - "explanation": string (1-sentence explanation referencing the core slide concept)
    """
    
    response = model.generate_content(prompt)
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# Screen 1: Generate Quiz
if not st.session_state.questions:
    st.info("👈 Please enter your Google API Key and upload your lecture slides in the sidebar to start!")
    
    if uploaded_file and api_key:
        if st.button("🚀 Generate My 10-Question Quiz"):
            with st.spinner("Generating your interactive study sprint..."):
                try:
                    # Extract text content
                    if uploaded_file.type == "text/plain":
                        text_content = uploaded_file.read().decode("utf-8")
                    else:
                        import pypdf
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        text_content = "".join([page.extract_text() for page in pdf_reader.pages])
                    
                    st.session_state.questions = generate_quiz(text_content, api_key)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating quiz: {e}. Please check your API key.")

# Screen 2: Game Dashboard & Questions
else:
    q_idx = st.session_state.current_q
    
    # Check if Game is Finished
    if q_idx >= len(st.session_state.questions):
        st.balloons()
        st.success(f"🎉 **Sprint Completed! Final Score: {st.session_state.score} / 10**")
        
        score_percent = (st.session_state.score / 10) * 100
        if score_percent >= 80:
            st.write("🌟 **Mastery Status:** Excellent! You have strong recall of these concepts.")
        elif score_percent >= 60:
            st.write("👍 **Mastery Status:** Good job! Review the 2-3 slides you missed.")
        else:
            st.write("📖 **Mastery Status:** Needs another revision sprint before test day.")
            
        if st.button("Play Again with New Questions"):
            st.session_state.clear()
            st.rerun()
            
    else:
        # Progress Bar & Score Banner
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress((q_idx + 1) / 10)
        with col2:
            st.metric("Score", f"{st.session_state.score} / {q_idx}")
            
        # Display Current Question
        curr_q = st.session_state.questions[q_idx]
        st.subheader(f"Question {q_idx + 1} of 10")
        st.write(f"### {curr_q['question']}")
        
        # Interactive Answer Buttons
        st.write("---")
        for option in curr_q['options']:
            if st.button(option, key=option, disabled=st.session_state.answered):
                st.session_state.answered = True
                st.session_state.selected_option = option
                if option == curr_q['answer']:
                    st.session_state.score += 1
                st.rerun()

        # Display Feedback after Clicking an Answer
        if st.session_state.answered:
            selected = st.session_state.selected_option
            correct = curr_q['answer']
            
            if selected == correct:
                st.success(f"✅ **Correct!** {curr_q['explanation']}")
            else:
                st.error(f"❌ **Incorrect.** The correct answer was: **{correct}**")
                st.info(f"💡 **Takeaway:** {curr_q['explanation']}")
                
            if st.button("Next Question ➡️"):
                st.session_state.current_q += 1
                st.session_state.answered = False
                st.session_state.selected_option = None
                st.rerun()
