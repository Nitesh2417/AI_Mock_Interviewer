import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Mock Interview Coach",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# This is Logic for Streaming
def stream_text(text, delay=0.03):
    """A generator that yields text word-by-word for a streaming effect."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)



st.markdown("""
<style>
    .stChatInput { padding-bottom: 20px; }
    .stSidebar { background-color: #f8f9fa; }
    
    /* Typing Indicator Animation */
    .typing-indicator {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 10px 15px;
      background-color: #f1f3f4;
      border-radius: 15px;
      width: fit-content;
      margin-bottom: 15px;
    }
    .typing-indicator span {
      width: 8px;
      height: 8px;
      background-color: #80868b;
      border-radius: 50%;
      animation: pulse 1.5s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(1) { animation-delay: 0s; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes pulse {
      0%, 100% { transform: scale(0.8); opacity: 0.5; }
      50% { transform: scale(1.2); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)


if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "coach_triggered" not in st.session_state:
    st.session_state.coach_triggered = False


with st.sidebar:
    st.header("⚙️ Interview Setup")
    
    role = st.text_input("Target Role", value="AI Engineer")
    focus = st.selectbox("Focus Area", ["Behavioral", "Technical", "System Design", "Mixed"])
    background = st.text_area(
        "Background / Resume Snippet", 
        value="M.Sc. Computer Science. Built multi-agent AI systems.",
        height=100
    )
    
    st.divider()
    
    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        st.session_state.transcript = []
        st.session_state.coach_triggered = False
        st.session_state.interview_active = True
        
        with st.spinner("Initializing AI Agents..."):
            try:
                res = requests.post(f"{API_URL}/start", json={
                    "target_role": role,
                    "focus_area": focus,
                    "background": background
                })
                res.raise_for_status()
                data = res.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.transcript = data["state"]["transcript"]
                st.toast("Interview Started!", icon="✅")
            except requests.exceptions.RequestException:
                st.error("🚨 Backend connection failed. Is your FastAPI server running?")
                st.session_state.interview_active = False

    if st.session_state.interview_active:
        if st.button("🛑 End / Reset Session", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.transcript = []
            st.session_state.interview_active = False
            st.session_state.coach_triggered = False
            st.rerun()


st.title("🤖 AI Mock Interview Coach")

if not st.session_state.interview_active:
    st.info("👋 Welcome! Please configure your interview in the sidebar and click **Start Interview**.")
else:
   
    is_finished = False
    
    
    for msg in st.session_state.transcript:
        if msg["role"] == "Candidate":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(msg["content"])
        elif msg["role"] == "Interviewer":
            with st.chat_message("assistant", avatar="🎤"):
                st.write(msg["content"])
        elif msg["role"] == "Coach":
            is_finished = True
            with st.chat_message("assistant", avatar="📊"):
                st.success("Interview Complete! Here is your feedback:")
                st.markdown(msg["content"])
                
    
    if is_finished and not st.session_state.coach_triggered:
        st.balloons()
        st.session_state.coach_triggered = True
                
    
    if not is_finished:
        user_input = st.chat_input("Type your answer here...")
        
        if user_input:
            
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(user_input)
                
            
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("""
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            """, unsafe_allow_html=True)
            
            try:
                
                res = requests.post(f"{API_URL}/chat", json={
                    "session_id": st.session_state.session_id,
                    "message": user_input
                })
                res.raise_for_status()
                
                
                thinking_placeholder.empty()
                
                
                new_transcript = res.json()["state"]["transcript"]
                latest_ai_message = new_transcript[-1]
                
                
                with st.chat_message("assistant", avatar="🎤" if latest_ai_message["role"] == "Interviewer" else "📊"):
                    st.write_stream(stream_text(latest_ai_message["content"]))
                
                
                st.session_state.transcript = new_transcript
                st.rerun()
                
            except requests.exceptions.RequestException:
                thinking_placeholder.empty()
                st.error("🚨 Connection lost. Please check the backend server.")