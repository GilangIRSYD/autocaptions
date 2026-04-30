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
    # Cinematic styling: Roboto Bold with outline and shadow (No Box)
    style = "FontName=Roboto,Bold=1,FontSize=18,Alignment=2,MarginV=30,Outline=1.5,Shadow=1,PrimaryColour=&H00FFFFFF"





    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "fast", "-c:a", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd, check=True)


