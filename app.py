import streamlit as st
import google.generativeai as genai
import time
from pathlib import Path

# 1. SETUP: This makes the app look professional
st.set_page_config(page_title="AI Video Coach", page_icon="🎥")
st.title("🎥 AI Video Performance Coach")
st.markdown("Upload your video to get a professional score and improvement tips.")

# 2. SECURITY: This looks for your "Secret" API Key
# When you deploy, you will paste your key into Streamlit's settings
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add your GEMINI_API_KEY to the Streamlit Secrets.")
    st.stop()

# 3. UPLOADER: The button for the user
uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Show the video to the user
    st.video(uploaded_file)
    
    if st.button("Analyze My Video"):
        with st.spinner("The AI is watching your video... (this may take a minute)"):
            try:
                # Save the uploaded file temporarily
                temp_path = Path("temp_video.mp4")
                temp_path.write_bytes(uploaded_file.read())

                # Upload to Google Gemini
                video_file = genai.upload_file(path=str(temp_path))
                
                # Wait for the video to be processed by Google
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                # 4. THE PROMPT: Our "Master Instructions"
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = """
                Analyze this video as a high-end social media coach. 
                Provide a score from 1-100 and give feedback on:
                1. Hook Strength: Did it grab attention in 3 seconds?
                2. Technicals: Lighting, Framing, and Audio/Music balance.
                3. On-screen Text: Is it readable and in the 'safe zone'?
                4. Improvement Tips: Give 3 clear steps to make the next take better.
                """
                
                # Generate the feedback
                response = model.generate_content([video_file, prompt])
                
                # 5. DISPLAY: Show the results!
                st.success("Analysis Complete!")
                st.markdown("### 🏆 Your Video Report")
                st.write(response.text)
                
                # Cleanup: Delete the file from Google to stay in the free tier
                genai.delete_file(video_file.name)
                temp_path.unlink()

            except Exception as e:
                st.error(f"Something went wrong: {e}")
