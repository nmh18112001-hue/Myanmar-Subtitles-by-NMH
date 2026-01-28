import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Config ---
# ညီကိုပေးထားတဲ့ Key ကို အသုံးပြုထားပါတယ်
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# Gemini ဖြင့် မြန်မာလို ဘာသာပြန်ခိုင်းသည့် Function
def translate_to_myanmar(text):
    if not text.strip():
        return ""
    # AI ကို မြန်မာလိုပဲ ပြန်ပေးဖို့ တိတိကျကျ ခိုင်းစေခြင်း
    prompt = f"Translate the following text into natural, fluent Myanmar (Burmese) language only. This is for video subtitles: '{text}'"
    try:
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return text

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
    progress_bar = st.progress(0)
    total_segments = len(segments)
    
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        
        # Whisper မှ ရလာသော အင်္ဂလိပ်စာကို Gemini ဖြင့် မြန်မာလို ပြန်ခိုင်းခြင်း
        original_text = segment['text'].strip()
        mm_text = translate_to_myanmar(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

st.title("🎬 NMH Gemini Myanmar Subtitle Maker")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) ထုတ်မည်"):
        with st.spinner("Gemini AI က မြန်မာလို ဘာသာပြန်ပေးနေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'base' အသုံးပြုခြင်းက မြန်ဆန်စေပါသည်
                model_whisper = whisper.load_model("base")
                # task="translate" သည် အသံကို အင်္ဂလိပ်စာသား အရင်ပြောင်းပေးပါသည်
                result = model_whisper.transcribe("temp.mp4", task="translate")
                
                # အင်္ဂလိပ်စာသားများကို မြန်မာလို ပြောင်းလဲ၍ SRT ရေးသားခြင်း
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar_sub.srt")
            except Exception as e:
                st.error(f"Error: {e}")

