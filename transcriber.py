import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model():
    # Try to load on GPU first, fallback to CPU if kernel is incompatible
    try:
        model = whisper.load_model("base", device="cuda")
        return model, "cuda"
    except Exception:
        model = whisper.load_model("base", device="cpu")
        return model, "cpu"

def transcribe_to_srt(model_info, audio_path):
    model, device = model_info
    # Fallback transcription if CUDA fails during execution
    try:
        result = model.transcribe(audio_path, fp16=(device == "cuda"))
    except Exception:
        # If it failed on CUDA, reload on CPU and try again
        if device == "cuda":
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_path, fp16=False)
        else:
            raise

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
