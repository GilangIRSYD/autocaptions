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
            import whisper
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_path, fp16=False)
        else:
            raise

    srt_content = ""
    srt_index = 1
    
    def format_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    for segment in result['segments']:
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()
        
        # Split text if longer than 50 characters
        if len(text) > 50:
            # Find the best place to split (nearest space to the middle)
            mid = len(text) // 2
            split_index = text.rfind(' ', 0, mid + 10)
            if split_index == -1:
                split_index = text.find(' ', mid)
                
            if split_index != -1:
                part1 = text[:split_index].strip()
                part2 = text[split_index:].strip()
                
                # Proportional time split
                duration = end - start
                ratio = len(part1) / len(text)
                mid_time = start + (duration * ratio)
                
                srt_content += f"{srt_index}\n{format_time(start)} --> {format_time(mid_time)}\n{part1}\n\n"
                srt_index += 1
                srt_content += f"{srt_index}\n{format_time(mid_time)} --> {format_time(end)}\n{part2}\n\n"
                srt_index += 1
                continue
                
        # If not split
        srt_content += f"{srt_index}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n"
        srt_index += 1
        
    return srt_content

