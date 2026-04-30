import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

def transcribe_to_srt(model, audio_path):
    result = model.transcribe(audio_path)
    srt_content = ""
    for i, segment in enumerate(result['segments']):
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()
        
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
            
        srt_content += f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n"
    return srt_content
