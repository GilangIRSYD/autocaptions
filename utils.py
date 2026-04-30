import subprocess
import os

def extract_audio(video_path, audio_path):
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    subprocess.run(cmd, check=True)

def burn_subtitles(video_path, srt_path, output_path):
    # Using libx264 for CPU encoding as per spec
    # Refined Opaque Bounding Box styling
    style = "Alignment=2,FontSize=16,MarginV=40,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=3,Outline=1"
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "fast", "-c:a", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd, check=True)


