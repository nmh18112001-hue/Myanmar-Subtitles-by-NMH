import streamlit as st
import whisper
import os
from datetime import timedelta
from easygoogletranslate import EasyGoogleTranslate

# ဘာသာပြန်စက် (Translator) ကို စတင်ခြင်း
translator = EasyGoogleTranslate(
    source_language='auto',
    target_language='my',
    timeout=10
)

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
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        
        original_text = segment['text'].strip()
        try:
            # တရုတ် သို့မဟုတ် အင်္ဂလိပ်မှ မြန်မာသို့ တိုက်ရိုက်ပြန်ခြင်း
            mm_text = translator.translate(original_text)
        except:
            mm_text = original_text
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
    return srt_content

st.set_page_config(page_title="NMH Subtitle Tool", page_icon="🎬")

st.title("🇲🇲 Myanmar Auto Subtitle Generator")
st.write("Professional Tool by NMH (Digital Marketer)")

with st.sidebar:
    st.markdown("### 🛠 Developer Info")
    st.info("Created for Content Creators & Htoo Khit Gold Shop")
    st.markdown("[Facebook Profile](https://www.facebook.com/your-profile-link)")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("AI က မြန်မာစာတန်းထိုးများကို အချိန်ကိုက် ဖန်တီးနေပါသည်..."):
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # model ကို 'base' သုံးထားပါသည်
                model = whisper.load_model("base")
                # task="translate" သုံးခြင်းဖြင့် အင်္ဂလိပ်မှတဆင့် မြန်မာသို့ ပိုမိုတိကျစေရန် လုပ်ဆောင်ပါသည်
                result = model.transcribe("temp_video.mp4", task="translate")
                
                srt_output = write_srt(result['segments'])
                
                st.success("အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar_sub.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
                
