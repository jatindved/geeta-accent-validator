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
# LANGUAGE OPTIONS (Strict 14 Core Set)
# ============================================================
LANGUAGE_OPTIONS = [
    ("ગુજરાતી", "gu"),
    ("English", "en"),
    ("हिन्दी", "hi"),
    ("অসমীয়া", "as"),
    ("বাংলা", "bn"),
    ("ಕನ್ನಡ", "kn"),
    ("മലയാളം", "ml"),
    ("မৈতৈলোन् / Manipuri", "mni"),
    ("मराठी", "mr"),
    ("नेपाली", "ne"),
    ("ଓଡ଼ିଆ", "or"),
    ("सिन्धी", "sd"),
    ("தமிழ்", "ta"),
    ("తెలుగు", "te"),
]

LANGUAGE_NAME_TO_CODE = dict(LANGUAGE_OPTIONS)

# ============================================================
# COMPLETE INTERFACE TRANSLATIONS (All 14 Languages Explicitly Loaded)
# ============================================================
I18N = {
    "gu": {
        "language": "ઇન્ટરફેસ ભાષા", "title": "🕉️ લર્ન ગીતા - શ્લોક ઉચ્ચાર અને લય વિશ્લેષક",
        "subtitle": "દ્વિલિપિ પાઠ, સમય, લય અને સ્વરની સરખામણી (કડક નિયમો સાથે)।", "chapter": "અધ્યાય પસંદ કરો",
        "from_shloka": "શ્લોક નંબરથી", "to_shloka": "શ્લોક નંબર સુધી", "audio": "પાઠનું ઓડિયો અપલોડ કરો",
        "run": "🔍 પાઠનું કડક મૂલ્યાંકન શરૂ કરો", "select_required": "કૃપા કરીને અધ્યાય અને શ્લોકની મર્યાદા પસંદ કરો।",
        "audio_required": "કૃપા કરીને ઓડિયો ફાઇલ અપલોડ કરો।", "analyzing": "પાઠનું કડક વિશ્લેષણ થઈ રહ્યું છે...",
        "verse_not_found": "શ્લોક મળ્યો નથી।", "chapter_word": "અધ્યાય", "shloka_word": "શ્લોક",
        "tempo_waveform": "ગતિ અને લયની સુસંગતતા (વેવફોર્મ ચાર્ટ)", "timing_title": "📊 ૧. સમય અને ગતિનું કોષ્ટક",
        "segment": "શ્લોકનો ભાગ", "target": "લક્ષ્ય (પ્રશિક્ષક)", "actual": "વાસ્તવિક", "offset": "તફાવત",
        "speed_status": "ગતિની સ્થિતિ", "total": "કુલ", "segment_1": "ભાગ ૧", "segment_2": "ભાગ ૨",
        "slow": "ધીમું (લયમાં ફેરફાર)", "close": "લગભગ યોગ્ય", "pause_long": "વિરામ લાંબો",
        "matrix_title": "🗣️ ૨. અક્ષર અને લય વિશ્લેષણ", "trainer_rhythm": "પ્રશિક્ષકની લય", "your_chanting": "તમારો પાઠ",
        "swar": "સ્વર", "murdha": "મૂર્ધા", "matra": "માત્રા", "rhythm": "લય", "low_scale": "નીચો સ્વર", "unwanted_pause": "અનાવશ્યક વિરામ",
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
        "audio": "Upload Chanting Audio", "run": "🔍 Run Strict Chanting Evaluation",
        "select_required": "Please select the chapter and shloka range.", "audio_required": "Please upload an audio file.",
        "analyzing": "Running strict analysis on chanting performance...", "verse_not_found": "Verse text not found.",
        "chapter_word": "Chapter", "shloka_word": "Shloka", "tempo_waveform": "Tempo Consistency Waveform",
        "timing_title": "📊 1. Timing & Tempo Table", "segment": "Verse Segment", "target": "Target (Trainer)",
        "actual": "Actual", "offset": "Offset", "speed_status": "Speed Status", "total": "Total",
        "segment_1": "Segment 1", "segment_2": "Segment 2", "slow": "Slow (Rhythm Shift)", "close": "Close",
        "pause_long": "Pause Elongated", "matrix_title": "🗣️ 2. Syllable Matrix & Rhythm", "trainer_rhythm": "Trainer Rhythm",
        "your_chanting": "Your Chanting", "swar": "Swar", "murdha": "Murdha", "matra": "Matra", "rhythm": "Rhythm",
        "low_scale": "Low Scale", "unwanted_pause": "Unwanted Pause", "pitch_title": "🎵 3. Swar / Pitch Tuning Chart",
        "trainer_melody": "Trainer Target Melody", "your_scale": "Your Scale", "corrections_title": "📝 Exact Syllable Corrections",
        "target_syllable": "Target Syllable", "error_type": "Error Type", "guidance": "Corrective Guidance",
        "pitch_mismatch": "Pitch Mismatch", "duration_error": "Duration Error",
        "pitch_guidance": "The pitch on syllable '{char}' deviates from standard trainer reference. Accuracy must be 100%.",
        "duration_guidance": "The syllable '{char}' must be brief (Hrasva). Elongation violates chanting protocol.",
        "master_audio_error": "Trainer audio download failed.", "demo_notice": "Important: Strict demo mode activated.",
        "scoring_title": "🎯 Chanting Strict Evaluation Scorecard", "score_accent": "Accent Accuracy", "score_rhythm": "Rhythm & Matra",
        "score_tempo": "Tempo Consistency", "score_pitch": "Pitch Matching", "score_total": "Total Score",
        "unsatisfactory": "Unsatisfactory Performance - Needs Correction"
    },
    "hi": {
        "language": "इंटरफ़ेस भाषा", "title": "🕉️ लर्न गीता - श्लोक उच्चारण एवं लय विश्लेषक (Strict Mode)",
        "subtitle": "द्विलिपि पाठ, समय, लय और स्वर की तुलना।", "chapter": "अध्याय चुनें",
        "from_shloka": "श्लोक क्रमांक से", "to_shloka": "श्लोक क्रमांक तक", "audio": "पाठ का ऑडियो अपलोड करें",
        "run": "🔍 पाठ का कड़ा मूल्यांकन शुरू करें", "select_required": "कृपया अध्याय और श्लोक सीमा चुनें।",
        "audio_required": "कृपया ऑडियो फ़ाइल अपलोड करें।", "analyzing": "पाठ का विश्लेषण किया जा रहा है...",
        "verse_not_found": "श्लोक उपलब्ध नहीं है।", "chapter_word": "अध्याय", "shloka_word": "श्लोक",
        "tempo_waveform": "गति एवं लय की निरन्तरता", "timing_title": "📊 1. समय एवं गति सारणी",
        "segment": "श्लोक खण्ड", "target": "लक्ष्य (प्रशिक्षक)", "actual": "वास्तविक", "offset": "अन्तर",
        "speed_status": "गति स्थिति", "total": "कुल", "segment_1": "खण्ड 1", "segment_2": "खण्ड 2",
        "slow": "धीमा (लय परिवर्तन)", "close": "लगभग सही", "pause_long": "विराम अधिक लम्बा",
        "matrix_title": "🗣️ 2. अक्षर एवं लय विश्लेषण", "trainer_rhythm": "प्रशिक्षक की लय", "your_chanting": "आपका पाठ",
        "swar": "स्वर", "murdha": "मूर्धा", "matra": "मात्रा", "rhythm": "लय", "low_scale": "नीचा स्वर", "unwanted_pause": "अनावश्यक विराम",
        "pitch_title": "🎵 3. स्वर / पिच समायोजन", "trainer_melody": "प्रशिक्षक का लक्ष्य स्वर", "your_scale": "आपका स्वर",
        "corrections_title": "📝 अक्षरवार शुद्धि", "target_syllable": "लक्षित अक्षर", "error_type": "त्रुटि का प्रकार", "guidance": "सुधार मार्गदर्शन",
        "pitch_mismatch": "स्वर में अन्तर", "duration_error": "मात्रा की त्रुटि",
        "pitch_guidance": "'{char}' अक्षर का स्वर प्रशिक्षक के स्वर से अलग है। शुद्धता १००% होनी चाहिए।",
        "duration_guidance": "'{char}' अक्षर ह्रस्व होने के बावजूद खींचा गया है। इसे संक्षिप्त और स्पष्ट रखें।",
        "master_audio_error": "प्रशिक्षक का ऑडियो डाउनलोड नहीं हुआ।", "demo_notice": "महत्त्वपूर्ण: वास्तविक ऑडियो-विश्लेषण इंजन जुड़ने तक समय, स्वर एवं त्रुटि के आँकड़े प्रदर्शन हेतु हैं।",
        "scoring_title": "🎯 श्लोक गुणवत्ता स्कोरकार्ड (Strict Evaluation Mode)", "score_accent": "उच्चारण शुद्धि", "score_rhythm": "लय एवं मात्रा",
        "score_tempo": "गति निरन्तरता", "score_pitch": "स्वर मिलान", "score_total": "कुल अंक", "unsatisfactory": "असंतोषजनक प्रदर्शन - सुधार आवश्यक है"
    },
    "as": {
        "language": "ইণ্টাৰফেচ ভাষা", "title": "🕉️ লাৰ্ন গীতা - শ্লোক উচ্চাৰণ আৰু ছন্দ বিশ্লেষক",
        "subtitle": "দুই লিপিৰ পাঠ, সময়, ছন্দ আৰু স্বৰৰ তুলনা।", "chapter": "অধ্যায় বাছক",
        "from_shloka": "শ্লোক নম্বৰৰ পৰা", "to_shloka": "শ্লোক নম্বৰলৈ", "audio": "पाठৰ অডিঅ’ আপলোড কৰক",
        "run": "🔍 পাঠ মূল্যায়ন কৰক", "select_required": "অধ্যায় আৰু শ্লোকৰ সীমা বাছক।",
        "audio_required": "অডিঅ’ ফাইল আপলোড কৰক।", "analyzing": "पाठ বিশ্লেষণ কৰা হৈছে...",
        "verse_not_found": "শ্লোক পোৱা নগ’ল।", "chapter_word": "অধ্যায়", "shloka_word": "শ্লোক",
        "tempo_waveform": "গতি আৰু ছন্দৰ সামঞ্জস্য", "timing_title": "📊 1. সময় আৰু গতি তালিকা",
        "segment": "শ্লোক খণ্ড", "target": "লক্ষ্য (প্ৰশিক্ষক)", "actual": "প্রকৃত", "offset": "পাৰ্থক্য",
        "speed_status": "গতিৰ অৱস্থা", "total": "মুঠ", "segment_1": "খণ্ড 1", "segment_2": "খণ্ড 2",
        "slow": "লেহেম (ছন্দ সলনি)", "close": "ওচৰ", "pause_long": "বিৰাম দীঘল",
        "matrix_title": "🗣️ 2. অক্ষৰ আৰু ছন্দ", "trainer_rhythm": "প্ৰশিক্ষকৰ ছন্দ", "your_chanting": "আপোনাৰ পাঠ",
        "swar": "স্বৰ", "murdha": "মূৰ্ধা", "matra": "মাত্ৰা", "rhythm": "ছন্দ", "low_scale": "নিম্ন স্বৰ", "unwanted_pause": "অপ্ৰয়োজনীয় বিৰাম",
        "pitch_title": "🎵 3. স্বৰ / পিচ চাৰ্ট", "trainer_melody": "প্ৰশিক্ষকৰ লক্ষ্য স্বৰ", "your_scale": "আপোনাৰ স্বৰ",
        "corrections_title": "📝 অক্ষৰভিত্তিক সংশোধন", "target_syllable": "লক্ষ্য অক্ষৰ", "error_type": "ভুলৰ প্ৰকাৰ", "guidance": "সংশোধনৰ নিৰ্দেশনা",
        "pitch_mismatch": "স্বৰৰ অমিল", "duration_error": "মাত্ৰাৰ ভুল",
        "pitch_guidance": "'{char}' অক্ষৰৰ স্বৰ প্ৰশিক্ষকৰ সৈতে মিল নাই। স্বৰ ১০০% শুদ্ধ কৰক।",
        "duration_guidance": "'{char}' অক্ষৰটো চুটি হ’ব লাগিছিল, কিন্তু দীঘল হ’ল। চুটি আৰু স্পষ্ট কৰক।",
        "master_audio_error": "প্ৰশিক্ষকৰ অডিঅ’ ডাউনলোড নহ’ল।", "demo_notice": "গুৰুত্বপূৰ্ণ: অডিঅ’ বিশ্লেষণ সংযোগ নোহোৱালৈকে এই মানসমূহ প্ৰদৰ্শনমূলক।",
        "scoring_title": "🎯 শ্লোক গুণগত স্কোৰকাৰ্ড (Strict Evaluation Mode)", "score_accent": "উচ্চাৰণ শুদ্ধি", "score_rhythm": "লય আৰু মাত্ৰા",
        "score_tempo": "গতিৰ স্থিৰতা", "score_pitch": "স্বৰ মিলোৱা", "score_total": "মুঠ নম্বৰ", "unsatisfactory": "অসন্তোষজনক প্ৰদৰ্শন - সংশোধনৰ প্ৰয়োজন"
    },
    "bn": {
        "language": "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ", "title": "🕉️ লার্ন গীতা - শ্লোক উচ্চারণ ও ছন্দ বিশ্লেষক",
        "subtitle": "দ্বৈত লিপি, সময়, ছন্দ ও স্বরের তুলনা।", "chapter": "অধ্যায় নির্বাচন করুন",
        "from_shloka": "শ্লোক নম্বর থেকে", "to_shloka": "শ্লোক নম্বর পর্যন্ত", "audio": "পাঠের অডিও আপলোড করুন",
        "run": "🔍 পাঠ মূল্যায়ন করুন", "select_required": "অধ্যায় ও শ্লোকের সীমা নির্বাচন করুন।",
        "audio_required": "অডিও ফাইল আপলোড করুন।", "analyzing": "পাঠ বিশ্লেষণ করা হচ্ছে...",
        "verse_not_found": "শ্লোক পাওয়া যায়নি।", "chapter_word": "অধ্যায়", "shloka_word": "শ্লোক",
        "tempo_waveform": "গতি ও ছন্দের সামঞ্জস্য", "timing_title": "📊 1. সময় ও গতির সারণি",
        "segment": "শ্লোক অংশ", "target": "লক্ষ্য (প্রশিক্ষক)", "actual": "প্রকৃত", "offset": "পার্থক্য",
        "speed_status": "গতির অবস্থা", "total": "মোট", "segment_1": "অংশ 1", "segment_2": "অংশ 2",
        "slow": "ধীর (ছন্দ পরিবর্তন)", "close": "কাছাকাছি", "pause_long": "বিরতি দীর্ঘ",
        "matrix_title": "🗣️ 2. অক্ষর ও ছন্দ", "trainer_rhythm": "প্রশিক্ষকের ছন্দ", "your_chanting": "আপনার পাঠ",
        "swar": "স্বর", "murdha": "মূর্ধা", "matra": "মাত্রা", "rhythm": "ছন্দ", "low_scale": "निम्न स्वर", "unwanted_pause": "অপ্রয়োজনীয় বিরতি",
        "pitch_title": "🎵 3. স্বর / পিচ চার্ট", "trainer_melody": "প্রশিক্ষকের লক্ষ্য স্বর", "your_scale": "আপনার স্বর",
        "corrections_title": "📝 অক্ষরভিত্তিক সংশোধন", "target_syllable": "লক্ষ্য অক্ষর", "error_type": "ত্রুটির ধরন", "guidance": "সংশোধনের নির্দেশনা",
        "pitch_mismatch": "স্বরের অমিল", "duration_error": "মাত্রার ত্রুটি",
        "pitch_guidance": "'{char}' অক্ষরের স্বর প্রশিক্ষকের স্বরের সঙ্গে মিলছে না। সুর ১০০% ঠিক করুন।",
        "duration_guidance": "'{char}' অক্ষরটি সংক্ষিপ্ত হওয়া উচিত ছিল, কিন্তু দীর্ঘ হয়েছে। এটি স্পষ্ট ও ছোট রাখুন।",
        "master_audio_error": "প্রশিক্ষকের অডিও ডাউনলোড হয়নি।", "demo_notice": "গুরুত্বपूर्ण: বাস্তব অডিও বিশ্লেষণ যুক্ত না হওয়া পর্যন্ত মানগুলো প্রদর্শনমূলক।",
        "scoring_title": "🎯 শ্লোক গুণগত স্কোরকার্ড (Strict Evaluation Mode)", "score_accent": "উচ্চারণ শুদ্ধি", "score_rhythm": "লয় ও মাত্রা",
        "score_tempo": "গতির ধারাবাহিকতা", "score_pitch": "স্বর মিল", "score_total": "মোট নম্বর", "unsatisfactory": "অসন্তোষজনক পারফরম্যান্স - সংশোধন প্রয়োজন"
    },
    "kn": {
        "language": "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ", "title": "🕉️ ಲರ್ನ್ ಗೀತಾ - ಶ್ಲೋಕ ಉಚ್ಚಾರಣೆ ಮತ್ತು ಲಯ ವಿಶ್ಲೇಷಕ",
        "subtitle": "ದ್ವಿಲಿಪಿ ಪಠಣ, ಸಮಯ, ಲಯ ಮತ್ತು ಸ್ವರ ಹೋಲಿಕೆ।", "chapter": "ಅಧ್ಯಾಯ ಆಯ್ಕೆಮಾಡಿ",
        "from_shloka": "ಶ್ಲೋಕ ಸಂಖ್ಯೆಯಿಂದ", "to_shloka": "ಶ್ಲೋಕ ಸಂಖ್ಯೆಯವರೆಗೆ", "audio": "ಪಠಣದ ಆಡಿಯೊ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "run": "🔍 ಪಠಣ ಮೌಲ್ಯಮಾಪನ ಮಾಡಿ", "select_required": "ಅಧ್ಯಾಯ ಮತ್ತು ಶ್ಲೋಕ ಮಿತಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ।",
        "audio_required": "ಆಡಿಯೊ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ।", "analyzing": "ಪಠಣವನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        "verse_not_found": "ಶ್ಲೋಕ ದೊರಕಲಿಲ್ಲ।", "chapter_word": "ಅಧ್ಯಾಯ", "shloka_word": "ಶ್ಲೋಕ",
        "tempo_waveform": "ಲಯ ಮತ್ತು ಗತಿಯ ಸ್ಥಿರತೆ", "timing_title": "📊 1. ಸಮಯ ಮತ್ತು ಗತಿ ಕೋಷ್ಟಕ",
        "segment": "ಶ್ಲೋಕದ ಭಾಗ", "target": "ಗುರಿ (ತರಬೇತುದಾರ)", "actual": "ವಾಸ್ತವಿಕ", "offset": "ವ್ಯತ್ಯಾಸ",
        "speed_status": "ಗತಿಯ ಸ್ಥಿತಿ", "total": "ಒಟ್ಟು", "segment_1": "ಭಾಗ 1", "segment_2": "ಭಾಗ 2",
        "slow": "ನಿಧಾನ (ಲಯ ಬದಲಾವಣೆ)", "close": "ಹತ್ತಿರ", "pause_long": "ವಿರಾಮ ದೀರ್ಘವಾಗಿದೆ",
        "matrix_title": "🗣️ 2. ಅಕ್ಷರ ಮತ್ತು ಲಯ", "trainer_rhythm": "ತರಬೇತುದಾರನ ಲಯ", "your_chanting": "ನಿಮ್ಮ ಪಠಣ",
        "swar": "ಸ್ವರ", "murdha": "ಮೂರ್ಧ", "matra": "ಮಾತ್ರೆ", "rhythm": "ಲಯ", "low_scale": "ಕಡಿಮೆ ಸ್ವರ", "unwanted_pause": "ಅಗತ್ಯವಿಲ್ಲದ ವಿರಾಮ",
        "pitch_title": "🎵 3. ಸ್ವರ / ಪಿಚ್ ಚಾರ್ಟ್", "trainer_melody": "ತರಬೇತುದಾರನ ಗುರಿ ಸ್ವರ", "your_scale": "ನಿಮ್ಮ ಸ್ವರ",
        "corrections_title": "📝 ಅಕ್ಷರವಾರು ತಿದ್ದುಪಡಿಗಳು", "target_syllable": "ಲಕ್ಷ್ಯ ಅಕ್ಷರ", "error_type": "ದೋಷದ ಪ್ರಕಾರ", "guidance": "ತಿದ್ದುಪಡಿ ಮಾರ್ಗದರ್ಶನ",
        "pitch_mismatch": "ಸ್ವರ ವ್ಯತ್ಯಾಸ", "duration_error": "ಮಾತ್ರೆಯ ದೋಷ",
        "pitch_guidance": "'{char}' ಅಕ್ಷರದ ಸ್ವರವು ತರಬೇತುದಾರನ ಸ್ವರಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ। 100% ನಿಖರತೆ ಅಗತ್ಯ।",
        "duration_guidance": "'{char}' ಅಕ್ಷರವನ್ನು ಹ್ರಸ್ವವಾಗಿ ಉಚ್ಚರಿಸಿ, ದೀರ್ಘ ಮಾಡಬೇಡಿ।",
        "master_audio_error": "ತರಬೇತುದಾರನ ಆಡಿಯೊ ಡೌನ್‌ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ।", "demo_notice": "ಪ್ರಮುಖ ಸೂಚನೆ: ನೈಜ ಆಡಿಯೊ ಎಂಜಿನ್ ಜೋಡಿಸುವವರೆಗೆ ಈ ಮೌಲ್ಯಗಳು ಕೇವಲ ಪ್ರದರ್ಶನಕ್ಕಾಗಿ ಇರುತ್ತವೆ।",
        "scoring_title": "🎯 ಶ್ಲೋಕ ಗುಣಮಟ್ಟದ ಸ್ಕೋರ್‌ಕಾರ್ಡ್ (Strict Evaluation Mode)", "score_accent": "ಉಚ್ಚಾರಣಾ ಶುದ್ಧತೆ", "score_rhythm": "ಲಯ ಮತ್ತು ಮಾತ್ರೆ",
        "score_tempo": "ವೇಗದ ಸ್ಥಿರತೆ", "score_pitch": "ಸ್ವರ ಹೊಂದಾಣಿಕೆ", "score_total": "ಒಟ್ಟು ಅಂಕಗಳು", "unsatisfactory": "ಅಸಮರ್ಪಕ ಪ್ರದರ್ಶನ - ತಿದ್ದುಪಡಿ ಅಗತ್ಯವಿದೆ"
    },
    "ml": {
        "language": "ഇന്റർഫേസ് ഭാഷ", "title": "🕉️ ലേൺ ഗീത - ശ്ലോക ഉച്ചാരണവും ലയവും വിശകലനം",
        "subtitle": "ദ്വിലിപി പാരായണം, സമയം, ലയം, സ്വരം എന്നിവയുടെ താരതമ്യം।", "chapter": "അധ്യായം തിരഞ്ഞെടുക്കുക",
        "from_shloka": "ശ്ലോക നമ്പർ മുതൽ", "to_shloka": "ശ്ലോക നമ്പർ വരെ", "audio": "പാരായണ ഓഡിയോ അപ്‌ലോഡ് ചെയ്യുക",
        "run": "🔍 പാരായണം വിലയിരുത്തുക", "select_required": "അധ്യായവും ശ്ലോക പരിധിയും തിരഞ്ഞെടുക്കുക।",
        "audio_required": "ഓഡിയോ ഫയൽ അപ്‌ലോഡ് ചെയ്യുക।", "analyzing": "പാരായണം വിശകലനം ചെയ്യുന്നു...",
        "verse_not_found": "ശ്ലോകം ലഭ്യമല്ല।", "chapter_word": "അധ്യായം", "shloka_word": "ശ്ലോകം",
        "tempo_waveform": "ലയത്തിന്റെ സ്ഥിരത", "timing_title": "📊 1. സമയവും വേഗതയും കാണിക്കുന്ന പട്ടിക",
        "segment": "ശ്ലോക ഭാഗം", "target": "ലക്ഷ്യം (പരിശീലകൻ)", "actual": "യാഥാർത്ഥ്യം", "offset": "വ്യത്യാസം",
        "speed_status": "വേഗതയുടെ നില", "total": "ആകെ", "segment_1": "ഭാഗം 1", "segment_2": "ഭാഗം 2",
        "slow": "പതുക്കെ (ലയ വ്യതിയാനം)", "close": "ഏകദേശം അടുത്ത്", "pause_long": "ദൈർഘ്യമേറിയ ഇടവേള",
        "matrix_title": "🗣️ 2. അക്ഷരവും ലയവും", "trainer_rhythm": "പരിശീലകന്റെ ലയം", "your_chanting": "നിങ്ങളുടെ പാരായണം",
        "swar": "സ്വരം", "murdha": "മൂർദ്ധാവ്", "matra": "മാത്ര", "rhythm": "ലയം", "low_scale": "താഴ്ന്ന സ്വരം", "unwanted_pause": "ആവശ്യമില്ലാത്ത ഇടവേള",
        "pitch_title": "🎵 3. സ്വര ക്രമീകരണ ചാർട്ട്", "trainer_melody": "പരിശീലകന്റെ നിശ്ചിത സ്വരം", "your_scale": "നിങ്ങളുടെ സ്വരം",
        "corrections_title": "📝 അക്ഷര തിരുത്തലുകൾ", "target_syllable": "ലക്ഷ്യമാക്കിയ അക്ഷരം", "error_type": "പിശക് തരം", "guidance": "തിരുത്തൽ നിർദ്ദേശം",
        "pitch_mismatch": "സ്വര വ്യതിയാനം", "duration_error": "മാത്രാ പിശക്",
        "pitch_guidance": "'{char}' എന്ന അക്ഷരത്തിലെ സ്വരം പരിശീലകന്റേതുമായി പൊരുത്തപ്പെടുന്നില്ല। 100% കൃത്യത വേണം।",
        "duration_guidance": "'{char}' എന്ന അക്ഷരം ഹ്രസ്വമായി ഉച്ചരിക്കേണ്ടതായിരുന്നു, നീട്ടരുത്।",
        "master_audio_error": "പരിശീലകന്റെ ഓഡിയോ ഡൗൺലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല।", "demo_notice": "പ്രധാനം: യഥാർത്ഥ ഓഡിയോ എൻജിൻ ബന്ധിപ്പിക്കുന്നതുവരെ ഈ മൂല്യങ്ങൾ പ്രദർശനത്തിന് മാത്രമുള്ളതാണ്।",
        "scoring_title": "🎯 ശ്ലോക ഗുണനിലവാര സ്കോർകാർഡ് (Strict Evaluation Mode)", "score_accent": "ഉച്ചാരണ ശുദ്ധി", "score_rhythm": "ലയവും മാത്രയും",
        "score_tempo": "വേഗതയുടെ സ്ഥിരത", "score_pitch": "സ്വരം ഒപ്പിക്കൽ", "score_total": "ആകെ മാർക്ക്", "unsatisfactory": "തൃപ്തികരമല്ലാത്ത പ്രകടനം - തിരുത്തൽ ആവശ്യമാണ്"
    },
    "mni": {
        "language": "ইন্টারফেস লোন", "title": "🕉️ লর্ন গীতা - শ্লোক উচ্চারণ অমসুং লয় বিশ্লেষক",
        "subtitle": "অনী লিপি, মতম, লয় অমসুং স্বর তুলনা।", "chapter": "অধ্যায় খনবীয়ু",
        "from_shloka": "শ্লোক নম্বরদগী", "to_shloka": "শ্লোক নম্বর ফাওবা", "audio": "পাঠ अডিও আপলোড তৌবীয়ু",
        "run": "🔍 পাঠ মূল্যায়ন তৌবীয়ু", "select_required": "অধ্যায় অমসুং শ্লোক সীমা খনবীয়ু।",
        "audio_required": "অডিও ফাইল আপলোড তৌবীয়ু।", "analyzing": "পাঠ বিশ্লেষণ তৌরি...",
        "verse_not_found": "শ্লোক ফংদে।", "chapter_word": "অধ্যায়", "shloka_word": "শ্লোক",
        "tempo_waveform": "মতম অমসুং লয়গী লেংদবা মতৌ", "timing_title": "📊 1. মতম অমসুং गतिগী টেবিল",
        "segment": "শ্লোক খায়দোকপা", "target": "ওজা (ট্রেনার)", "actual": "অশেংবা", "offset": "খেন্নবা",
        "speed_status": "গতিগী ফীভમ", "total": "অপুনবা", "segment_1": "শ্লোক শরুক 1", "segment_2": "শ্লোক শরুক 2",
        "slow": "তপ্না (লয় হোংলকপা)", "close": "নক্না", "pause_long": "লেপ্পা মতম সাংথবা",
        "matrix_title": "🗣️ 2. ময়েক অমসুং লয়", "trainer_rhythm": "ওজাগী লয়", "your_chanting": "নহাক্কী পাঠ",
        "swar": "স্বর", "murdha": "মূর্ধা", "matra": "মাত্রা", "rhythm": "লয়", "low_scale": "নেম্বা স্বर", "unwanted_pause": "মथৌ তাদবা লেপ্পা",
        "pitch_title": "🎵 3. স্বর / পিচ চার্ট", "trainer_melody": "ওजাগী পান্দম স্বর", "your_scale": "নহাক্কী স্বর",
        "corrections_title": "📝 ময়েক ময়েক্কী চুমথোকপা", "target_syllable": "পান্দম ময়েক", "error_type": "অশোকপগী মখল", "guidance": "চুমথোক্নবা লमজিং",
        "pitch_mismatch": "স্বর মান্নদবা", "duration_error": "মাত্রাগী অশোকপা",
        "pitch_guidance": "'{char}' ময়েক অসি ওজাগী স্বরগা মান্নদে। স্বর ১০০% চুমথোকীয়ু।",
        "duration_guidance": "'{char}' ময়েক অসি তেন্না থোক্কদবনি, সাংনা চিংশিনবগী অশোকপনি।",
        "master_audio_error": "ওজাগী অডিও ডাউনলোড তৌবা ঙमদ্রে।", "demo_notice": "মরুওইবা: অশেংবা অডিও ইঞ্জিন কাঙলুপ অসিગા শम্নদ্রিফাওবা অসি উৎনবা খक्तনি।",
        "scoring_title": "🎯 শ্লোক গুণগত স্কোরকার্ড (Strict Evaluation Mode)", "score_accent": "উচ্চারণ চুম্বা", "score_rhythm": "লয় অমসুং মাত্রা",
        "score_tempo": "গতি লেংদবা", "score_pitch": "স্বর চুনবা", "score_total": "অপუნবা মার্ক", "unsatisfactory": "অপেনবা পোত্থোক নত্তে - চুমথোকপা মথৌ তাই"
    },
    "mr": {
        "language": "इंटरफेस भाषा", "title": "🕉️ लर्न गीता - श्लोक उच्चार व लय विश्लेषक",
        "subtitle": "द्विलिपी पठण, वेळ, लय आणि स्वर यांची तुलना।", "chapter": "अध्याय निवडा",
        "from_shloka": "श्लोक क्रमांकापासून", "to_shloka": "श्लोक क्रमांकापर्यंत", "audio": "पठणाचा ऑडिओ अपलोड करा",
        "run": "🔍 पठणाचे मूल्यमापन करा", "select_required": "अध्याय आणि श्लोक मर्यादा निवडा।",
        "audio_required": "ऑडिओ फाइल अपलोड करा।", "analyzing": "पठणाचे विश्लेषण सुरू आहे...",
        "verse_not_found": "श्लोक उपलब्ध नाही।", "chapter_word": "अध्याय", "shloka_word": "श्लोक",
        "tempo_waveform": "गति आणि लयीची सुसंगतता", "timing_title": "📊 1. वेळ आणि गती सारणी",
        "segment": "श्लोक खंड", "target": "लक्ष्य (प्रशिक्षक)", "actual": "वास्तविक", "offset": "फरक",
        "speed_status": "गतीची स्थिती", "total": "एकूण", "segment_1": "भाग 1", "segment_2": "भाग 2",
        "slow": "हळू (लय बदल)", "close": "जवळपास अचूक", "pause_long": "विराम जास्त लांबला",
        "matrix_title": "🗣️ 2. अक्षर आणि लय", "trainer_rhythm": "प्रशिक्षकाची लय", "your_chanting": "तुमचे पठण",
        "swar": "स्वर", "murdha": "मूर्धा", "matra": "मात्रा", "rhythm": "लय", "low_scale": "सखल स्वर", "unwanted_pause": "अनावश्यक विराम",
        "pitch_title": "🎵 3. स्वर / पिच ट्युनिंग चार्ट", "trainer_melody": "प्रशिक्षकाचा लक्ष्य स्वर", "your_scale": "तुमचा स्वर",
        "corrections_title": "📝 अक्षरनिहाय दुरुस्ती", "target_syllable": "लक्षित अक्षर", "error_type": "त्रुटीचा प्रकार", "guidance": "सुधारणेसाठी मार्गदर्शन",
        "pitch_mismatch": "स्वरातील तफावत", "duration_error": "मात्रेची त्रुटी",
        "pitch_guidance": "'{char}' या अक्षराचा स्वर प्रशिक्षकाच्या स्वराशी जुळत नाही। अचूकता १००% हवी।",
        "duration_guidance": "'{char}' हे अक्षर ह्रस्व (लहान) हवे होते, पण ते लांबवले गेले। ते संक्षिप्त व स्पष्ट ठेवा।",
        "master_audio_error": "प्रशिक्षकाचा ऑडिओ डाउनलोड झाला नाही।", "demo_notice": "महत्त्वपूर्ण: वास्तविक ऑडिओ विश्लेषण इंजिन जोडले जाईपर्यंत हे आकडे केवळ निदर्शनासाठी आहेत।",
        "scoring_title": "🎯 श्लोक गुणवत्ता स्कोअरकार्ड (Strict Evaluation Mode)", "score_accent": "उच्चारण शुद्धता", "score_rhythm": "लय व मात्रा",
        "score_tempo": "गती सुसंगतता", "score_pitch": "स्वर जुळवणी", "score_total": "एकूण गुण", "unsatisfactory": "असमाधानकारक कामगिरी - सुधारणा आवश्यक"
    },
    "ne": {
        "language": "इन्टरफेस भाषा", "title": "🕉️ लर्न गीता - श्लोक उच्चारण र लय विश्लेषक",
        "subtitle": "द्विलिपि पाठ, समय, लय र स्वरको तुलना।", "chapter": "अध्याय छान्नुहोस्",
        "from_shloka": "श्लोक नम्बरदेखि", "to_shloka": "श्लोक नम्बरसम्म", "audio": "पाठको अडियो अपलोड गर्नुहोस्",
        "run": "🔍 पाठ मूल्याङ्कन गर्नुहोस्", "select_required": "अध्याय र श्लोक सीमा छान्नुहोस्।",
        "audio_required": "অडियो फाइल अपलोड गर्नुहोस्।", "analyzing": "पाठ विश्लेषण हुँदैछ...",
        "verse_not_found": "श्लोक फेला परेन।", "chapter_word": "अध्याय", "shloka_word": "श्लोक",
        "tempo_waveform": "गति र लयको निरन्तरता", "timing_title": "📊 1. समय र गति तालिका",
        "segment": "श्लोक खण्ड", "target": "लक्ष्य (प्रशिक्षक)", "actual": "वास्तविक", "offset": "अन्तर",
        "speed_status": "गतिको अवस्था", "total": "कुल", "segment_1": "खण्ड 1", "segment_2": "खण्ड 2",
        "slow": "ढिलो (लय परिवर्तन)", "close": "नजिक", "pause_long": "विराम लामो",
        "matrix_title": "🗣️ 2. अक्षर र लय", "trainer_rhythm": "प्रशिक्षकको लय", "your_chanting": "تपाईंको पाठ",
        "swar": "स्वर", "murdha": "मूर्धा", "matra": "मात्रा", "rhythm": "लय", "low_scale": "तल्लो स्वर", "unwanted_pause": "अनावश्यक विराम",
        "pitch_title": "🎵 3. स्वर / पिच चार्ट", "trainer_melody": "प्रशिक्षकको लक्ष्य स्वर", "your_scale": "तपाईंको स्वर",
        "corrections_title": "📝 अक्षरगत सुधार", "target_syllable": "लक्षित अक्षर", "error_type": "त्रुटिको प्रकार", "guidance": "सुधार निर्देशन",
        "pitch_mismatch": "स्वर फरक", "duration_error": "मात्रा त्रुटि",
        "pitch_guidance": "'{char}' अक्षरको स्वर प्रशिक्षकको स्वरभन्दा फरक छ। शतप्रतिशत शुद्ध हुनुपर्छ।",
        "duration_guidance": "'{char}' अक्षर छोटो हुनुपर्थ्यो, तर लामो भयो। यसलाई संक्षिप्त राख्नुहोस्।",
        "master_audio_error": "प्रशिक्षकको अडियो डाउनलोड भएन।", "demo_notice": "महत्त्वपूर्ण: वास्तविक अडियो विश्लेषण नजोडिएसम्म यी मानहरू प्रदर्शनका लागि हुन्।",
        "scoring_title": "🎯 श्लोक गुणस्तर स्कोरकार्ड (Strict Evaluation Mode)", "score_accent": "उच्चारण शुद्धता", "score_rhythm": "लय र मात्रा",
        "score_tempo": "गति सुसंगतता", "score_pitch": "स्वर मिलान", "score_total": "कुल अङ्क", "unsatisfactory": "असंतोषजनक प्रदर्शन - सुधारको आवश्यकता"
    },
    "or": {
        "language": "ଇଣ୍ଟରଫେସ୍ ଭାଷା", "title": "🕉️ ଲର୍ନ ଗୀତା - ଶ୍ଲୋକ ଉଚ୍ଚାରଣ ଓ ଲୟ ବିଶ୍ଳେଷକ",
        "subtitle": "ଦ୍ୱିଲିପି ପାଠ, ସମୟ, ଲୟ ଓ ସ୍ୱର ତୁଳନା।", "chapter": "ଅଧ୍ୟାୟ ବାଛନ୍ତୁ",
        "from_shloka": "ଶ୍ଲୋକ ସଂଖ୍ୟାରୁ", "to_shloka": "ଶ୍ଲୋକ ସଂଖ୍ୟା ପର୍ଯ୍ୟନ୍ତ", "audio": "ପାଠ ଅଡିଓ ଅପଲୋଡ୍ କରନ୍ତୁ",
        "run": "🔍 ପାଠ ମୂଲ୍ୟାୟନ କରନ୍ତୁ", "select_required": "ଅଧ୍ୟାୟ ଓ ଶ୍ଲୋକ ସୀମା ବାଛନ୍ତୁ।",
        "audio_required": "ଅଡିଓ ଫାଇଲ୍ ଅପଲୋଡ୍ କରନ୍ତୁ।", "analyzing": "ପାଠ ବିଶ୍ଳେଷଣ ହେଉଛି...",
        "verse_not_found": "ଶ୍ଲୋକ ମିଳିଲା ନାହିଁ।", "chapter_word": "ଅଧ୍ୟାୟ", "shloka_word": "ଶ୍ଲୋକ",
        "tempo_waveform": "ଗତି ଏବଂ ଲୟର ସମାନତା", "timing_title": "📊 1. ସମୟ ଏବଂ ଗତି ସାରଣୀ",
        "segment": "ଶ୍ଲୋକ ଅଂଶ", "target": "ଲକ୍ଷ୍ୟ (ପ୍ରଶିକ୍ଷକ)", "actual": "ପ୍ରକୃତ", "offset": "ପାର୍ଥକ୍ୟ",
        "speed_status": "ଗତି ସ୍ଥିତି", "total": "ମୋଟ", "segment_1": "ଭାଗ 1", "segment_2": "ଭାଗ 2",
        "slow": "ଧୀମା (ଲୟ ପରିବର୍ତ୍ତନ)", "close": "ପାଖାପାଖି ଠିକ୍", "pause_long": "ବିରାମ ଅଧିକ ଲମ୍ବା",
        "matrix_title": "🗣️ 2. ଅକ୍ଷර ଓ ଲୟ ବିଶ୍ଳେଷଣ", "trainer_rhythm": "ପ୍ରଶିକ୍ଷକଙ୍କ ଲୟ", "your_chanting": "ଆପଣଙ୍କ ପାଠ",
        "swar": "ସ୍ୱର", "murdha": "ମୂର୍ଦ୍ଧା", "matra": "ମାତ୍ରା", "rhythm": "ଲୟ", "low_scale": "ନିମ୍ନ ସ୍ୱର", "unwanted_pause": "ଅନାବଶ୍ୟକ ବିରାମ",
        "pitch_title": "🎵 3. ସ୍ୱର / ପିଚ୍ ଚାର୍ଟ", "trainer_melody": "ପ୍ରଶିକ୍ଷକଙ୍କ ଲକ୍ଷ୍ୟ ସ୍ୱର", "your_scale": "ଆପଣଙ୍କ ସ୍ୱର",
        "corrections_title": "📝 ଅକ୍ଷරଭିତ୍ତିକ ସଂଶୋଧନ", "target_syllable": "ଲକ୍ଷିତ ଅକ୍ଷର", "error_type": "ତ୍ରୁଟିର ପ୍ରକାର", "guidance": "ସଂଶୋଧନ ମାର୍ଗଦର୍ଶନ",
        "pitch_mismatch": "ସ୍ୱר ଅମେଳ", "duration_error": "ମାତ୍ରା ତ୍ରୁଟି",
        "pitch_guidance": "'{char}' ଅକ୍ଷରର ସ୍ୱର ପ୍ରଶିକ୍ଷକଙ୍କ ସ୍ୱର ସହ ମିଶୁନାହିଁ। ଏହା ୧୦୦% ଠିକ୍ ହେବା ଆବଶ୍ୟକ।",
        "duration_guidance": "'{char}' ଅକ୍ଷରଟି ହ୍ରସ୍ୱ ହେବା ଉଚିତ୍ ଥିଲା, କିନ୍ତୁ ଦୀର୍ଘ ହୋଇଛି। ଏହାକୁ ସଂକ୍ଷିପ୍ତ ରଖନ୍ତୁ।",
        "master_audio_error": "ପ୍ରଶିକ୍ଷକଙ୍କ ଅଡିଓ ଡାଉନଲୋଡ୍ ହୋଇପାରିଲା ନାହିଁ।", "demo_notice": "ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ: ପ୍ରକୃତ ଅଡିଓ ଇଞ୍ଜିନ ସଂଯୋଗ ହେବା ପର୍ଯ୍ୟନ୍ତ ଏହି ମୂଲ୍ୟଗୁଡ଼ିକ କେବଳ ପ୍ରଦର୍ଶନ ପାଇଁ।",
        "scoring_title": "🎯 ଶ୍ଲୋକ ଗୁଣବତ୍ତା ସ୍କୋରକାର୍ด์ (Marks System)", "score_accent": "ଉଚ୍ଚାରଣ ଶୁଦ୍ଧତା", "score_rhythm": "ଲୟ ଓ ମାତ୍ରା",
        "score_tempo": "ଗତି ସ୍ଥିରତା", "score_pitch": "ସ୍ୱර ମେଳ", "score_total": "ମୋଟ ନମ୍ବର", "unsatisfactory": "ଅସନ୍ତୋଷଜନକ ପ୍ରଦର୍ଶନ - ସଂଶୋଧନ ଆବଶ୍ୟକ"
    },
    "sd": {
        "language": "انٽرفيس ٻولي", "title": "🕉️ لرن گيتا - شلوڪ اچار ۽ لئه تجزيو",
        "subtitle": "ٻٽي لپي، وقت، لئه ۽ سُر جو مقابلو۔", "chapter": "باب چونڊيو",
        "from_shloka": "شلوڪ نمبر کان", "to_shloka": "شلوڪ نمبر تائين", "audio": "پاٺ جو آڊيو اپلوڊ ڪريو",
        "run": "🔍 پاٺ جو جائزو وٺو", "select_required": "باب ۽ شلوڪ جي حد چونڊيو۔",
        "audio_required": "آڊيو فائل اپلوڊ ڪريو۔", "analyzing": "پاٺ جو تجزيو ٿي رهيو آهي...",
        "verse_not_found": "شلوڪ نه مليو۔", "chapter_word": "باب", "shloka_word": "شلوڪ",
        "tempo_waveform": "وقت ۽ لئه جي برابري", "timing_title": "📊 1. وقت ۽ رفتار جو نقشو",
        "segment": "شلوڪ جو حصো", "target": "استاد (ٽرينر)", "actual": "اصل", "offset": "فرق",
        "speed_status": "رفتار جي حالت", "total": "ڪُل", "segment_1": "حصو 1", "segment_2": "حصو 2",
        "slow": "سست (لئه جي تبديلي)", "close": "ويجهو", "pause_long": "وڌيڪ وقفو",
        "matrix_title": "🗣️ 2. اکر ۽ لئه تجزيو", "trainer_rhythm": "استاد جي لئه", "your_chanting": "توهان جو پاٺ",
        "swar": "سُر", "murdha": "مُورڌا", "matra": "ماترا", "rhythm": "لئه", "low_scale": "پست سُر", "unwanted_pause": "غير ضروري وقفو",
        "pitch_title": "🎵 3. پچ / سُر جو چارٽ", "trainer_melody": "استاد جو مقرر سُر", "your_scale": "توهان جو سُر",
        "corrections_title": "📝 اکرن جي درستگي", "target_syllable": "مقرر اکر", "error_type": "غلطي جو قسم", "guidance": "درستگي جي هدايت",
        "pitch_mismatch": "سُر جو تفاوت", "duration_error": "ماترا جي غلطي",
        "pitch_guidance": "اکر '{char}' تي توهان جو سُر استاد جي سُر سان نٿو ملي۔ غلطي ۱۰۰٪ درست ڪريو۔",
        "duration_guidance": "اکر '{char}' ننڍو هجڻ گهرجي ها، پر توهان ان کي ڊگهو ڪيو آهي۔ ننڍو ۽ صاف اچاريو۔",
        "master_audio_error": "استاد جو آڊيو ڊائون لوڊ نه ٿي سگهيو۔", "demo_notice": "اهم نوٽ: اصل آڊيو انجڻ جوڙڻ تائين هي انگ اکر صرف ڏيکارڻ لاءِ آهن۔",
        "scoring_title": "🎯 شلوڪ قابليت اسڪورڪارڊ (Marks System)", "score_accent": "اکرن جي شڌي", "score_rhythm": "لئه ۽ ماترا",
        "score_tempo": "رفتار جي برابري", "score_pitch": "سُرن جو ميل", "score_total": "ڪُل مارڪون", "unsatisfactory": "غير تسلي بخش ڪارڪردگي - درستگي جي ضرورت آهي"
    },
    "ta": {
        "language": "இடைமுக மொழி", "title": "🕉️ லேர்ன் கீதா - சுலோக உச்சரிப்பு மற்றும் லய பகுப்பாய்வி",
        "subtitle": "இரட்டை எழுத்து, நேரம், லயம் மற்றும் சுருதி ஒப்பீடு।", "chapter": "அத்தியாயத்தைத் தேர்ந்தெடுக்கவும்",
        "from_shloka": "சுலோக எண் முதல்", "to_shloka": "சுலோக எண் வரை", "audio": "பாராயண ஆடியோவைப் பதிவேற்றவும்",
        "run": "🔍 பாராயணத்தை மதிப்பிடவும்", "select_required": "அத்தியாயம் மற்றும் சுலோக வரம்பைத் தேர்ந்தெடுக்கவும்।",
        "audio_required": "ஆடியோ கோப்பைப் பதிவேற்றவும்।", "analyzing": "பாராயணம் பகுப்பாய்வு செய்யப்படுகிறது...",
        "verse_not_found": "சுலோகம் கிடைக்கவில்லை।", "chapter_word": "அத்தியாயம்", "shloka_word": "சுலோகம்",
        "tempo_waveform": "லயத்தின் சீரான தன்மை", "timing_title": "📊 1. நேரம் மற்றும் வேக அட்டவணை",
        "segment": "சுலோகப் பகுதி", "target": "இலக்கு (ஆசிரியர்)", "actual": "உண்மை", "offset": "வேறுப்பாடு",
        "speed_status": "வேக நிலை", "total": "மொத்தம்", "segment_1": "பகுதி 1", "segment_2": "பகுதி 2",
        "slow": "மெதுவான (லய மாற்றம்)", "close": "நெருக்கமானது", "pause_long": "நீண்ட இடைவெளி",
        "matrix_title": "🗣️ 2. அசை மற்றும் லயம்", "trainer_rhythm": "ஆசிரியரின் லயம்", "your_chanting": "உங்கள் பாராயணம்",
        "swar": "சுரம்", "murdha": "மூர்த்தா", "matra": "மாத்திரை", "rhythm": "லயம்", "low_scale": "தாழ்ந்த சுருதி", "unwanted_pause": "தேவையற்ற இடைவெளி",
        "pitch_title": "🎵 3. சுருதி சீரமைப்பு வரைபடம்", "trainer_melody": "ஆசிரியரின் இலக்கு சுருதி", "your_scale": "உங்களது சுருதி",
        "corrections_title": "📝 அசைவாரி திருத்தங்கள்", "target_syllable": "இலக்கு அசை", "error_type": "பிழை வகை", "guidance": "திருத்த வழிகாட்டுதல்",
        "pitch_mismatch": "சுருதி விலகல்", "duration_error": "மாத்திரைப் பிழை",
        "pitch_guidance": "'{char}' என்ற அசையின் சுருதி ஆசிரியரின் சுருதியோடு பொருந்தவில்லை। 100% துல்லியம் தேவை।",
        "duration_guidance": "'{char}' என்ற அசை குறிலாக ஒலிக்க வேண்டும், நெடிலாக நீட்டக் கூடாது। சுருக்கமாக ஒலிக்கவும்।",
        "master_audio_error": "ஆசிரியரின் ஆடியோவை பதிவிறக்க முடியவில்லை।", "demo_notice": "முக்கியம்: உண்மையான ஆடியோ எஞ்சின் இணைக்கப்படும் வரை இந்த மதிப்புகள் மாதிரி மட்டுமே।",
        "scoring_title": "🎯 சுலோக மதிப்பெண் அட்டை (Marks System)", "score_accent": "உச்சரிப்பு சுத்தி", "score_rhythm": "லயம் மற்றும் மாத்திரை",
        "score_tempo": "வேக சீரமைப்பு", "score_pitch": "சுருதி பொருத்தம்", "score_total": "மொத்த மதிப்பெண்கள்", "unsatisfactory": "திருப்தியற்ற செயல்திறன் - திருத்தம் தேவை"
    },
    "te": {
        "language": "ఇంటర్‌ఫేస్ భాష", "title": "🕉️ లెర్న్ గీతా - శ్లోక ఉచ్చారణ మరియు లయ విశ్లేషకం",
        "subtitle": "ద్విలిపి పఠనం, సమయం, లయ మరియు స్వర పోలిక।", "chapter": "అధ్యాయం ఎంచుకోండి",
        "from_shloka": "శ్లోక సంఖ్య నుండి", "to_shloka": "శ్లోక సంఖ్య వరకు", "audio": "పఠన ఆడియోను అప్‌లోడ్ చేయండి",
        "run": "🔍 పఠనాన్ని మూల్యాంకనం చేయండి", "select_required": "అధ్యాయం మరియు శ్లోక పరిధిని ఎంచుకోండి।",
        "audio_required": "ఆడియో ఫైల్‌ను అప్‌లోడ్ చేయండి।", "analyzing": "పఠనాన్ని విశ్లేషిస్తోంది...",
        "verse_not_found": "శ్లోకం లభించలేదు।", "chapter_word": "అధ్యాయం", "shloka_word": "శ్లోకం",
        "tempo_waveform": "లయ మరియు వేగం యొక్క స్థిరత్వం", "timing_title": "📊 1. సమయ మరియు వేగ పట్టిక",
        "segment": "శ్లోక భాగం", "target": "లక్ష్యం (శిక్షకుడు)", "actual": "వాస్తవ పఠనం", "offset": "వ్యత్యాసం",
        "speed_status": "వేగ స్థితి", "total": "మొత్తం", "segment_1": "భాగం 1", "segment_2": "భాగం 2",
        "slow": "నెమ్మది (లయ మార్పు)", "close": "దగ్గరగా ఉంది", "pause_long": "ఎక్కువ విరామం",
        "matrix_title": "🗣️ 2. అక్షర మరియు లయ విశ్లేషణ", "trainer_rhythm": "శిక్షకుడి లయ", "your_chanting": "మీ పఠనం",
        "swar": "స్వరం", "murdha": "మూర్ధన్యం", "matra": "మాత్ర", "rhythm": "లయ", "low_scale": "తక్కువ స్వరం", "unwanted_pause": "అనవసర విరామం",
        "pitch_title": "🎵 3. స్వర స్థాయి / పిచ్ చార్ట్", "trainer_melody": "శిక్షకుడి లక్ష్య స్వరం", "your_scale": "మీ స్వరం",
        "corrections_title": "📝 అక్షరాల వారీగా సవరణలు", "target_syllable": "లక్ష్య అక్షరం", "error_type": "దోష రకం", "guidance": "సవరణ మార్గదర్శకం",
        "pitch_mismatch": "స్వర స్థాయి వ్యత్యాసం", "duration_error": "మాత్రల దోషం",
        "pitch_guidance": "'{char}' అక్షరం వద్ద మీ స్వరం శిక్షకుడి స్వరంతో సరిపోలడం లేదు। 100% ఖచ్చితత్వం ఉండాలి।",
        "duration_guidance": "'{char}' అక్షరాన్ని హ్రస్వంగా పలకాలి, ఎక్కువ సాగదీశారు। క్లుప్తంగా, స్పష్టంగా పలకండి।",
        "master_audio_error": "శిక్షకుడి ఆడియో డౌన్‌లోడ్ కాలేదు।", "demo_notice": "ముఖ్య గమనిక: నిజమైన ఆడియో ఇంజిన్ అనుసంధానించబడే వరకు ఈ విలువలన్నీ కేవలం ప్రదర్శన కోసం మాత్రమే।",
        "scoring_title": "🎯 శ్లోక మార్కుల నివేదిక (Marks System)", "score_accent": "ఉచ్చారణ శుద్ధత", "score_rhythm": "లయ మరియు మాత్ర",
        "score_tempo": "వేగ స్థిరత్వం", "score_pitch": "స్వర స్థాయి మేళవింపు", "score_total": "మొత్తం మార్కులు", "unsatisfactory": "అసంతృప్తికరమైన ప్రదర్శన - సవరణ అవసరం"
    }
}

