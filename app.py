import streamlit as st
import whisper
import os
from datetime import timedelta
from deep_translator import GoogleTranslator

# ဘာသာပြန်စက်ကို စတင်ခြင်း (Microsoft/Google Engine သုံးပါမည်)
translator = GoogleTranslator(source='auto', target='my')

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
        
        # မူရင်းအင်္ဂလိပ်စာသားကို မြန်မာလို တိုက်ရိုက်ပြန်ခြင်း
        original_text = segment['text'].strip()
        try:
            mm_text = translator.translate(original_text)
        except:
            mm_text = original_text # Error ဖြစ်ပါက မူရင်းစာပြရန်
            
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        progress_bar.progress(i / total_segments)
        
    return srt_content

st.set_page_config(page_title="NMH Subtitle Tool", page_icon="🎬")
st.title("🎬 NMH Myanmar Subtitle Tool")
st.write("Professional SRT Generator (No Key Required)")

uploaded_file = st.file_uploader("ဗီဒီယို တင်ပေးပါ", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("မြန်မာစာတန်းထိုး (SRT) စတင်ထုတ်မည်"):
        with st.spinner("အသံကို နားထောင်ပြီး မြန်မာလို ဘာသာပြန်နေပါသည်..."):
            with open("temp.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Whisper Model Load
                model = whisper.load_model("base")
                # Task Translate က အသံကို စာသားအရင်ပြောင်းပေးပါသည်
                result = model.transcribe("temp.mp4", task="translate")
                
                # မြန်မာ SRT ထုတ်ယူခြင်း
                srt_output = write_srt(result['segments'])
                
                st.success("အောင်မြင်ပါသည်!")
                st.download_button("Download Myanmar SRT", srt_output, "myanmar_sub.srt")
                
                with st.expander("စာသားများကို ကြည့်ရှုရန်"):
                    st.text(srt_output)
            except Exception as e:
                st.error(f"Error: {e}")
            
            if os.path.exists("temp.mp4"):
                os.remove("temp.mp4")
                
