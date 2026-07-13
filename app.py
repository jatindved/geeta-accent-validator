import streamlit as st
import numpy as np
import os
import pandas as pd
import re
import urllib.request
import tempfile

# Page Configuration for iOS/Android Mobile Layout
st.set_page_config(
    page_title="Learn Geeta - Shloka Accent & Rhythm Validator",
    page_icon="🕉️",
    layout="centered"
)

# Custom Premium Styling & Typography
st.markdown("""
<style>
    .main { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .heading-text { text-align: center; margin-bottom: 25px; }
    .shloka-container {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 20px;
        border-left: 6px solid #0071e3;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    .shloka-title { font-size: 14px; color: #0071e3; font-weight: bold; margin-bottom: 8px; }
    .shloka-devanagari { font-size: 22px; line-height: 2; text-align: center; color: #1d1d1f; margin-bottom: 14px; }
    .shloka-iast { font-size: 17px; line-height: 1.6; text-align: center; color: #434345; font-style: italic; border-top: 1px dashed #e5e5ea; padding-top: 12px; }
    .error-pitch { color: #ff3b30 !important; font-weight: bold; text-decoration: underline; }
    .error-syllable { color: #ff9500 !important; font-weight: bold; border-bottom: 2px dashed #ff9500; }
    
    .analysis-table-wrapper { width: 100%; overflow-x: auto; margin-top: 15px; }
    .analysis-table { width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e5ea; min-width: 500px; }
    .analysis-table th { background: #f2f2f7; color: #1d1d1f; font-weight: 600; padding: 10px; font-size: 13px; text-align: left; }
    .analysis-table td { padding: 10px; font-size: 13px; color: #434345; border-bottom: 1px solid #e5e5ea; }
    
    .badge-pitch { background: #ffe5e5; color: #ff3b30; padding: 4px 6px; border-radius: 6px; font-weight: bold; font-size: 11px; }
    .badge-matra { background: #fff2e5; color: #ff9500; padding: 4px 6px; border-radius: 6px; font-weight: bold; font-size: 11px; }
    .highlight-char { background: #ffcc00; color: #000; padding: 2px 4px; border-radius: 4px; font-weight: bold; }
    .section-sub-title { font-size: 14px; font-weight: 700; color: #0071e3; margin-top: 20px; margin-bottom: 8px; border-bottom: 1px solid #e5e5ea; padding-bottom: 4px; }
    .matrix-line { font-family: monospace; font-size: 13px; background: #f1f3f4; padding: 8px; border-radius: 6px; margin: 4px 0; white-space: pre-wrap; }
    
    @media (max-width: 600px) {
        .shloka-devanagari { font-size: 18px !important; }
        .shloka-iast { font-size: 14px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ૧૩ સત્તાવાર ભારતીય ભાષાઓનો સચોટ ટ્રાન્સલેશન ડેટાબેઝ
ui_lexicon = {
    "English": {
        "title": "🕉️ Learn Geeta - Shloka Accent & Rhythm Validator", "subtitle": "Dynamic Dual-Script Realtime Audio Alignment Engine.",
        "lbl_ch": "Select Chapter", "lbl_from": "From Shloka No.", "lbl_to": "To Shloka No.", "lbl_lang": "Interface Language",
        "lbl_audio": "Upload Chanting Performance Audio", "btn_run": "🔍 Run Deep Audio & Scriptural Evaluation",
        "rep_title": "📊 Micro-Level Syllable Alignment & Analytics", "rep_legend": "🎨 **Diagnostic Guide:** Red = Pitch/Swar Error | Orange = Syllable/Matra Mismatch",
        "rep_tempo": "Tempo Consistency Waveform:", "th_word": "Target Syllable", "th_type": "Error Type", "th_action": "Exact Corrective Action Guidance",
        "t_sec_lbl": "📊 1. Timing & Tempo Table", "s_sec_lbl": "🗣️ 2. Syllable Matrix & Pitch Graph", "p_sec_lbl": "🎵 3. Swar / Pitch Tuning Chart",
        "err_p_msg": "The pitch frequency on syllable '{char}' deviates from standard. Lower your pitch to match certified accent.",
        "err_m_msg": "Syllable '{char}' is short (Hrasva) but was elongated too long (Dirgha error). Keep it brief and crisp."
    },
    "Hindi": {
        "title": "🕉️ लर्न गीता - श्लोक उच्चारण एवं लय परीक्षक", "subtitle": "रीयल-टाइम ऑडियो संरेखण और लिपि मिलान इंजन।",
        "lbl_ch": "अध्याय चुनें", "lbl_from": "किस श्लोक से?", "lbl_to": "किस श्लोक तक?", "lbl_lang": "इंटरफ़ेस भाषा (Language)",
        "lbl_audio": "अपना रिकॉर्ड किया गया श्लोक ऑडियो यहाँ अपलोड करें", "btn_run": "🔍 ऑडियो और श्लोक मूल्यांकन शुरू करें",
        "rep_title": "📊 सूक्ष्म-स्तरीय अक्षर संरेखण और विश्लेषण रिपोर्ट", "rep_legend": "🎨 **विश्लेषण गाइड:** लाल = पिच/स्वर त्रुटि | नारंगी = मात्रा दोष",
        "rep_tempo": "लय और गति का ग्राफिकल संकेत:", "th_word": "विशिष्ट अक्षर / मात्रा", "th_type": "त्रुटि का प्रकार", "th_action": "सुधारात्मक मार्गदर्शन (Action)",
        "t_sec_lbl": "📊 1. समय और लय तालिका (Timing & Tempo Table)", "s_sec_lbl": "🗣️ 2. अक्षर-वार मात्रा और पिच रिपोर्ट", "p_sec_lbl": "🎵 3. पिच और स्वर चार्ट (Swar / Pitch Tuning Chart)",
        "err_p_msg": "इस विशिष्ट अक्षर '{char}' पर आपका स्वर ऊँचा गया है। उच्चारण करते समय स्वर थोड़ा कम करें।",
        "err_m_msg": "यहाँ '{char}' अक्षर ह्रस्व होने के बावजूद लंबा खिंचा है। इसे लंबा करने के बजाय छोटा और सीमित बोलें।"
    },
    "Gujarati": {
        "title": "🕉️ લર્ન ગીતા - શ્લોક ઉચ્ચારણ અને લય ચકાસક", "subtitle": "રીઅલ-ટાઇમ ઓડિયો અલાઈનમેન્ટ
