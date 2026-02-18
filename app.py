import streamlit as st

if not st.user.is_logged_in:
    st.title("Welcome to CreatorScore AI")
    st.write("Please log in to analyze your videos.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

st.write(f"Hello, {st.user.name}! Ready for a viral score?")
# ... (rest of your video upload code here)
import google.generativeai as genai
import time
from pathlib import Path

# 1. THEME & UI: Professional Layout
st.set_page_config(page_title="CreatorScore AI", page_icon="📈", layout="wide")
st.title("📈 CreatorScore AI")
st.caption("Get viral-ready feedback in seconds.")

# 2. SETUP: Secure API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key in Secrets.")
    st.stop()

# 3. SIDEBAR: Settings
with st.sidebar:
    st.header("Settings")
    model_choice = "gemini-3-flash-preview" # Latest 2026 Model
    st.info("Using Gemini 3 Flash for maximum speed.")

# 4. MAIN INTERFACE: Upload Section
uploaded_file = st.file_uploader("Drop your video here", type=["mp4", "mov"])

if uploaded_file:
    col1, col2 = st.columns([1, 1]) # Split screen: Video on left, Results on right
    
    with col1:
        st.video(uploaded_file)
    
    with col2:
        if st.button("🚀 Score My Video", use_container_width=True):
            with st.spinner("Analyzing..."):
                # Process the video
                temp_path = Path("temp_video.mp4")
                temp_path.write_bytes(uploaded_file.read())
                video_file = genai.upload_file(path=str(temp_path))
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(1)
                    video_file = genai.get_file(video_file.name)

                # 5. NEW PROMPT: Concise & Viral-Focused
                model = genai.GenerativeModel(model_choice)
                prompt = """
                Act as a viral growth expert. Give a CONCISE report:
                - Overall Score: (X/100)
                - 1-Sentence Hook Review: (Is it good? Why/Why not?)
                - Top 2 Viral Tips: (What 2 specific things will increase views/likes?)
                - Technical Fix: (1 tip for lighting/audio/text)
                Keep the total answer under 100 words.
                """
                
                response = model.generate_content([video_file, prompt])
                
                # 6. DISPLAY: Dashboard Style
                st.subheader("Your Viral Report")
                st.markdown(response.text)
                
                # Cleanup
                genai.delete_file(video_file.name)
                temp_path.unlink()