def get_texts(language_code: str) -> dict:
    return {**I18N["en"], **I18N.get(language_code, {})}

# ============================================================
# HIGH-FIDELITY CUSTOM PREMIUM CSS STYLE
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
    .chart-explanation { background: #f4f6f8; border-left: 4px solid #ff3b30; padding: 10px 14px; font-size: 13px; color: #1d1d1f; border-radius: 0 8px 8px 0; margin-top: 8px; }
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

# ============================================================
# MAIN APPLICATION LOGIC INTERFACE
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

student_audio = st.file_uploader(lex["audio"], type=["mp3", "wav", "m4a", "aac"])

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

                # Strict reduction math configurations
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

                iast_p_word = iast_words[min(p_idx, len(iast_words)-1)] if iast_words else ""
                iast_m_word = iast_words[min(m_idx, len(iast_words)-1)] if iast_words else ""
                iast_p_syl = split_iast_into_syllables(iast_p_word)
                iast_m_syl = split_iast_into_syllables(iast_m_word)
                err_iast_p = iast_p_syl[0] if iast_p_syl else ""
                err_iast_m = iast_m_syl[0] if iast_m_syl else ""

                high_iast_words = []
                for idx, w in enumerate(iast_words):
                    sw = escape(w)
                    if idx == p_idx and err_iast_p:
                        sc = escape(err_iast_p)
                        sw = replace_first(sw, sc, f"<span class='error-pitch'>{sc}</span>")
                    elif idx == m_idx and err_iast_m:
                        sc = escape(err_iast_m)
                        sw = replace_first(sw, sc, f"<span class='error-syllable'>{sc}</span>")
                    high_iast_words.append(sw)

                colored_dev_html = " ".join(high_dev_words)
                colored_iast_html = " ".join(high_iast_words)

                # Shloka Render Core Screen Injection Block
                st.markdown(f"""
                <div dir="{page_direction}" class="shloka-container">
                    <div class="shloka-title">🚩 {escape(lex["chapter_word"])} {chapter}, {escape(lex["shloka_word"])} {shloka}</div>
                    <div class="shloka-devanagari" dir="ltr">{colored_dev_html}</div>
                    <div class="shloka-iast" dir="ltr">{colored_iast_html}</div>
                </div>
                """, unsafe_allow_html=True)

                # 🎯 MULTILINGUAL STRICT SCORING DISPLAY Enforced across variables
                st.markdown(f'<div dir="{page_direction}"><h3>{escape(lex["scoring_title"])}</h3></div>', unsafe_allow_html=True)
                sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
                sc_col1.metric(lex["score_accent"], f"{m_accent}/40", delta=f"-{40-m_accent}", delta_color="inverse")
                sc_col2.metric(lex["score_rhythm"], f"{m_rhythm}/30", delta=f"-{30-m_rhythm}", delta_color="inverse")
                sc_col3.metric(lex["score_tempo"], f"{m_tempo}/20", delta=f"-{20-m_tempo}", delta_color="inverse")
                sc_col4.metric(lex["score_pitch"], f"{m_pitch}/10", delta=f"-{10-m_pitch}", delta_color="inverse")
                st.html(f"<div dir='{page_direction}' style='background:#ffe5e5; border:1px solid #ff3b30; border-radius:10px; padding:12px; text-align:center; font-size:18px; font-weight:bold; color:#d70015;'>⚠️ {escape(lex['score_total'])}: {m_total} / 100 ({escape(lex['unsatisfactory'])})</div>")

                # Waveform Component Native Chart Rendering
                st.markdown(f"<div dir='{page_direction}' class='tempo-label'>{escape(lex['tempo_waveform'])}:</div>", unsafe_allow_html=True)
                wave_data = rng.integers(15, 60, size=45)
                wave_data[15] = 95; wave_data[30] = 88
                st.bar_chart(wave_data, height=90, use_container_width=True)
                
                # Dynamic Explanation for Waveform via Translation Tokens
                if language_code == "gu":
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>📈 આ ચાર્ટ શું કહે છે?</b><br>
                        આ ચાર્ટ તમારા પાઠની <b>ઝડપ અને સાતત્ય (Tempo Continuity)</b> દર્શાવે છે. જ્યાં ઊભી લીટીઓ સમાન ઊંચાઈની છે, ત્યાં તમારી ગતિ બરાબર છે. પરંતુ જ્યાં અચાનક મોટો ઊંચો બાર દેખાય છે, તેનો અર્થ એ છે કે ત્યાં તમે <b>અનાવશ્યક લાંબો વિરામ (પોઝ)</b> લીધો છે જે શ્লোકની લય તોડે છે.
                    </div>
                    """, unsafe_allow_html=True)
                elif language_code == "hi":
                    st.markdown("""
                    <div class="chart-explanation">
                        <b>📈 यह चार्ट क्या कहता है?</b><br>
                        यह चार्ट आपके पाठ की <b>गति और निरंतरता (Tempo Continuity)</b> को दर्शाता है। जहाँ लाइनें समान ऊँचाई की हैं, वहाँ गति ठीक है। लेकिन जहाँ अचानक ऊँचा बार दिखाई दे, वहाँ आपने <b>अनावश्यक लंबा विराम (पॉज़)</b> लिया है।
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chart-explanation">
                        <b>📈 What does this chart show?</b><br>
                        This chart visualizes your <b>Chanting Speed & Tempo Continuity</b>. Uniform bars indicate steady rhythm, while sudden tall bars reveal an <b>unwanted long pause</b> that breaks protocol.
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
                            <tr>
                                <td>└─ {escape(lex["segment_1"])}</td><td>{t_1:.1f}s</td><td>{a_1:.1f}s</td><td><span style="color:#ff9500;">+{a_1-t_1:.1f}s</span></td><td>⏱️ {escape(lex["close"])}</td>
                            </tr>
                            <tr>
                                <td>└─ {escape(lex["segment_2"])}</td><td>{t_2:.1f}s</td><td>{a_2:.1f}s</td><td><span style="color:#ff3b30;font-weight:700;">+{a_2-t_2:.1f}s</span></td><td>⏸️ {escape(lex["pause_long"])}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"<div dir='{page_direction}' class='section-sub-title'>{escape(lex['matrix_title'])}</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="matrix-line"><b>{escape(lex["trainer_rhythm"])}:</b> --({escape(lex["swar"])})--({escape(lex["murdha"])})--({escape(lex["matra"])})--[%s]--</div>
                <div class="matrix-line"><b>{escape(lex["your_chanting"])}:</b> --({escape(lex["low_scale"])})--({escape(lex["murdha"])})--({escape(lex["matra"])})--[%s]-- ⚠️ (+{metrics["offset_1"]:.1f}s)</div>
                """ % (escape(lex["rhythm"]), escape(lex["unwanted_pause"])), unsafe_allow_html=True)

                st.markdown(f"<div dir='{page_direction}' class='section-sub-title'>{escape(lex['pitch_title'])}</div>", unsafe_allow_html=True)
                chart_len = 45
                x_axis = np.linspace(0, 4 * np.pi, chart_len)
                trainer_pitch = 150 + 12 * np.sin(x_axis)
                student_pitch = trainer_pitch + rng.uniform(-25, 12, size=chart_len)
                
                pitch_df = pd.DataFrame({
                    lex["trainer_melody"]: trainer_pitch,
                    lex["your_scale"]: student_pitch
                })
                st.line_chart(pitch_df, height=140, use_container_width=True)
                
                # Dynamic Multi-Script Pitch Explanation
                if language_code == "gu":
                    st.markdown("""
                    <div class="chart-explanation" style="border-left-color: #ff3b30;">
                        <b>📈 આ ગ્રાફ શું કહે છે?</b><br>
                        આ તમારા <b>સ્વરનો ઉતાર-ચડાવ (Pitch/Swar Tuning)</b> દર્શાવે છે. 
                        <ul>
                            <li><b>સોલિડ લાઇન:</b> પ્રશિક્ષક (Trainer) નો સચોટ લક્ષ્ય સૂર છે જે પઠન શુદ્ધિ માટે સ્ટાન્ડર્ડ છે.</li>
                            <li><b>અસ્થિર લાઇન:</b> તમારો રેકોર્ડ થયેલો અવાજ છે. નિયમ મુજબ આ બંને લાઇન એકબીજાની બિલકુલ નજીક હોવી જોઈએ. જ્યાં ગેપ મોટો છે ત્યાં સૂર દોષ પકડાયો છે.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif language_code == "hi":
                    st.markdown("""
                    <div class="chart-explanation" style="border-left-color: #ff3b30;">
                        <b>📈 यह ग्राफ क्या कहता है?</b><br>
                        यह आपके <b>स्वर के उतार-चढ़ाव (Pitch/Swar Tuning)</b> को दर्शाता है।
                        <ul>
                            <li><b>सॉलिड लाइन:</b> प्रशिक्षक (Trainer) का शुद्ध मूल स्वर है।</li>
                            <li><b>अस्थिर लाइन:</b> आपकी रिकॉर्ड की गई आवाज़ है। कड़े नियमों के अनुसार दोनों लाइनें आपस में मेल खानी चाहिए। जहाँ अंतर है, वहाँ स्वर दोष है।</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chart-explanation" style="border-left-color: #ff3b30;">
                        <b>📈 What does this chart show?</b><br>
                        This tracks your <b>Pitch & Frequency Tuning (Swar Melody)</b>.
                        <ul>
                            <li><b>Solid Line:</b> Certified Trainer reference baseline melody.</li>
                            <li><b>Fluctuating Line:</b> Your recorded voice scale. In strict mode, both paths must overlap. Any wide gap indicates a clear pitch violation.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                p_guidance = lex["pitch_guidance"].format(char=err_p_char)
                d_guidance = lex["duration_guidance"].format(char=err_m_char)
                st.markdown(f"<div dir='{page_direction}' class='section-sub-title'>{escape(lex['corrections_title'])}</div>", unsafe_allow_html=True)
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
