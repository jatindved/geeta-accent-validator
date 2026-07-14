import os
import re
import tempfile
import textwrap
import urllib.request
from html import escape

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go  # કસ્ટમ કલર અને કંડિશનલ ટોલરન્સ ગ્રાફ

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
    "gu": {
        "language": "ઇન્ટરફેસ ભાષા", "title": "🕉️ લર્ન ગીતા - શ્લોક ઉચ્ચાર અને લય વિશ્લેષક",
        "subtitle": "દ્વિલિપિ પાઠ, સમય, લય અને સ્વરની સરખામણી (કડક નિયમો સાથે)।", "chapter": "અધ્યાય પસંદ કરો",
        "from_shloka": "શ્લોક નંબરથી", "to_shloka": "શ્લોક નંબર સુધી", 
        "audio_record_lbl": "🎙️ તમારો પાઠ અહીં લાઈવ રેકોર્ડ કરો (મોબાઈલ માટે ઉત્તમ)", 
        "audio_upload_lbl": "📁 અથવા રેકોર્ડ કરેલી ઓડિયો ફાઇલ અપલોડ કરો", 
        "run": "🔍 પાઠનું કડક મૂલ્યાંકન શરૂ કરો", "select_required": "કૃપા કરીને અધ્યાય અને શ્લોકની મર્યાદા પસંદ કરો।",
        "audio_required": "કૃપા કરીને શ્લોક રેકોર્ડ કરો અથવા ઓડિયો ફાઇલ અપલોડ કરો।", "analyzing": "પાઠનું કડક વિશ્લેષણ થઈ રહ્યું છે...",
        "verse_not_found": "શ્લોક મળ્યો નથી।", "chapter_word": "અધ્યાય", "shloka_word": "શ્લોક",
        "tempo_waveform": "ગતિ અને લયની તુલના (લીલો = પ્રશિક્ષક | વાદળી = તમારો સાચો પાઠ | લาล = ટોલરન્સ બહાર ભૂલ)", "timing_title": "📊 ૧. સમય અને ગતિનું કોષ્ટક",
        "segment": "શ્લોકનો ભાગ", "target": "લક્ષ્ય (પ્રશિક્ષક)", "actual": "વાસ્તવિક", "offset": "તફાવત",
        "speed_status": "ગતિની સ્થિતિ", "total": "કુલ", "segment_1": "ભાગ ૧", "segment_2": "ભાગ ૨",
        "slow": "ધીમું (લયમાં ફેરફાર)", "close": "લગભગ યોગ્ય", "pause_long": "વિરામ લાંબો",
        "matrix_title": "🗣️ ૨. અક્ષર અને લય વિશ્લેષણ", "trainer_rhythm": "પ્રશિક્ષકની લય", "your_chanting": "તમારો પાઠ",
        "swar": "સ્વર", "murdha": "มૂર્ધા", "matra": "માત્રા", "rhythm": "લય", "low_scale": "નીચો સ્વર", "unwanted_pause": "અનાવશ્યક વિરામ",
        "pitch_title": "🎵 ૩. સ્વર / પિચ ટ્યુનિંગ ગ્રાફ (કડક સરખામણી)", "trainer_melody": "પ્રશિક્ષકનો લક્ષ્ય સ્વર", "your_scale": "તમારો સ્વર",
        "corrections_title": "📝 ૪. અક્ષરવાર સુધારા અને માર્ગદર્શન", "target_syllable": "લક્ષિત અક્ષર", "error_type": "ભૂલનો પ્રકાર", "guidance": "સુધારાનું માર્ગદર્શન",
        "pitch_mismatch": "સ્વરમાં તફાવત (સ્વર ભૂલ)", "duration_error": "માત્રાની ભૂલ (દીર્ઘ/હ્રસ્વ દોષ)",
        "pitch_guidance": "'{char}' અક્ષરનો સ્વર પ્રશિક્ષકના સત્તાવાર સ્વરથી અલગ છે। સૂર સહેજ પણ ઉપર-નીચે ચલાવી લેવામાં આવશે નહીં।",
        "duration_guidance": "'{char}' અક્ષર હ્રસ્વ હોવા છતાં ખેંચાયો છે। આ અક્ષર પર લય તૂટે છે, તેને ટૂંકો અને મર્યાદિત રાખો।",
        "master_audio_error": "પ્રશિક્ષકનું ઓડિયો ડાઉનલોડ થયું નથી।",
        "demo_notice": "મહત્ત્વપૂર્ણ: વાસ્તવિક ઓડિયો વિશ્લેષણ જોડાય ત્યાં સુધી આ આંકડા પ્રદર્શન અને કડક ટેસ્ટિંગ મોડ માટે છે।",
        "scoring_title": "🎯 શ્લોક શુદ્ધતા સ્કોરકાર્ડ (Strict Evaluation Mode)",
        "score_accent": "ઉચ્ચાર શુદ્ધિ (Accent)", "score_rhythm": "લય અને માત્રા (Rhythm)",
        "score_tempo": "ગતિ સુસંગતતા (Tempo)", "score_pitch": "સ્વર મેળ (Pitch)", "score_total": "કુલ ગુણ",
        "unsatisfactory": "અસંતોષકારક પ્રદર્શન - સુધારણા જરૂરી છે"
    },
    "en": {
        "language": "Interface Language", "title": "🕉️ Learn Geeta - Shloka Accent & Rhythm Validator",
        "subtitle": "Strict dual-script chanting, timing, rhythm and pitch validation.",
        "chapter": "Select Chapter", "from_shloka": "From Shloka No.", "to_shloka": "To Shloka No.",
        "audio_record_lbl": "🎙️ Record Chanting Live (Best for Mobile)",
        "audio_upload_lbl": "📁 Or Upload Audio File", "run": "🔍 Run Strict Chanting Evaluation",
        "select_required": "Please select the chapter and shloka range.", "audio_required": "Please record or upload an audio file.",
        "analyzing": "Running strict analysis on chanting performance...", "verse_not_found": "Verse text not found.",
        "chapter_word": "Chapter", "shloka_word": "Shloka", "tempo_waveform": "Tempo Comparison Chart (Green=Trainer, Blue=Correct, Red=Tolerance Out Error)",
        "timing_title": "📊 1. Timing & Tempo Table", "segment": "Verse Segment", "target": "Target (Trainer)",
        "actual": "Actual", "offset": "Offset", "speed_status": "Speed Status", "total": "Total",
        "segment_1": "Segment 1", "segment_2": "Segment 2", "slow": "Slow (Rhythm Shift)", "close": "Close",
        "pause_long": "Pause Elongated", "matrix_title": "🗣️ 2. Syllable Matrix & Rhythm", "trainer_rhythm": "Trainer Rhythm",
        "your_chanting": "Your Chanting", "swar": "Swar", "murdha": "Murdha", "matra": "Matra", "rhythm": "Rhythm",
        "low_scale": "Low Scale", "unwanted_pause": "Unwanted Pause", "pitch_title": "🎵 3. Swar / Pitch Tuning Chart",
        "trainer_melody": "Trainer Target Melody", "your_scale": "Your Scale", "corrections_title": "📝 Exact Syllable Corrections",
        "target_syllable": "Target Syllable", "error_type": "Error Type", "guidance": "Corrective Guidance",
        "pitch_mismatch": "Pitch Mismatch", "duration_error": "Duration Error",
        "pitch_guidance": "The pitch on syllable '{char}' deviates from trainer reference.",
        "duration_guidance": "The syllable '{char}' should be brief (Hrasva).",
        "master_audio_error": "Trainer audio download failed.", "demo_notice": "Important: Strict demo mode activated.",
        "scoring_title": "🎯 Chanting Strict Evaluation Scorecard", "score_accent": "Accent Accuracy", "score_rhythm": "Rhythm & Matra",
        "score_tempo": "Tempo Consistency", "score_pitch": "Pitch Matching", "score_total": "Total Score",
        "unsatisfactory": "Unsatisfactory Performance - Needs Correction"
    }
}

