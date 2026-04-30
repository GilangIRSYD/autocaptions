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

def format_time_ass(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    # ASS format requires exactly 2 digits for centiseconds, and single digit hour
    if cs == 100:
        s += 1
        cs = 0
    if s == 60:
        m += 1
        s = 0
    if m == 60:
        h += 1
        m = 0
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def transcribe_to_ass(model_info, audio_path):
    model, device = model_info
    try:
        result = model.transcribe(audio_path, fp16=(device == "cuda"), word_timestamps=True)
    except Exception:
        if device == "cuda":
            import whisper
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_path, fp16=False, word_timestamps=True)
        else:
            raise

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Roboto,14,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,1.5,1,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header

    for segment in result.get('segments', []):
        words = segment.get('words', [])
        if not words:
            continue

        # Group words into phrases (max 50 chars)
        phrases = []
        current_phrase = []
        for w in words:
            w_text = w['word'].strip()
            test_phrase = " ".join([word['word'] for word in current_phrase] + [w_text])
            if len(test_phrase) > 50 and current_phrase:
                phrases.append(current_phrase)
                current_phrase = [{'word': w_text, 'start': w['start'], 'end': w['end']}]
            else:
                current_phrase.append({'word': w_text, 'start': w['start'], 'end': w['end']})
        if current_phrase:
            phrases.append(current_phrase)

        # Generate overlapping dialogue lines using the {\alpha&HFF&} transparency trick
        for phrase_words in phrases:
            phrase_end = phrase_words[-1]['end']
            
            for i, word_obj in enumerate(phrase_words):
                display_start = word_obj['start']
                display_end = phrase_words[i+1]['start'] if i + 1 < len(phrase_words) else phrase_end
                
                # To prevent text from shifting horizontally when centered, we print the FULL sentence.
                # However, words that haven't been spoken yet are made completely transparent.
                visible_words = [w['word'] for w in phrase_words[:i+1]]
                invisible_words = [w['word'] for w in phrase_words[i+1:]]
                
                if invisible_words:
                    text_to_display = " ".join(visible_words) + " {\\alpha&HFF&}" + " ".join(invisible_words)
                else:
                    text_to_display = " ".join(visible_words)
                    
                ass_content += f"Dialogue: 0,{format_time_ass(display_start)},{format_time_ass(display_end)},Default,,0,0,0,,{text_to_display}\n"

    return ass_content


