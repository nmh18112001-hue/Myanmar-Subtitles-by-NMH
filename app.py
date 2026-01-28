import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# Gemini ဖြင့် ဘာသာပြန်ပေးမည့် Function
def translate_with_gemini(text):
    if not text.strip():
        return ""
    
    # AI ကို ပိုမိုနားလည်စေရန် ခိုင်းစေချက် (Prompt)
    prompt = f"""Translate this text into natural, spoken Myanmar language (Burmese). 
    Context: This is for a video subtitle. 
    Tone: Friendly and conversational. 
    Text to translate: {text}"""
    
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return text # Error ဖြစ်ရင် မူရင်းစာပဲပြမယ်

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def write_srt(segments):
    srt_content = ""
    # တိုးတက်မှုနှုန်းကို ပြသရန်
    progress_bar = st.progress(0)
    total_segments = len(segments)
    
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        
        # Whisper မှ ရလာသော စာသားကို Gemini ဖြင့် ဘာသာပြန်ခြင်း
        original_text = segment['text'].strip()
        mm_text = translate_with_gemini(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        
        # Progress Update
        progress_bar.progress(i / total_segments)
        
    return srt_content

# --- Website Interface ---
st.set_page_config(page_title="NAING MIN HTET Gemini Translator", page_icon="🎬")

st.title("🎬 NMH Gemini AI Subtitle Maker")
st.write("Gemini AI သုံးထားသဖြင့် ဘာသာပြန် မြန်မာဆန်ဆန် ပိုမိုမှန်ကန်ပါသည်")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/microchip.png")
    st.info("NMH - Digital Marketer at Htoo Khit Gold Shop")
    st.write("Gemini 1.5 Flash Model ကို အသုံးပြုထားပါသည်။")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("Gemini AI ဖြင့် မြန်မာ SRT ထုတ်မည်"):
        with st.spinner("Gemini က ဗီဒီယိုကို နားထောင်ပြီး မြန်မာလို ဘာသာပြန်နေပါသည်..."):
            
