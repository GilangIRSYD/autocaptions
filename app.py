import streamlit as st
import os
import shutil
from utils import extract_audio, burn_subtitles
from transcriber import load_whisper_model, transcribe_to_ass

st.set_page_config(page_title="Auto-Caption Burn-in", layout="wide")
st.title("🎬 Auto-Caption Burn-in System")
st.caption("Version 1.1.1 - Font Size Fix & Animation Optimization")

# Ensure workdir exists
workdir = "workspace/session"
if not os.path.exists(workdir):
    os.makedirs(workdir, exist_ok=True)

if "step" not in st.session_state:
    st.session_state.step = 1

# Step 1: Upload & Transcribe
with st.expander("Step 1: Upload & Transcribe", expanded=(st.session_state.step == 1)):
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
    if uploaded_file:
        input_path = os.path.join(workdir, "input.mp4")
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Start Transcription"):
            with st.spinner("Mengekstrak audio dan transkripsi AI..."):
                try:
                    audio_path = os.path.join(workdir, "audio.wav")
                    extract_audio(input_path, audio_path)
                    
                    model_info = load_whisper_model()
                    ass_content = transcribe_to_ass(model_info, audio_path)
                    
                    st.session_state.ass_content = ass_content
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during transcription: {e}")

# Step 2: Review & Edit Subtitle
with st.expander("Step 2: Review & Edit Subtitle", expanded=(st.session_state.step == 2)):
    if "ass_content" in st.session_state:
        edited_ass = st.text_area("Edit ASS content", st.session_state.ass_content, height=300)
        if st.button("Save & Start Burn-in"):
            st.session_state.ass_content = edited_ass
            ass_path = os.path.join(workdir, "subs.ass")
            with open(ass_path, "w") as f:
                f.write(edited_ass)
            st.session_state.step = 3
            st.rerun()

# Step 3: Burn-in & Result
with st.expander("Step 3: Burn-in & Result", expanded=(st.session_state.step == 3)):
    if st.session_state.step == 3:
        input_path = os.path.join(workdir, "input.mp4")
        ass_path = os.path.join(workdir, "subs.ass")
        output_path = os.path.join(workdir, "output.mp4")
        
        if not os.path.exists(output_path):
            with st.spinner("Melakukan hardcode subtitle (CPU Encoding)..."):
                try:
                    burn_subtitles(input_path, ass_path, output_path)
                except Exception as e:
                    st.error(f"Error during burn-in: {e}")
        
        if os.path.exists(output_path):
            st.video(output_path)
            with open(output_path, "rb") as f:
                st.download_button("Download Final Video", f, file_name="output_captioned.mp4")
            
            if st.button("Start New Project"):
                if os.path.exists(workdir):
                    shutil.rmtree(workdir)
                st.session_state.clear()
                st.rerun()
