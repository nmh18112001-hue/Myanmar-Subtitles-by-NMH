import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

def translate_to_myanmar(text):
    if not text.strip():
        return ""
    
    # Gemini ကို တိတိကျကျ ခိုင်းစေခြင်း
    prompt = f"Translate the following text strictly into Myanmar (Burmese) language only. Output ONLY the translation. Do not include phrases like 'Here is the translation' or 'Waiting'. Text: {text}"
    
    try:
        response = model_gemini.generate_content(prompt)
        # စာသားအလွတ်ဖြစ်နေလျှင် သို့မဟုတ် Error တက်လျှင် မူရင်းစာသားကိုပဲ ပြန်ပေးရန်
        if response and response.text:
            return response.text.strip()
        else:
            return text
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
        # Gemini ဖြင့် မြန်မာလို အမှန်တကယ် ပြန်ပေးရန် ခိုင်းခြင်း
        mm_text = translate_to_myanmar(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

st.set_page_config(page_title="NMH Subtitle Tool", page_icon="🎬")
st.title("🎬 NMH Gemini AI Subtitle Maker")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("Gemini AI က မြန်မာလို အော်တို ဘာသာပြန်ပေးနေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'base' အသုံးပြုထားပါသည်
                model_whisper = whisper.load_model("base")
                result = model_whisper.transcribe("temp.mp4", task="translate")
                
                # အမှန်တကယ် ဘာသာပြန်ထားသော စာသားများ ထုတ်ယူခြင်း
                srt_output = write_srt(result['segments'])
                
                st.success("မြန်မာ SRT ထုတ်ယူမှု အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT File", srt_output, "myanmar_sub.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
            
            if os.path.exists("temp.mp4"):
                os.remove("temp.mp4")
                
