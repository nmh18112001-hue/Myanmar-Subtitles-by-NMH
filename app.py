import streamlit as st
import whisper
import os
from datetime import timedelta
import google.generativeai as genai

# --- Gemini API Configuration ---
# ညီကိုပေးထားတဲ့ API Key ကို အသုံးပြုထားပါတယ်
GEMINI_API_KEY = "AIzaSyCsB5NMrCY0OPsXx53u5W7onVAEsG0qjjE"
genai.configure(api_key=GEMINI_API_KEY)
# ပိုမိုမြန်ဆန် တိကျစေရန် flash model ကို သုံးပါမယ်
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

def translate_to_myanmar(text):
    if not text.strip():
        return ""
    
    # AI ကို မြန်မာစာမှလွဲ၍ အင်္ဂလိပ်စာလုံး လုံးဝမပါစေရန် တင်းတင်းကျပ်ကျပ် ခိုင်းထားတဲ့ Prompt ပါ
    prompt = f"Translate the following text into natural, conversational Myanmar (Burmese) language. IMPORTANT: Output ONLY the Myanmar translation. Do not repeat the original text. Do not include any English words. Text to translate: {text}"
    
    try:
        response = model_gemini.generate_content(prompt)
        # ရလာတဲ့ စာသားကို သန့်စင်လိုက်ပါတယ်
        mm_text = response.text.strip()
        return mm_text
    except Exception:
        return "ဘာသာပြန်ရန် အခက်အခဲရှိနေပါသည်"

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
        
        # Whisper မှ ရလာသော အင်္ဂလိပ်စာကို Gemini ဖြင့် မြန်မာလို အတင်းအကြပ် ပြန်ခိုင်းခြင်း
        original_text = segment['text'].strip()
        mm_text = translate_to_myanmar(original_text)
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

# --- Website UI ---
st.set_page_config(page_title="NMH Myanmar Subtitle Tool", page_icon="🎬")
st.title("🎬 NMH Gemini AI Subtitle Maker")
st.write("တရုတ်/အင်္ဂလိပ် အသံများကို မြန်မာစာတန်း (SRT) အဖြစ် တိကျစွာ ပြောင်းလဲပေးပါသည်။")

with st.sidebar:
    st.markdown("### 🛠 Developer Info")
    st.info("NMH - Digital Marketing Expert")
    st.markdown("[Visit Facebook Profile](https://www.facebook.com/your-profile-link)")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("Gemini AI က မြန်မာလို အော်တို ဘာသာပြန်ပေးနေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'base' အသုံးပြုခြင်းက မြန်ဆန်စေပါသည်
                model_whisper = whisper.load_model("base")
                # Whisper က အသံကို အင်္ဂလိပ်စာသား အရင်ပြောင်းပေးပါသည်
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
                
