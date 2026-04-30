import subprocess
import os

def extract_audio(video_path, audio_path):
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    subprocess.run(cmd, check=True)

def burn_subtitles(video_path, ass_path, output_path):
    # Styling is now natively handled by the .ass file header
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"ass='{ass_path}'",
        "-c:v", "libx264", "-preset", "fast", "-c:a", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd, check=True)


