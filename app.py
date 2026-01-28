import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai
import time

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model ကို ပိုမိုတည်ငြိမ်သော Flash model သုံးပါမည်
model_gemini = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="You are a professional subtitle translator. Translate English text to natural Myanmar (Burmese) language. Give ONLY the translation. No English. No explanations."
)

def translate_to_myanmar(text):
    if not text.strip():
        return ""
    
    try:
        # API Limit မဖြစ်စေရန် စက္ကန့်ပိုင်းခဏစောင့်ခိုင်းခြင်း
        time.sleep(1) 
        response = model_gemini.generate_content(text)
        mm_text = response.text.strip()
        
        # အကယ်၍ ပြန်လာတဲ့စာသားက အင်္ဂလိပ်လိုဖြစ်နေရင် သို့မဟုတ် ဗလာဖြစ်နေရင်
        if not mm_text or mm_text == text:
            return "ဘာသာပြန်နေဆဲဖြစ်ပါသည်..."
            
        return mm_text
    except Exception:
        return "ခေတ္တစောင့်ဆိုင်းပေးပါ..."

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
        
        original_text = segment['text'].strip()
        # Gemini ကို အသုံးပြု၍ မြန်မာလို အမှန်တကယ် ပြန်ခိုင်းခြင်း
        mm_text = translate_to_myanmar(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

# --- Website UI ---
st.set_page_config(page_title="NMH Myanmar Subtitle Tool", page_icon="🎬")
st.title("🎬 NMH Gemini AI Subtitle Maker")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("Gemini AI က မြန်မာလို အကောင်းဆုံး ဘာသာပြန်ပေးနေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                model_whisper = whisper.load_model("base")
                # Whisper က အသံကို အင်္ဂလိပ်စာအရင်ပြောင်းပေးပါသည်
                result = model_whisper.transcribe("temp.mp4", task="translate")
                
                # Gemini က ထိုအင်္ဂလိပ်စာကို မြန်မာစာအဖြစ် ထပ်ဆင့်ဘာသာပြန်ပါသည်
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT File", srt_output, "myanmar_sub.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
            
            if os.path.exists("temp.mp4"):
                os.remove("temp.mp4")
                
