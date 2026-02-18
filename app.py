import streamlit as st
import streamlit_authenticator as stauth
import google.generativeai as genai
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import time

# --- INITIAL SETUP ---
st.set_page_config(page_title="CreatorScore Pro", layout="wide")

# Configure Gemini Brain
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key in Secrets.")
    st.stop()

# --- USER AUTHENTICATION ---
# In a real app, you'd save this to a database. For now, we use a simple config.
# Normally, you would generate this via a 'Sign Up' form.
credentials = {
    "usernames": {
        "testuser": {
            "name": "Creator Alpha",
            "password": "password123" # In production, use hashed passwords!
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "creator_score_cookie",
    "signature_key",
    cookie_expiry_days=30
)

# Render the Login Box
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")
    st.info("Don't have an account? For this demo, use: testuser / password123")
elif authentication_status == None:
    st.warning("Please enter your username and password")
    st.info("Demo account: testuser | password: password123")

# --- MAIN APP (Only shows after Login) ---
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.title(f"Welcome back, {name}!")
    
    # Upload & Analysis Section
    uploaded_file = st.file_uploader("Upload your content to check the score", type=["mp4", "mov"])

    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            st.video(uploaded_file)
        
        with col2:
            if st.button("Analyze & Score"):
                with st.spinner("AI is analyzing your content..."):
                    temp_path = Path("temp_video.mp4")
                    temp_path.write_bytes(uploaded_file.read())
                    video_file = genai.upload_file(path=str(temp_path))
                    
                    while video_file.state.name == "PROCESSING":
                        time.sleep(1)
                        video_file = genai.get_file(video_file.name)

                    model = genai.GenerativeModel("gemini-3-flash-preview")
                    prompt = "Act as a viral coach. Give a score /100 and 3 tips for more views."
                    
                    response = model.generate_content([video_file, prompt])
                    st.success("Analysis Complete!")
                    st.write(response.text)
                    
                    # Cleanup
                    genai.delete_file(video_file.name)
                    temp_path.unlink()
