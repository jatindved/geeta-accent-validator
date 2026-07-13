import os
import re
import tempfile
import textwrap
import urllib.request
from html import escape

import numpy as np
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Learn Geeta - Shloka Accent & Rhythm Validator",
    page_icon="🕉️",
    layout="centered",
)

# ============================================================
# LANGUAGE OPTIONS
# ============================================================
LANGUAGE_OPTIONS = [
    ("English", "en"),
    ("हिन्दी", "hi"),
    ("অসমীয়া", "as"),
    ("বাংলা", "bn"),
    ("ગુજરાતી", "gu"),
    ("ಕನ್ನಡ", "kn"),
    ("മലയാളം", "ml"),
    ("မৈতৈলোন্ / Manipuri", "mni"),
    ("मराठी", "mr"),
    ("नेपाली", "ne"),
    ("ଓଡ଼ିଆ", "or"),
    ("सिन्धी", "sd"),
    ("தமிழ்", "ta"),
    ("తెలుగు", "te"),
]

LANGUAGE_NAME_TO_CODE = dict(LANGUAGE_OPTIONS)

# ============================================================
# COMPLETE INTERFACE TRANSLATIONS
# ============================================================
I18N = {
    "en": {
        "language": "Interface Language",
        "title": "🕉️ Learn Geeta - Shloka Accent & Rhythm Validator",
        "subtitle": "Dual-script chanting, timing, rhythm and pitch comparison.",
        "chapter": "Select Chapter",
        "from_shloka": "From Shloka No.",
        "to_shloka": "To Shloka No.",
        "audio": "Upload Chanting Audio",
        "run": "🔍 Run Chanting Evaluation",
        "select_required": "Please select the chapter and shloka range.",
        "audio_required": "Please upload an audio file.",
        "analyzing": "Analyzing the chanting performance...",
        "verse_not_found": "Verse text not found.",
        "chapter_word": "Chapter",
        "shloka_word": "Shloka",
        "tempo_waveform": "Tempo Consistency Waveform",
        "timing_title": "📊 1. Timing & Tempo Table",
        "segment": "Verse Segment",
        "target": "Target (Trainer)",
        "actual": "Actual",
        "offset": "Offset",
        "speed_status": "Speed Status",
        "total": "Total",
        "segment_1": "Segment 1",
        "segment_2": "Segment 2",
        "slow": "Slow (Rhythm Shift)",
        "close": "Close",
        "pause_long": "Pause Elongated",
        "matrix_title": "🗣️ 2. Syllable Matrix & Rhythm",
        "trainer_rhythm": "Trainer Rhythm",
        "your_chanting": "Your Chanting",
        "swar": "Swar",
        "murdha": "Murdha",
        "matra": "Matra",
        "rhythm": "Rhythm",
        "low_scale": "Low Scale",
        "unwanted_pause": "Unwanted Pause",
        "pitch_title": "🎵 3. Swar / Pitch Tuning Chart",
        "trainer_melody": "Trainer Target Melody",
        "your_scale": "Your Scale",
        "corrections_title": "📝 Exact Syllable Corrections",
        "target_syllable": "Target Syllable",
        "error_type": "Error Type",
        "guidance": "Corrective Guidance",
        "pitch_mismatch": "Pitch Mismatch",
        "duration_error": "Duration Error",
        "pitch_guidance": "The pitch on syllable '{char}' differs from the trainer reference. Match the trainer scale more closely.",
        "duration_guidance": "The syllable '{char}' should be brief, but it was prolonged. Keep it short and crisp.",
        "master_audio_error": "Trainer audio could not be downloaded. The report will still be displayed.",
        "demo_notice": "Important: the timing, pitch and error values in this version are demonstration values until a real audio-analysis engine is connected.",
    },
    "hi": {
        "language": "इंटरफ़ेस भाषा",
        "title": "🕉️ लर्न गीता - श्लोक उच्चारण एवं लय विश्लेषक",
        "subtitle": "द्विलिपि पाठ, समय, लय और स्वर की तुलना।",
        "chapter": "अध्याय चुनें",
        "from_shloka": "श्लोक क्रमांक से",
        "to_shloka": "श्लोक क्रमांक तक",
        "audio": "पाठ का ऑडियो अपलोड करें",
        "run": "🔍 पाठ का मूल्यांकन करें",
        "select_required": "कृपया अध्याय और श्लोक सीमा चुनें।",
        "audio_required": "कृपया ऑडियो फ़ाइल अपलोड करें।",
        "analyzing": "पाठ का विश्लेषण किया जा रहा है...",
        "verse_not_found": "श्लोक उपलब्ध नहीं है।",
        "chapter_word": "अध्याय",
        "shloka_word": "श्लोक",
        "tempo_waveform": "गति एवं लय की निरन्तरता",
        "timing_title": "📊 1. समय एवं गति सारणी",
        "segment": "श्लोक खण्ड",
        "target": "लक्ष्य (प्रशिक्षक)",
        "actual": "वास्तविक",
        "offset": "अन्तर",
        "speed_status": "गति स्थिति",
        "total": "कुल",
        "segment_1": "खण्ड 1",
        "segment_2": "खण्ड 2",
        "slow": "धीमा (लय परिवर्तन)",
        "close": "लगभग सही",
        "pause_long": "विराम अधिक लम्बा",
        "matrix_title": "🗣️ 2. अक्षर एवं लय विश्लेषण",
        "trainer_rhythm": "प्रशिक्षक की लय",
        "your_chanting": "आपका पाठ",
        "swar": "स्वर",
        "murdha": "मूर्धा",
        "matra": "मात्रा",
        "rhythm": "लय",
        "low_scale": "नीचा स्वर",
        "unwanted_pause": "अनावडे विराम",
        "pitch_title": "🎵 3. स्वर / पिच समायोजन",
        "trainer_melody": "प्रशिक्षक का लक्ष्य स्वर",
        "your_scale": "आपका स्वर",
        "corrections_title": "📝 अक्षरवार शुद्धि",
        "target_syllable": "लक्षित अक्षर",
        "error_type": "त्रुटि का प्रकार",
        "guidance": "सुधार मार्गदर्शन",
        "pitch_mismatch": "स्वर में अन्तर",
        "duration_error": "मात्रा की त्रुटि",
        "pitch_guidance": "'{char}' अक्षर का स्वर प्रशिक्षक के स्वर से अलग है। प्रशिक्षक के स्वर से अधिक निकटता रखें।",
        "duration_guidance": "'{char}' अक्षर छोटा होना चाहिए, परन्तु अधिक खींचा गया। इसे संक्षिप्त एवं स्पष्ट रखें।",
        "master_audio_error": "प्रशिक्षक का ऑडियो डाउनलोड नहीं हुआ।",
        "demo_notice": "महत्त्वपूर्ण: वास्तविक ऑडियो-विश्लेषण इंजन जुड़ने तक समय, स्वर एवं त्रुटि के आँकड़े प्रदर्शन हेतु हैं।",
    },
    "gu": {
        "language": "ઇન્ટરફેસ ભાષા", "title": "🕉️ લર્ન ગીતા - શ્લોક ઉચ્ચાર અને લય વિશ્લેષક",
        "subtitle": "દ્વિલિપિ પાઠ, સમય, લય અને સ્વરની સરખામણી।", "chapter": "અધ્યાય પસંદ કરો",
        "from_shloka": "શ્લોક નંબરથી", "to_shloka": "શ્લોક નંબર સુધી", "audio": "પાઠનું ઓડિયો અપલોડ કરો",
        "run": "🔍 પાઠનું મૂલ્યાંકન કરો", "select_required": "કૃપા કરીને અધ્યાય અને શ્લોકની મર્યાદા પસંદ કરો।",
        "audio_required": "કૃપા કરીને ઓડિયો ફાઇલ અપલોડ કરો।", "analyzing": "પાઠનું વિશ્લેષણ થઈ રહ્યું છે...",
        "verse_not_found": "શ્લોક મળ્યો નથી।", "chapter_word": "અધ્યાય", "shloka_word": "શ્લોક",
        "tempo_waveform": "ગતિ અને લયની સુસંગતતા", "timing_title": "📊 1. સમય અને ગતિનું કોષ્ટક",
        "segment": "શ્લોકનો ભાગ", "target": "લક્ષ્ય (પ્રશિક્ષક)", "actual": "વાસ્તવિક", "offset": "તફાવત",
        "speed_status": "ગતિની સ્થિતિ", "total": "કુલ", "segment_1": "ભાગ 1", "segment_2": "ભાગ 2",
        "slow": "ધીમું (લયમાં ફેરફાર)", "close": "Lબગ યોગ્ય", "pause_long": "વિરામ લાંબો",
        "matrix_title": "🗣️ 2. અક્ષર અને લય", "trainer_rhythm": "પ્રશિક્ષકની લય", "your_chanting": "તમારો પાઠ",
        "swar": "સ્વર", "murdha": "મૂર્ધા", "matra": "માત્રા", "rhythm": "લય", "low_scale": "નીચો સ્વર", "unwanted_pause": "અનાવશ્યક વિરામ",
        "pitch_title": "🎵 3. સ્વર / પિચ ચાર્ટ", "trainer_melody": "પ્રશિક્ષકનો લક્ષ્ય સ્વર", "your_scale": "તમારો સ્વર",
        "corrections_title": "📝 અક્ષરવાર સુધારા", "target_syllable": "લક્ષિત અક્ષર", "error_type": "ભૂલનો પ્રકાર", "guidance": "સુધારાનું માર્ગદર્શન",
        "pitch_mismatch": "સ્વરમાં તફાવત", "duration_error": "માત્રાની ભૂલ",
        "pitch_guidance": "'{char}' અક્ષરનો સ્વર પ્રશિક્ષકના સ્વરથી અલગ છે। પ્રશિક્ષકના સૂર સાથે મેળવો।",
        "duration_guidance": "'{char}' અક્ષર હ્રસ્વ હોવા છતાં લંબાયો છે। આ અક્ષરને ટૂંકો અને સ્પષ્ટ બોલો।",
        "master_audio_error": "પ્રશિક્ષકનું ઓડિયો ડાઉનલોડ થયું નથી। તેમ છતાં રિપોર્ટ બતાવવામાં આવશે।",
        "demo_notice": "મહત્ત્વપૂર્ણ: વાસ્તવિક ઓડિયો વિશ્લેષણ જોડાય ત્યાં સુધી આ આંકડા પ્રદર્શન માટે છે।",
    }
}

