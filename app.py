import streamlit as st
import google.generativeai as genai
import time
import os

# --- Gemini API Config ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# --- UI Interface ---
st.set_page_config(page_title="NMH Gemini Subtitle Expert", layout="wide")
st.title("🎬 NMH Gemini Direct Subtitle Tool")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT", "Step 2: English SRT to Myanmar"])

# --- Part 1: Video to English SRT ---
with tab1:
    st.header("ဗီဒီယိုမှ အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="vid_up")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("Gemini က ဗီဒီယိုကို ကြည့်ပြီး အင်္ဂလိပ် SRT ထုတ်ပေးနေသည်..."):
            with open("temp_v.mp4", "wb") as f:
                f.write(video_file.getbuffer())
            
            # Gemini ဆီ Video ပို့ခြင်း
            gemini_file = upload_to_gemini("temp_v.mp4", mime_type="video/mp4")
            while gemini_file.state.name == "PROCESSING":
                time.sleep(2)
                gemini_file = genai.get_file(gemini_file.name)

            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Watch this video and generate a precise English SRT subtitle file with timestamps. Output only the SRT content."
            
            response = model.generate_content([gemini_file, prompt])
            srt_eng = response.text.strip()
            
            st.success("English SRT ရပါပြီ!")
            st.download_button("Download English SRT", srt_eng, "english.srt")
            st.text_area("Preview", srt_eng, height=200)

# --- Part 2: English SRT to Myanmar ---
with tab2:
    st.header("အင်္ဂလိပ် SRT မှ မြန်မာဘာသာပြန်ခြင်း")
    srt_file = st.file_uploader("English SRT ဖိုင်ကို ပြန်တင်ပါ", type=["srt"], key="srt_up")
    
    if srt_file and st.button("Translate to Myanmar"):
        with st.spinner("Gemini က မြန်မာလို အလှပဆုံး ဘာသာပြန်ပေးနေသည်..."):
            eng_content = srt_file.read().decode("utf-8")
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Translate the following English SRT content into natural, conversational Myanmar language. Keep the timestamps exactly the same. Output only the translated SRT content: \n\n{eng_content}"
            
            response = model.generate_content(prompt)
            srt_mm = response.text.strip()
            
            st.success("မြန်မာ SRT ရပါပြီ!")
            st.download_button("Download Myanmar SRT", srt_mm, "myanmar_final.srt")
            st.text_area("Preview", srt_mm, height=200)
            
