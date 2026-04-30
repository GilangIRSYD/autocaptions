# Auto-Caption Burn-in System Design Document

## 1. Overview
This document outlines the design and architecture for a Streamlit-based web application that allows users to upload a video, automatically transcribe the audio using OpenAI Whisper (CUDA accelerated), edit the generated subtitles (SRT), and hardcode (burn-in) the subtitles into a final downloadable video using FFmpeg.

## 2. Architecture & Data Flow
- **Web Framework:** Streamlit.
- **Model Engine:** OpenAI Whisper (Base model), loaded into VRAM using `st.cache_resource` to avoid repetitive loading overhead.
- **Processing Engine:** FFmpeg executed via Python's `subprocess`.
- **Temporary Storage:** All file processing happens within a temporary workspace directory (e.g., `/app/workspace/<session_id>/`). This includes:
  - `input.mp4`: The uploaded original video.
  - `audio.wav`: Extracted audio for Whisper processing.
  - `subs.srt`: The generated/edited subtitle file.
  - `output.mp4`: The final video with hardcoded subtitles.
  The directory is purged when the user clicks "Start New Session".

## 3. UI/UX Flow (Accordion/Expander Style)
The UI utilizes a linear step-by-step approach using Streamlit Expanders (`st.expander`) managed by `st.session_state` (tracking steps 1 to 3).

### Step 1: Upload & Transcribe
- An expander contains an `st.file_uploader`.
- Once uploaded, the user clicks "Start Transcription".
- The system extracts audio (FFmpeg) and runs Whisper.
- A loading spinner indicates progress. Once complete, state advances to Step 2.

### Step 2: Review & Edit Subtitle
- An expander opens containing an `st.text_area` populated with the Whisper-generated SRT content.
- The user can review, fix typos, and adjust timestamps directly in the text area.
- A "Save & Start Burn-in" button triggers the next step.

### Step 3: Burn-in & Result
- An expander opens with a spinner indicating CPU-based encoding (FFmpeg `libx264`).
- Once finished, the native `st.video` player is displayed for preview.
- Includes a "Download Final Video" button and a "Start New Project" button to clean up the workspace and reset state.

## 4. Docker & Infrastructure
- **Base Image:** CUDA-enabled Ubuntu runtime (`nvidia/cuda:11.8.0-runtime-ubuntu22.04`).
- **Dependencies:** Python 3.10+, FFmpeg, PyTorch (cu118), Whisper, and Streamlit.
- **Docker Compose:** Maps port 8501, mounts the workspace volume, and exposes the NVIDIA GPU via `deploy.resources.reservations.devices`.

## 5. Error Handling
- **Invalid Uploads:** Handled during Step 1; FFmpeg extraction errors will trigger an `st.error` prompting for a valid video.
- **Silent/Empty Audio:** Handled by validating Whisper's output. Displays a warning if no transcription is generated.
- **SRT Formatting Errors:** If the user breaks the SRT format in Step 2, FFmpeg will throw an error during burn-in. The application will catch `stderr`, display an `st.error` alert, and allow the user to fix the text without restarting the entire process.
