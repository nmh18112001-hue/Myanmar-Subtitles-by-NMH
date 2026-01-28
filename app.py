import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Config ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

def translate_to_myanmar(text):
    if not text.strip():
        return ""
    
    # AI ကို မြန်မာစာမှလွဲ၍ အခြားဘာမှ မရေးရန် အမိန့်ပေးထားသည့် Prompt
    prompt = f"""
    Task: Translate the following English text into natural, spoken Myanmar (Burmese) language.
    Constraint: Output ONLY the translated Myanmar text. Do not include any English, explanations, or notes.
    Context: Video subtitles for Myanmar audience.
    Text: {text}
    """
    
    try:
        response = model_gemini.generate_content(prompt)
        # ရလာတဲ့ စာသားထဲကမှ မြန်မာစာ မဟုတ်တာတွေကို ဖယ်ရှားဖို့ ကြိုးစားပါမယ်
        translated_text = response.text.strip()
        return translated_text
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
        # Gemini ကို အသုံးပြု၍ မြန်မာလို အတင်းအကြပ် ပြန်ခိုင်းခြင်း
        mm_text = translate_to_myanmar(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

st.title("🎬 NMH Gemini Myanmar Subtitle Maker")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) ထုတ်မည်"):
        with st.spinner("Gemini AI က မြန်မာလို အော်တို ဘာသာပြန်ပေးနေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'base' အသုံးပြုထားပါသည်
                model_whisper = whisper.load_model("base")
                # Whisper က အသံကို အင်္ဂလိပ်စာအရင်ပြောင်းပေးပါသည်
                result = model_whisper.transcribe("temp.mp4", task="translate")
                
                # Gemini က ထိုအင်္ဂလိပ်စာကို မြန်မာစာအဖြစ် ထပ်ဆင့်ဘာသာပြန်ပါသည်
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar_translated.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