# Auto fallback load for other languages to prevent missing dictionary blocks
for code in ["as", "bn", "kn", "ml", "mni", "mr", "ne", "or", "sd", "ta", "te"]:
    if code not in I18N: I18N[code] = I18N["en"]

def get_texts(language_code: str) -> dict:
    return {**I18N["en"], **I18N.get(language_code, {})}

# ============================================================
# GRADIO STYLE APPLE HIGH-FIDELITY CSS
# ============================================================
st.markdown(
    """
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .heading-text { text-align: center; margin: 8px 0 22px 0; }
    .heading-text h1 { font-size: 28px; font-weight: 750; color: #1d1d1f; margin-bottom: 8px; }
    .heading-text p { color: #6e6e73; font-size: 14px; margin: 0; }
    .shloka-container {
        background: #f8f9fa; border-radius: 16px; padding: 20px;
        border-left: 6px solid #0071e3; margin: 20px 0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    .shloka-title { font-size: 14px; color: #0071e3; font-weight: 700; margin-bottom: 10px; }
    .shloka-devanagari { font-size: 22px; line-height: 2; text-align: center; color: #1d1d1f; margin-bottom: 14px; }
    .shloka-iast { font-size: 17px; line-height: 1.7; text-align: center; color: #434345; font-style: italic; border-top: 1px dashed #d2d2d7; padding-top: 12px; }
    .error-pitch { color: #ff3b30 !important; font-weight: 700; text-decoration: underline; }
    .error-syllable { color: #ff9500 !important; font-weight: 700; border-bottom: 2px dashed #ff9500; }
    .tempo-label { margin: 12px 0 6px 0; font-size: 12px; font-weight: 700; color: #6e6e73; }
    .analysis-table-wrapper { width: 100%; overflow-x: auto; margin-top: 10px; border-radius: 12px; }
    .analysis-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d2d2d7; min-width: 650px; }
    .analysis-table th { background: #f2f2f7; color: #1d1d1f; font-weight: 700; padding: 11px; font-size: 13px; text-align: left; border: 1px solid #d2d2d7; }
    .analysis-table td { padding: 11px; font-size: 13px; color: #434345; border: 1px solid #e5e5ea; vertical-align: top; }
    .section-sub-title { font-size: 15px; font-weight: 750; color: #0071e3; margin-top: 22px; margin-bottom: 8px; border-bottom: 1px solid #d2d2d7; padding-bottom: 6px; }
    .matrix-line { font-family: ui-monospace, monospace; font-size: 13px; background: #f1f3f4; padding: 9px; border-radius: 7px; margin: 5px 0; white-space: pre-wrap; }
    .badge-pitch { display: inline-block; background: #ffe5e5; color: #d70015; padding: 4px 7px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .badge-matra { display: inline-block; background: #fff2e5; color: #c75b00; padding: 4px 7px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .highlight-char { background: #ffd60a; color: #000000; padding: 2px 4px; border-radius: 4px; font-weight: 700; }
    .demo-notice { border: 1px solid #ffcc00; background: #fff9db; color: #5c4b00; border-radius: 10px; padding: 10px 12px; font-size: 12px; margin: 12px 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# ALGORITHMIC UTILITIES
# ============================================================
def clean_key(value) -> str:
    try:
        if pd.isna(value): return ""
        return str(int(str(value).strip().split(".")[0]))
    except (ValueError, TypeError):
        return str(value).strip()

@st.cache_data
def load_geeta_databases():
    hin_path, eng_path = "Geeta - Hin.csv", "Geeta - Eng.csv"
    hin_dict, eng_dict = {}, {}
    if os.path.exists(hin_path):
        df = pd.read_csv(hin_path)
        for _, row in df.iterrows():
            if len(row) >= 3 and not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                key = f"{clean_key(row.iloc[0])}_{clean_key(row.iloc[1])}"
                hin_dict[key] = str(row.iloc[2]).replace("\n", " ").strip()
    if os.path.exists(eng_path):
        df = pd.read_csv(eng_path)
        for _, row in df.iterrows():
            if len(row) >= 3 and not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                key = f"{clean_key(row.iloc[0])}_{clean_key(row.iloc[1])}"
                eng_dict[key] = str(row.iloc[2]).replace("\n", " ").strip()
    return hin_dict, eng_dict

def split_into_syllables(word: str) -> list[str]:
    pattern = r"([क-ह]्|[क-ह][ािीुूृॄेैोौंःँ]?|[अ-औ])"
    return [item for item in re.findall(pattern, word) if item.strip()]

def split_iast_into_syllables(word: str) -> list[str]:
    pattern = r"([bcdfghjklmnpqrstvwxyz]h?[āīūṛ१्eaiouṃṁḥ]?|[aeiouāīūṛ])"
    return re.findall(pattern, word, flags=re.IGNORECASE)

def replace_first(text: str, old: str, new: str) -> str:
    if not old: return text
    return text.replace(old, new, 1)

def render_html(html: str) -> None:
    st.html(textwrap.dedent(html).strip())

def make_demo_metrics(chapter: int, shloka: int) -> dict:
    seed = chapter * 1000 + shloka
    rng = np.random.default_rng(seed)
    target_total = round(float(rng.uniform(9.5, 12.0)), 1)
    actual_total = round(target_total + float(rng.uniform(0.5, 3.0)), 1)
    target_1 = round(target_total * float(rng.uniform(0.46, 0.52)), 1)
    target_2 = round(target_total - target_1, 1)
    actual_1 = round(target_1 + float(rng.uniform(0.1, 1.0)), 1)
    actual_2 = round(actual_total - actual_1, 1)
    return {
        "target_total": target_total, "actual_total": actual_total, "offset_total": round(actual_total - target_total, 1),
        "target_1": target_1, "actual_1": actual_1, "offset_1": round(actual_1 - target_1, 1),
        "target_2": target_2, "actual_2": actual_2, "offset_2": round(actual_2 - target_2, 1),
        "trainer_hz": int(rng.integers(145, 161)), "student_hz": int(rng.integers(128, 146)),
    }

# Gradio Style Dynamic Web Bar Generator
def make_waveform_svg(chapter: int, shloka: int) -> str:
    rng = np.random.default_rng(chapter * 1000 + shloka)
    bars = []
    for index in range(60):
        height = int(rng.integers(10, 42))
        y = 45 - height
        fill = "#ff3b30" if index in (18, 38) else "#34c759"
        bars.append(f"<rect x='{index * 12 + 10}' y='{y}' width='7' height='{height}' rx='3' fill='{fill}' />")
    return (
        "<svg width='100%' height='50' viewBox='0 0 740 50' preserveAspectRatio='none' style='background:#f1f3f4;border-radius:10px;padding:4px;'>"
        + "".join(bars) + "</svg>"
    )

def download_master_audio(chapter: int) -> tuple[str | None, str | None]:
    chapter_code = f"CH{chapter:02d}"
    url = f"https://huggingface.co/datasets/jatindved/geeta-master-audios/resolve/main/master_audios/{chapter_code}.mp3"
    temp_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()
        urllib.request.urlretrieve(url, temp_path)
        return temp_path, None
    except Exception as exc:
        if temp_path and os.path.exists(temp_path): os.remove(temp_path)
        return None, str(exc)

# Language Interface
selected_language_name = st.selectbox(
    "🌐 Interface Language", options=[name for name, _ in LANGUAGE_OPTIONS], index=0, key="interface_language"
)
language_code = LANGUAGE_NAME_TO_CODE[selected_language_name]
lex = get_texts(language_code)
page_direction = "rtl" if language_code in {"ur", "sd"} else "ltr"

render_html(f'<div dir="{page_direction}" class="heading-text"><h1>{escape(lex["title"])}</h1><p>{escape(lex["subtitle"])}</p></div>')

hin_db, eng_db = load_geeta_databases()

# Form Architecture
col1, col2, col3 = st.columns(3)
with col1:
    chapter_sel = st.selectbox(lex["chapter"], options=list(range(1, 19)), index=None, placeholder="-", format_func=lambda value: f"{lex['chapter_word']} {value}", key="chapter_sel")
with col2:
    start_shloka = st.selectbox(lex["from_shloka"], options=list(range(1, 79)), index=None, placeholder="-", key="start_shloka")
with col3:
    end_shloka = st.selectbox(lex["to_shloka"], options=list(range(1, 79)), index=None, placeholder="-", key="end_shloka")

student_audio = st.file_uploader(lex["audio"], type=["mp3", "wav", "m4a", "aac", "ogg", "flac"], key="student_audio")

render_html(f'<div dir="{page_direction}" class="demo-notice">{escape(lex["demo_notice"])}</div>')

# Execution Engine
if st.button(lex["run"], type="primary", use_container_width=True):
    if chapter_sel is None or start_shloka is None or end_shloka is None:
        st.error(lex["select_required"])
    elif student_audio is None:
        st.warning(lex["audio_required"])
    else:
        with st.spinner(lex["analyzing"]):
            chapter = int(chapter_sel)
            start = int(start_shloka)
            end = int(end_shloka)
            if start > end: start, end = end, start

            master_audio_path, master_audio_error = download_master_audio(chapter)
            if master_audio_error: st.info(lex["master_audio_error"])

            report_parts = []
            for shloka in range(start, end + 1):
                db_key = f"{chapter}_{shloka}"
                raw_dev = hin_db.get(db_key, lex["verse_not_found"])
                raw_iast = eng_db.get(db_key, lex["verse_not_found"])

                dev_words = raw_dev.split()
                iast_words = raw_iast.split()

                pitch_word_index = 2 if len(dev_words) > 2 else 0
                matra_word_index = 5 if len(dev_words) > 5 else min(1, len(dev_words) - 1)

                target_pitch_word = dev_words[pitch_word_index] if dev_words else "-"
                target_matra_word = dev_words[matra_word_index] if dev_words else "-"

                pitch_syllables = split_into_syllables(target_pitch_word)
                matra_syllables = split_into_syllables(target_matra_word)

                error_pitch_char = pitch_syllables[1] if len(pitch_syllables) > 1 else pitch_syllables[0] if pitch_syllables else target_pitch_word
                error_matra_char = matra_syllables[1] if len(matra_syllables) > 1 else matra_syllables[0] if matra_syllables else target_matra_word

                iast_pitch_index = 3 if len(iast_words) > 3 else 0
                iast_matra_index = 6 if len(iast_words) > 6 else min(1, len(iast_words) - 1)

                iast_pitch_word = iast_words[iast_pitch_index] if iast_words else "-"
                iast_matra_word = iast_words[iast_matra_index] if iast_words else "-"

                iast_pitch_syllables = split_iast_into_syllables(iast_pitch_word)
                iast_matra_syllables = split_iast_into_syllables(iast_matra_word)

                iast_pitch_char = iast_pitch_syllables[0] if iast_pitch_syllables else ""
                iast_matra_char = iast_matra_syllables[0] if iast_matra_syllables else ""

                highlighted_dev_words = []
                for index, word in enumerate(dev_words):
                    safe_word = escape(word)
                    if index == pitch_word_index:
                        safe_char = escape(error_pitch_char)
                        safe_word = replace_first(safe_word, safe_char, f"<span class='error-pitch'>{safe_char}</span>")
                    elif index == matra_word_index:
                        safe_char = escape(error_matra_char)
                        safe_word = replace_first(safe_word, safe_char, f"<span class='error-syllable'>{safe_char}</span>")
                    highlighted_dev_words.append(safe_word)

                highlighted_iast_words = []
                for index, word in enumerate(iast_words):
                    safe_word = escape(word)
                    if index == iast_pitch_index and iast_pitch_char:
                        safe_char = escape(iast_pitch_char)
                        safe_word = replace_first(safe_word, safe_char, f"<span class='error-pitch'>{safe_char}</span>")
                    elif index == iast_matra_index and iast_matra_char:
                        safe_char = escape(iast_matra_char)
                        safe_word = replace_first(safe_word, safe_char, f"<span class='error-syllable'>{safe_char}</span>")
                    highlighted_iast_words.append(safe_word)

                colored_dev = " ".join(highlighted_dev_words)
                colored_iast = " ".join(highlighted_iast_words)

                metrics = make_demo_metrics(chapter, shloka)
                waveform_svg = make_waveform_svg(chapter, shloka)

                pitch_guidance = lex["pitch_guidance"].format(char=error_pitch_char)
                duration_guidance = lex["duration_guidance"].format(char=error_matra_char)

                report_parts.append(
                    f"""
                    <div dir="{page_direction}" class="shloka-container">
                        <div class="shloka-title">🚩 {escape(lex["chapter_word"])} {chapter}, {escape(lex["shloka_word"])} {shloka}</div>
                        <div class="shloka-devanagari" dir="ltr">{colored_dev}</div>
                        <div class="shloka-iast" dir="ltr">{colored_iast}</div>
                        <div class="tempo-label">{escape(lex["tempo_waveform"])}:</div>
                        {waveform_svg}
                        <div class="section-sub-title">{escape(lex["timing_title"])}</div>
                        <div class="analysis-table-wrapper">
                            <table class="analysis-table">
                                <thead>
                                    <tr>
                                        <th>{escape(lex["segment"])}</th><th>{escape(lex["target"])}</th><th>{escape(lex["actual"])}</th><th>{escape(lex["offset"])}</th><th>{escape(lex["speed_status"])}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><b>{escape(lex["chapter_word"])} {chapter} - {escape(lex["shloka_word"])} {shloka} ({escape(lex["total"])})</b></td>
                                        <td>{metrics["target_total"]:.1f}s</td><td>{metrics["actual_total"]:.1f}s</td><td><span style="color:#ff3b30;font-weight:700;">+{metrics["offset_total"]:.1f}s</span></td><td>🐢 {escape(lex["slow"])}</td>
                                    </tr>
                                    <tr>
                                        <td>└─ {escape(lex["segment_1"])}</td><td>{metrics["target_1"]:.1f}s</td><td>{metrics["actual_1"]:.1f}s</td><td><span style="color:#ff9500;">+{metrics["offset_1"]:.1f}s</span></td><td>⏱️ {escape(lex["close"])}</td>
                                    </tr>
                                    <tr>
                                        <td>└─ {escape(lex["segment_2"])}</td><td>{metrics["target_2"]:.1f}s</td><td>{metrics["actual_2"]:.1f}s</td><td><span style="color:#ff3b30;font-weight:700;">+{metrics["offset_2"]:.1f}s</span></td><td>⏸️ {escape(lex["pause_long"])}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="section-sub-title">{escape(lex["matrix_title"])}</div>
                        <div class="matrix-line"><b>{escape(lex["trainer_rhythm"])}:</b> --({escape(lex["swar"])})--({escape(lex["murdha"])})--({escape(lex["matra"])})--[{escape(lex["rhythm"])}]--</div>
                        <div class="matrix-line"><b>{escape(lex["your_chanting"])}:</b> --({escape(lex["low_scale"])})--({escape(lex["murdha"])})--({escape(lex["matra"])})--[{escape(lex["unwanted_pause"])}]-- ⚠️ (+{metrics["offset_1"]:.1f}s)</div>
                        <div class="section-sub-title">{escape(lex["pitch_title"])}</div>
                        <div style="background:#ffffff;border:1px solid #e5e5ea;border-radius:12px;padding:10px;text-align:center;">
                            <p style="font-size:11px;color:#686868;text-align:left;margin:0 0 8px 0;">{escape(lex["trainer_melody"])}: {metrics["trainer_hz"]} Hz | {escape(lex["your_scale"])}: {metrics["student_hz"]} Hz</p>
                            <svg width="100%" height="70" viewBox="0 0 600 70" style="background:#f8f9fa;border-radius:8px;">
                                <line x1="50" y1="35" x2="550" y2="35" stroke="#0071e3" stroke-width="2" />
                                <path d="M 50 35 L 550 35" stroke="#34c759" stroke-width="4" fill="none" />
                                <path d="M 50 50 Q 150 58 250 40 T 450 54 T 550 48" stroke="#ff3b30" stroke-width="2.5" stroke-dasharray="5 3" fill="none" />
                            </svg>
                        </div>
                        <div class="section-sub-title">{escape(lex["corrections_title"])}</div>
                        <div class="analysis-table-wrapper">
                            <table class="analysis-table">
                                <thead>
                                    <tr><th>{escape(lex["target_syllable"])}</th><th>{escape(lex["error_type"])}</th><th>{escape(lex["guidance"])}</th></tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><b>{escape(target_pitch_word)}</b> (<span class="highlight-char">{escape(error_pitch_char)}</span>)</td>
                                        <td><span class="badge-pitch">{escape(lex["pitch_mismatch"])}</span></td><td>{escape(pitch_guidance)}</td>
                                    </tr>
                                    <tr>
                                        <td><b>{escape(target_matra_word)}</b> (<span class="highlight-char">{escape(error_matra_char)}</span>)</td>
                                        <td><span class="badge-matra">{escape(lex["duration_error"])}</span></td><td>{escape(duration_guidance)}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    """
                )

            render_html("\n".join(report_parts))
            
            # 🎯 FIX: st.remove ની જગ્યાએ સાચું ઓપરેટિંગ સિસ્ટમ ફંક્શન os.remove વાપર્યું
            if master_audio_path and os.path.exists(master_audio_path): 
                os.remove(master_audio_path)
