import streamlit as st
import google.generativeai as genai
import time
import os
from moviepy.editor import VideoFileClip

# --- Gemini API Config ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)

def process_video_to_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path)
    return audio_path

# --- UI Interface ---
st.set_page_config(page_title="NMH Gemini Subtitle Expert", layout="wide")
st.title("🎬 NMH Gemini AI Subtitle Expert")

tab1, tab2 = st.tabs(["Step 1: Video to English SRT", "Step 2: English SRT to Myanmar"])

# --- Part 1: Video to English SRT ---
with tab1:
    st.header("ဗီဒီယိုမှ အင်္ဂလိပ်စာတန်းထုတ်ယူခြင်း")
    video_file = st.file_uploader("Video တင်ပါ", type=["mp4", "mov", "avi"], key="vid_up")
    
    if video_file and st.button("Generate English SRT"):
        with st.spinner("AI က ဗီဒီယိုကို နားထောင်နေပါသည်..."):
            with open("temp_v.mp4", "wb") as f:
                f.write(video_file.getbuffer())
            
            # ဗီဒီယိုမှ အသံကို သီးသန့်ထုတ်ယူခြင်း (Error ကင်းစေရန်)
            audio_path = process_video_to_audio("temp_v.mp4")
            
            # Gemini ဆီ Audio ပို့ခြင်း
            gemini_file = genai.upload_file(audio_path, mime_type="audio/mpeg")
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Generate a precise English SRT subtitle file with timestamps based on this audio. Output ONLY the SRT content."
            
            response = model.generate_content([gemini_file, prompt])
            srt_eng = response.text.strip()
            
            st.success("English SRT ရပါပြီ!")
            st.download_button("Download English SRT", srt_eng, "english.srt")
            st.text_area("Preview", srt_eng, height=200)
            
            # ဖိုင်ဟောင်းများ ရှင်းလင်းခြင်း
            os.remove("temp_v.mp4")
            os.remove(audio_path)

# --- Part 2: English SRT to Myanmar ---
with tab2:
    st.header("အင်္ဂလိပ် SRT မှ မြန်မာဘာသာပြန်ခြင်း")
    srt_input = st.file_uploader("English SRT ဖိုင်ကို ပြန်တင်ပါ", type=["srt"], key="srt_up")
    
    if srt_input and st.button("Translate to Myanmar"):
        with st.spinner("Gemini AI က မြန်မာလို ဘာသာပြန်ပေးနေပါသည်..."):
            eng_content = srt_input.read().decode("utf-8")
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Translate the following English SRT content into natural, conversational Myanmar language. Keep the timestamps exactly the same. Output ONLY the translated SRT content: \n\n{eng_content}"
            
            response = model.generate_content(prompt)
            srt_mm = response.text.strip()
            
            st.success("မြန်မာ SRT ရပါပြီ!")
            st.download_button("Download Myanmar SRT", srt_mm, "myanmar_final.srt")
            st.text_area("Preview", srt_mm, height=200)
            
