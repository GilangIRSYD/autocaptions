# Auto-Caption Burn-in System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit app to upload video, transcribe with Whisper (GPU), edit SRT, and burn-in with FFmpeg.

**Architecture:** Single-page Streamlit app with accordion-style flow using session state. Uses FFmpeg for audio extraction and video burn-in, and OpenAI Whisper for transcription.

**Tech Stack:** Streamlit, OpenAI Whisper, FFmpeg, Docker, NVIDIA CUDA.

---

### Task 1: Docker Infrastructure

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/requirements.txt`
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/Dockerfile`
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/docker-compose.yml`

- [ ] **Step 1: Create requirements.txt**
```text
streamlit
openai-whisper
torch
torchaudio
```

- [ ] **Step 2: Create Dockerfile**
```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

- [ ] **Step 3: Create docker-compose.yml**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Task 2: Core Utilities (FFmpeg Wrappers)

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/utils.py`

- [ ] **Step 1: Implement extract_audio**
```python
import subprocess
import os

def extract_audio(video_path, audio_path):
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    subprocess.run(cmd, check=True)
```

- [ ] **Step 2: Implement burn_subtitles**
```python
def burn_subtitles(video_path, srt_path, output_path):
    # Using libx264 for CPU encoding as per spec
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='Alignment=2,FontSize=24,MarginV=20'",
        "-c:v", "libx264", "-preset", "fast", "-c:a", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd, check=True)
```

### Task 3: Transcription Service

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/transcriber.py`

- [ ] **Step 1: Implement load_model with caching**
```python
import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")
```

- [ ] **Step 2: Implement transcribe_audio**
```python
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
```

### Task 4: Streamlit App Shell & Step 1

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/autocaption/app.py`

- [ ] **Step 1: Initialize session state**
```python
import streamlit as st
import os
import shutil
from utils import extract_audio, burn_subtitles
from transcriber import load_whisper_model, transcribe_to_srt

st.set_page_config(page_title="Auto-Caption Burn-in", layout="wide")
st.title("🎬 Auto-Caption Burn-in System")

if "step" not in st.session_state:
    st.session_state.step = 1
if "workdir" not in st.session_state:
    st.session_state.workdir = "workspace/session"
    os.makedirs(st.session_state.workdir, exist_ok=True)
```

- [ ] **Step 2: Implement Step 1 Expander (Upload)**
```python
with st.expander("Step 1: Upload & Transcribe", expanded=(st.session_state.step == 1)):
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
    if uploaded_file:
        input_path = os.path.join(st.session_state.workdir, "input.mp4")
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Start Transcription"):
            with st.spinner("Processing..."):
                audio_path = os.path.join(st.session_state.workdir, "audio.wav")
                extract_audio(input_path, audio_path)
                model = load_whisper_model()
                st.session_state.srt_content = transcribe_to_srt(model, audio_path)
                st.session_state.step = 2
                st.rerun()
```

### Task 5: Step 2 & 3 UI

**Files:**
- Modify: `/Users/gilangsafera/Documents/gilang/code/autocaption/app.py`

- [ ] **Step 1: Implement Step 2 Expander (Edit)**
```python
with st.expander("Step 2: Review & Edit Subtitle", expanded=(st.session_state.step == 2)):
    if "srt_content" in st.session_state:
        edited_srt = st.text_area("Edit SRT content", st.session_state.srt_content, height=300)
        if st.button("Save & Start Burn-in"):
            st.session_state.srt_content = edited_srt
            srt_path = os.path.join(st.session_state.workdir, "subs.srt")
            with open(srt_path, "w") as f:
                f.write(edited_srt)
            st.session_state.step = 3
            st.rerun()
```

- [ ] **Step 2: Implement Step 3 Expander (Burn-in)**
```python
with st.expander("Step 3: Burn-in & Result", expanded=(st.session_state.step == 3)):
    if st.session_state.step == 3:
        input_path = os.path.join(st.session_state.workdir, "input.mp4")
        srt_path = os.path.join(st.session_state.workdir, "subs.srt")
        output_path = os.path.join(st.session_state.workdir, "output.mp4")
        
        if not os.path.exists(output_path):
            with st.spinner("Burning subtitles (CPU Encoding)..."):
                burn_subtitles(input_path, srt_path, output_path)
        
        st.video(output_path)
        with open(output_path, "rb") as f:
            st.download_button("Download Final Video", f, file_name="output_captioned.mp4")
            
        if st.button("Start New Project"):
            shutil.rmtree(st.session_state.workdir)
            st.session_state.clear()
            st.rerun()
```
