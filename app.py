import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

def translate_with_gemini(text):
    if not text.strip():
        return ""
    prompt = f"Translate this text into natural, spoken Myanmar language (Burmese) for video subtitles: {text}"
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
        original_text = segment['text'].strip()
        mm_text = translate_with_gemini(original_text)
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

# --- Website UI ---
st.set_page_config(page_title="NMH Gemini Translator", page_icon="🎬")
st.title("🎬 NMH Gemini AI Subtitle Maker")

with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/microchip.png")
    st.info("NMH - Digital Marketer at Htoo Khit Gold Shop")
    st.write("Gemini 1.5 Flash Model ကို အသုံးပြုထားပါသည်။")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("Gemini AI ဖြင့် မြန်မာ SRT ထုတ်မည်"):
        with st.spinner("Gemini က ဗီဒီယိုကို နားထောင်ပြီး မြန်မာလို ဘာသာပြန်နေပါသည်..."):
            # ဗီဒီယိုကို ယာယီသိမ်းဆည်းခြင်း
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Whisper model load လုပ်ခြင်း
                model_whisper = whisper.load_model("base")
                # တရုတ်/အခြားဘာသာကို အင်္ဂလိပ်အရင်ပြန်
                result = model_whisper.transcribe("temp_video.mp4", task="translate")
                
                # Gemini ဖြင့် မြန်မာလို ထပ်ဆင့်ပြန်ခြင်း
                srt_output = write_srt(result['segments'])
                
                st.success("Gemini SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "gemini_translated.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error ဖြစ်ပွားပါသည်: {e}")
            
            # အလုပ်ပြီးလျှင် ယာယီဖိုင်ကို ဖျက်ခြင်း
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
                
