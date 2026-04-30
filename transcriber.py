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

def format_time_srt(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    if s == 60:
        m += 1
        s = 0
    if m == 60:
        h += 1
        m = 0
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def format_time_ass(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
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

def transcribe_to_srt(model_info, audio_path):
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

    srt_content = ""
    srt_index = 1

    for segment in result.get('segments', []):
        words = segment.get('words', [])
        if not words:
            continue

        current_phrase = []
        for w in words:
            w_text = w['word'].strip()
            test_phrase = " ".join([word['word'] for word in current_phrase] + [w_text])
            if len(test_phrase) > 50 and current_phrase:
                # Output current phrase
                start_time = current_phrase[0]['start']
                end_time = current_phrase[-1]['end']
                text = " ".join([word['word'] for word in current_phrase])
                srt_content += f"{srt_index}\n{format_time_srt(start_time)} --> {format_time_srt(end_time)}\n{text}\n\n"
                srt_index += 1
                current_phrase = [{'word': w_text, 'start': w['start'], 'end': w['end']}]
            else:
                current_phrase.append({'word': w_text, 'start': w['start'], 'end': w['end']})
                
        if current_phrase:
            start_time = current_phrase[0]['start']
            end_time = current_phrase[-1]['end']
            text = " ".join([word['word'] for word in current_phrase])
            srt_content += f"{srt_index}\n{format_time_srt(start_time)} --> {format_time_srt(end_time)}\n{text}\n\n"
            srt_index += 1

    return srt_content

def parse_srt_time(time_str):
    import re
    parts = re.split('[:,]', time_str)
    h, m, s, ms = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    return h * 3600 + m * 60 + s + ms / 1000.0

def convert_srt_to_ass(srt_text):
    import re
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Roboto,70,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,4,2,2,10,10,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header
    
    # Split into blocks, handle both \r\n and \n
    blocks = srt_text.replace('\r\n', '\n').strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_match = re.search(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
            if not time_match: continue
            
            start_time = parse_srt_time(time_match.group(1))
            end_time = parse_srt_time(time_match.group(2))
            text = " ".join(lines[2:])
            words = text.split()
            
            if not words: continue
            
            duration_per_word = (end_time - start_time) / len(words)
            phrase_words = []
            
            for i, word in enumerate(words):
                w_start = start_time + (i * duration_per_word)
                w_end = start_time + ((i + 1) * duration_per_word)
                phrase_words.append({'word': word, 'start': w_start, 'end': w_end})
                
            for i, word_obj in enumerate(phrase_words):
                display_start = word_obj['start']
                display_end = phrase_words[i+1]['start'] if i + 1 < len(phrase_words) else end_time
                
                visible_words = [w['word'] for w in phrase_words[:i+1]]
                invisible_words = [w['word'] for w in phrase_words[i+1:]]
                
                if invisible_words:
                    text_to_display = " ".join(visible_words) + " {\\alpha&HFF&}" + " ".join(invisible_words)
                else:
                    text_to_display = " ".join(visible_words)
                    
                ass_content += f"Dialogue: 0,{format_time_ass(display_start)},{format_time_ass(display_end)},Default,,0,0,0,,{text_to_display}\n"
                
    return ass_content