for code in ["hi", "as", "bn", "kn", "ml", "mni", "mr", "ne", "or", "sd", "ta", "te"]:
    if code not in I18N: I18N[code] = I18N["en"]

def get_texts(language_code: str) -> dict:
    return {**I18N["en"], **I18N.get(language_code, {})}

# ============================================================
# PREMIUM APP GRAPHICS CSS RULES
# ============================================================
st.markdown(
    """
<style>
    .heading-text { text-align: center; margin: 8px 0 22px 0; }
    .heading-text h1 { font-size: 26px; font-weight: 750; color: #1d1d1f; }
    .shloka-container {
        background: #f8f9fa; border-radius: 16px; padding: 22px;
        border-left: 6px solid #d70015; margin: 20px 0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    .shloka-title { font-size: 14px; color: #d70015; font-weight: 700; margin-bottom: 10px; }
    .shloka-devanagari { font-size: 24px; line-height: 2.2; text-align: center; color: #1d1d1f; margin-bottom: 14px; font-weight: 500; }
    .shloka-iast { font-size: 18px; line-height: 1.8; text-align: center; color: #434345; font-style: italic; border-top: 1px dashed #d2d2d7; padding-top: 12px; }
    
    .error-pitch { color: #ff3b30 !important; font-weight: 800; text-decoration: underline; background: #ffe5e5; padding: 0 4px; border-radius: 4px; }
    .error-syllable { color: #ff9500 !important; font-weight: 800; border-bottom: 3px dashed #ff9500; background: #fff2e5; padding: 0 4px; border-radius: 4px; }
    
    .tempo-label { margin: 15px 0 6px 0; font-size: 14px; font-weight: 700; color: #1d1d1f; }
    .analysis-table-wrapper { width: 100%; overflow-x: auto; margin-top: 10px; border-radius: 12px; }
    .analysis-table { width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d2d2d7; }
    .analysis-table th { background: #f2f2f7; color: #1d1d1f; font-weight: 700; padding: 11px; font-size: 13px; border: 1px solid #d2d2d7; text-align: left; }
    .analysis-table td { padding: 11px; font-size: 13px; color: #434345; border: 1px solid #e5e5ea; }
    .section-sub-title { font-size: 16px; font-weight: 750; color: #d70015; margin-top: 24px; margin-bottom: 8px; border-bottom: 1px solid #d2d2d7; padding-bottom: 6px; }
    .matrix-line { font-family: monospace; font-size: 13px; background: #f1f3f4; padding: 9px; border-radius: 7px; margin: 5px 0; }
    .badge-pitch { background: #ffe5e5; color: #d70015; padding: 3px 6px; border-radius: 5px; font-weight: 700; }
    .badge-matra { background: #fff2e5; color: #c75b00; padding: 3px 6px; border-radius: 5px; font-weight: 700; }
    .highlight-char { background: #ffd60a; padding: 2px 4px; border-radius: 4px; font-weight: 700; }
    .chart-explanation { background: #f4f6f8; border-left: 4px solid #0071e3; padding: 10px 14px; font-size: 13px; color: #1d1d1f; border-radius: 0 8px 8px 0; margin-top: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# DATABASES & UTILITIES
# ============================================================
def clean_key(value) -> str:
    try:
        if pd.isna(value): return ""
        return str(int(str(value).strip().split(".")[0]))
    except (ValueError, TypeError):
        return str(value).strip()

@st.cache_data
def load_geeta_databases():
    hin_dict, eng_dict = {}, {}
    if os.path.exists("Geeta - Hin.csv"):
        df = pd.read_csv("Geeta - Hin.csv")
        for _, row in df.iterrows():
            if len(row) >= 3 and not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                hin_dict[f"{clean_key(row.iloc[0])}_{clean_key(row.iloc[1])}"] = str(row.iloc[2]).replace("\n", " ").strip()
    if os.path.exists("Geeta - Eng.csv"):
        df = pd.read_csv("Geeta - Eng.csv")
        for _, row in df.iterrows():
            if len(row) >= 3 and not pd.isna(row.iloc[0]) and not pd.isna(row.iloc[1]):
                eng_dict[f"{clean_key(row.iloc[0])}_{clean_key(row.iloc[1])}"] = str(row.iloc[2]).replace("\n", " ").strip()
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

# ============================================================
# MAIN INTERFACE IMPLEMENTATION
# ============================================================
selected_language_name = st.selectbox("🌐 Interface Language", options=[name for name, _ in LANGUAGE_OPTIONS], index=0)
language_code = LANGUAGE_NAME_TO_CODE[selected_language_name]
lex = get_texts(language_code)

page_direction = "rtl" if language_code in {"ur", "sd"} else "ltr"
st.markdown(f'<div dir="{page_direction}" class="heading-text"><h1>{escape(lex["title"])}</h1><p>{escape(lex["subtitle"])}</p></div>', unsafe_allow_html=True)

hin_db, eng_db = load_geeta_databases()

col1, col2, col3 = st.columns(3)
with col1:
    chapter_sel = st.selectbox(lex["chapter"], options=list(range(1, 19)), index=None, placeholder="-", format_func=lambda v: f"{lex['chapter_word']} {v}")
with col2:
    start_shloka = st.selectbox(lex["from_shloka"], options=list(range(1, 79)), index=None, placeholder="-")
with col3:
    end_shloka = st.selectbox(lex["to_shloka"], options=list(range(1, 79)), index=None, placeholder="-")

# 🎯 🎯 FIX: ડ્યુઅલ ઓડિયો ઇનપુટ સિસ્ટમ (મોબાઈલ માટે લાઈવ માઈક અને અપલોડ બંને ઓપ્શન)
student_audio_live = st.audio_input(lex["audio_record_lbl"])
student_audio_file = st.file_uploader(lex["audio_upload_lbl"], type=["mp3", "wav", "m4a", "aac"])

# છેલ્લું કોઈ પણ એક ઇનપુટ સિલેક્ટ કરવા માટેનું લોજિક
student_audio = student_audio_live if student_audio_live is not None else student_audio_file

st.markdown(f'<div dir="{page_direction}" class="demo-notice">{escape(lex["demo_notice"])}</div>', unsafe_allow_html=True)

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

            for shloka in range(start, end + 1):
                db_key = f"{chapter}_{shloka}"
                raw_dev = hin_db.get(db_key, lex["verse_not_found"])
                raw_iast = eng_db.get(db_key, lex["verse_not_found"])

                rng = np.random.default_rng(chapter * 1000 + shloka)
                t_tot = round(float(rng.uniform(10.2, 11.8)), 1)
                a_tot = round(t_tot + float(rng.uniform(1.2, 2.8)), 1)
                t_1 = round(t_tot * 0.5, 1); a_1 = round(t_1 + float(rng.uniform(0.4, 0.9)), 1)
                t_2 = round(t_tot - t_1, 1); a_2 = round(a_tot - a_1, 1)

                m_accent = int(rng.integers(24, 31))
                m_rhythm = int(rng.integers(16, 22))
                m_tempo = int(rng.integers(10, 14))
                m_pitch = int(rng.integers(4, 7))
                m_total = m_accent + m_rhythm + m_tempo + m_pitch

                dev_words = raw_dev.split()
                iast_words = raw_iast.split()
                
                p_idx = min(2, len(dev_words) - 1) if dev_words else 0
                m_idx = min(5, len(dev_words) - 1) if dev_words else 0
                
                t_p_word = dev_words[p_idx] if dev_words else "-"
                t_m_word = dev_words[m_idx] if dev_words else "-"
                
                p_syl = split_into_syllables(t_p_word)
                m_syl = split_into_syllables(t_m_word)
                
                err_p_char = p_syl[1] if len(p_syl) > 1 else p_syl[0] if p_syl else t_p_word
                err_m_char = m_syl[1] if len(m_syl) > 1 else m_syl[0] if m_syl else t_m_word

                high_dev_words = []
                for idx, w in enumerate(dev_words):
                    sw = escape(w)
                    if idx == p_idx:
                        sc = escape(err_p_char)
                        sw = replace_first(sw, sc, f"<span class='error-pitch'>{sc}</span>")
                    elif idx == m_idx:
                        sc = escape(err_m_char)
                        sw = replace_first(sw, sc, f"<span class='error-syllable'>{sc}</span>")
                    high_dev_words.append(sw)

                colored_dev_html = " ".join(high_dev_words)

                st.markdown(f"""
                <div dir="{page_direction}" class="shloka-container">
                    <div class="shloka-title">🚩 {escape(lex["chapter_word"])} {chapter}, {escape(lex["shloka_word"])} {shloka}</div>
                    <div class="shloka-devanagari" dir="ltr">{colored_dev_html}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f'<div dir="{page_direction}"><h3>{escape(lex["scoring_title"])}</h3></div>', unsafe_allow_html=True)
                sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
                sc_col1.metric(lex["score_accent"], f"{m_accent}/40")
                sc_col2.metric(lex["score_rhythm"], f"{m_rhythm}/30")
                sc_col3.metric(lex["score_tempo"], f"{m_tempo}/20")
                sc_col4.metric(lex["score_pitch"], f"{m_pitch}/10")
                
                st.markdown(f"<div dir='{page_direction}' class='tempo-label'>{escape(lex['tempo_waveform'])}:</div>", unsafe_allow_html=True)
                
                # ડાયનેમિક ઓરિજિનલ શ્લોક શબ્દો ગ્રાફ એક્સિસ (X-AXIS) પર લોક
                num_words = len(dev_words)
                word_labels = [w.replace("।", "").replace("॥", "").strip() for w in dev_words]
                
                trainer_bars = rng.uniform(1.2, 1.8, size=num_words)
                student_bars = np.array(trainer_bars, dtype=float)
                
                error_index = min(2, num_words - 1)
                student_bars[error_index] += 0.9 
                
                ok_diff_index = min(4, num_words - 1) if num_words > 4 else 0
                if ok_diff_index != error_index:
                    student_bars[ok_diff_index] += 0.2

                student_colors = []
                for i in range(num_words):
                    diff = student_bars[i] - trainer_bars[i]
                    if diff > 0.5:
                        student_colors.append("#ff3b30") # 🔴 કડક લાલ (ભૂલ)
                    else:
                        student_colors.append("#0071e3") # 🔵 પ્રોફેશનલ બ્લુ (સાચો લય)

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=word_labels, y=trainer_bars, name='Trainer Standard',
                    marker_color='#34c759', hovertemplate='ટ્રેનર લય: %{y:.2f}s<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=word_labels, y=student_bars, name='Your Performance',
                    marker_color=student_colors, hovertemplate='તમારો લય: %{y:.2f}s<extra></extra>'
                ))

                fig.update_layout(
                    barmode='group', height=240, margin=dict(l=20, r=20, t=10, b=30),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(title="સમય (સેકન્ડ)", gridcolor="#e5e5ea"),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-25)
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                faulty_word = word_labels[error_index]
                st.markdown(f"""
                <div style='background: #fff3cd; padding: 10px 14px; border-radius: 8px; font-size: 13px; color: #856404; margin-bottom: 20px; border-left: 4px solid #ff3b30;'>
                    ⚠️ <b>Tolerance Error High Alert:</b> શ્લોકના ચોક્કસ શબ્દ <b>"{faulty_word}"</b> પર તમારો પાઠ નિયત લય મર્યાદા (૦.૫ સેકન્ડ ટોલરન્સ) કરતાં <b>+{student_bars[error_index]-trainer_bars[error_index]:.2f}s</b> વધારે લાંબો ગયો છે, તેથી તે સ્तંભ આપોઆપ <b>લાલ (Red)</b> રંગમાં બદલાઈ ગયો છે.
                </div>
                """, unsafe_allow_html=True)
                
                if language_code == "gu":
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>📈 ટોલરન્સ કલર ગ્રાફ માર્ગદર્શન:</b><br>
                        • <b>લીલો સ્તંભ:</b> પ્રશિક્ષક (Trainer) નો સત્તાવાર સમય છે.<br>
                        • <b>વાદળી સ્તંભ:</b> તમારો સાચો પાઠ છે.<br>
                        • <b>લાલ સ્તંભ:</b> શ્લોકના જે શબ્દ પર <b>ટોલરન્સ લિમિટ તૂટી છે</b>, તે શબ્દનો આખો ગ્રાફ સ્તંભ લાલ થઈ જશે.
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"<div dir='{page_direction}' class='section-sub-title'>{escape(lex['timing_title'])}</div>", unsafe_allow_html=True)
                st.markdown(f"""
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
                                <td>{t_tot:.1f}s</td><td>{a_tot:.1f}s</td><td><span style="color:#ff3b30;font-weight:700;">+{a_tot-t_tot:.1f}s</span></td><td>🐢 {escape(lex["slow"])}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div dir='{page_direction}' class='section-sub-title'>{escape(lex['corrections_title'])}</div>", unsafe_allow_html=True)
                p_guidance = lex["pitch_guidance"].format(char=err_p_char)
                d_guidance = lex["duration_guidance"].format(char=err_m_char)
                st.markdown(f"""
                <div class="analysis-table-wrapper">
                    <table class="analysis-table">
                        <thead>
                            <tr><th>{escape(lex["target_syllable"])}</th><th>{escape(lex["error_type"])}</th><th>{escape(lex["guidance"])}</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><b>{escape(t_p_word)}</b> (<span class="highlight-char">{escape(err_p_char)}</span>)</td>
                                <td><span class="badge-pitch">{escape(lex["pitch_mismatch"])}</span></td><td>{escape(p_guidance)}</td>
                            </tr>
                            <tr>
                                <td><b>{escape(t_m_word)}</b> (<span class="highlight-char">{escape(err_m_char)}</span>)</td>
                                <td><span class="badge-matra">{escape(lex["duration_error"])}</span></td><td>{escape(d_guidance)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <hr style="margin:30px 0; border:1px solid #e5e5ea;"/>
                """, unsafe_allow_html=True)
