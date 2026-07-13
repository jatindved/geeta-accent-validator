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
# LANGUAGE OPTIONS (Strictly Filtered as per user request)
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
# COMPLETE INTERFACE TRANSLATIONS (All 14 Languages Full Scope)
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
        "unwanted_pause": "अनावश्यक विराम",
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
        "master_audio_error": "प्रशिक्षक का ऑडियो डाउनलोड नहीं हुआ। रिपोर्ट फिर भी दिखाई जाएगी।",
        "demo_notice": "महत्त्वपूर्ण: वास्तविक ऑडियो-विश्लेषण इंजन जुड़ने तक समय, स्वर एवं त्रुटि के आँकड़े प्रदर्शन हेतु हैं।",
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
        "pitch_guidance": "'{char}' অক্ষৰৰ স্বৰ প্ৰশিক্ষকৰ সৈতে মিল নাই। স্বৰ ঠিক কৰক।",
        "duration_guidance": "'{char}' অক্ষৰটো চুটি হ’ব লাগিছিল, কিন্তু দীঘল হ’ল। চুটি আৰু স্পষ্ট কৰক।",
        "master_audio_error": "প্ৰশিক্ষকৰ অডিঅ’ ডাউনলোড নহ’ল।", "demo_notice": "গুৰুত্বপূৰ্ণ: অডিঅ’ বিশ্লেষণ সংযোগ নোহোৱালৈকে এই মানসমূহ প্ৰদৰ্শনমূলক।",
    },
    "bn": {
        "language": "ইন্টারফেস ভাষা", "title": "🕉️ লার্ন গীতা - শ্লোক উচ্চারণ ও ছন্দ বিশ্লেষক",
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
        "pitch_guidance": "'{char}' অক্ষরের স্বর প্রশিক্ষকের স্বরের সঙ্গে মিলছে না। সুর ঠিক করুন।",
        "duration_guidance": "'{char}' অক্ষরটি সংক্ষিপ্ত হওয়া উচিত ছিল, কিন্তু দীর্ঘ হয়েছে। এটি স্পষ্ট ও ছোট রাখুন।",
        "master_audio_error": "প্রশিক্ষকের অডিও ডাউনলোড হয়নি।", "demo_notice": "গুরুত্বপূর্ণ: বাস্তব অডিও বিশ্লেষণ যুক্ত না হওয়া পর্যন্ত মানগুলো প্রদর্শনমূলক।",
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
        "slow": "ધીમું (લયમાં ફેરફાર)", "close": "લગભગ યોગ્ય", "pause_long": "વિરામ લાંબો",
        "matrix_title": "🗣️ 2. અક્ષર અને લય", "trainer_rhythm": "પ્રશિક્ષકની લય", "your_chanting": "તમારો પાઠ",
        "swar": "સ્વર", "murdha": "મૂર્ધા", "matra": "માત્રા", "rhythm": "લય", "low_scale": "નીચો સ્વર", "unwanted_pause": "અનાવશ્યક વિરામ",
        "pitch_title": "🎵 3. સ્વર / પિચ ચાર્ટ", "trainer_melody": "પ્રશિક્ષકનો લક્ષ્ય સ્વર", "your_scale": "તમારો સ્વર",
        "corrections_title": "📝 અક્ષરવાર સુધારા", "target_syllable": "લક્ષિત અક્ષર", "error_type": "ભૂલનો પ્રકાર", "guidance": "સુધારાનું માર્ગદર્શન",
        "pitch_mismatch": "સ્વરમાં તફાવત", "duration_error": "માત્રાની ભૂલ",
        "pitch_guidance": "'{char}' અક્ષરનો સ્વર પ્રશિક્ષકના સ્વરથી અલગ છે। પ્રશિક્ષકના સૂર સાથે મેળવો।",
        "duration_guidance": "'{char}' અક્ષર હ્રસ્વ હોવા છતાં લંબાયો છે। આ અક્ષરને ટૂંકો અને સ્પષ્ટ બોલો।",
        "master_audio_error": "પ્રશિક્ષકનું ઓડિયો ડાઉનલોડ થયું નથી। તેમ છતાં રિપોર્ટ બતાવવામાં આવશે।",
        "demo_notice": "મહત્ત્વપૂર્ણ: વાસ્તવિક ઓડિયો વિશ્લેષણ જોડાય ત્યાં સુધી આ આંકડા પ્રદર્શન માટે છે।",
    },
    "kn": {
        "language": "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ", "title": "🕉️ ಲರ್ನ್ ಗೀತಾ - ಶ್ಲೋಕ ಉಚ್ಚಾರಣೆ ಮತ್ತು ಲಯ ವಿશ્લેಷಕ",
        "subtitle": "ದ್ವಿಲಿಪಿ ಪಠಣ, ಸಮಯ, ಲಯ ಮತ್ತು ಸ್ವರ ಹೋಲಿಕೆ।", "chapter": "ಅಧ್ಯಾಯ ಆಯ್ಕೆಮಾಡಿ",
        "from_shloka": "ಶ್ಲೋಕ ಸಂಖ್ಯೆಯಿಂದ", "to_shloka": "ಶ್ಲೋಕ ಸಂಖ್ಯೆಯವರೆಗೆ", "audio": "ಪಠಣದ ಆಡಿಯೊ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "run": "🔍 පಠಣ ಮೌಲ್ಯಮಾಪನ ಮಾಡಿ", "select_required": "ಅಧ್ಯಾಯ ಮತ್ತು ಶ್ಲೋಕ ಮಿತಿಯನ್ನು ಆಯ್કેಮಾಡಿ।",
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
        "pitch_guidance": "'{char}' ಅಕ್ಷರದ ಸ್ವರವು ತರಬೇತುದಾರನ ಸ್ವರಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ।",
        "duration_guidance": "'{char}' ಅಕ್ಷರವನ್ನು ಹ್ರಸ್ವವಾಗಿ ಉಚ್ಚರಿಸಿ, ದೀರ್ಘ ಮಾಡಬೇಡಿ।",
        "master_audio_error": "ತರಬೇತುದಾರನ ಆಡಿಯೊ ಡೌನ್‌ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ।", "demo_notice": "ಪ್ರಮುಖ ಸೂಚನೆ: ನೈಜ ಆಡಿಯೊ ಎಂಜಿನ್ ಜೋಡಿಸುವವರೆಗೆ ಈ ಮೌಲ್ಯಗಳು ಕೇವಲ ಪ್ರದರ್ಶನಕ್ಕಾಗಿ ಇರುತ್ತವೆ।",
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
        "swar": "സ്വരം", "murdha": "മൂർദ്ധാവ്ല്", "matra": "മാത്ര", "rhythm": "ലയം", "low_scale": "താഴ്ന്ന സ്വരം", "unwanted_pause": "ആവശ്യമില്ലാത്ത ഇടവേള",
        "pitch_title": "🎵 3. സ്വര ക്രമീകരണ ചാർട്ട്", "trainer_melody": "പരിശീലകന്റെ നിശ്ചിത സ്വരം", "your_scale": "നിങ്ങളുടെ സ്വരം",
        "corrections_title": "📝 അക്ഷര തിരുത്തലുകൾ", "target_syllable": "ലക്ഷ്യമാക്കിയ അക്ഷരം", "error_type": "പിശക് തരം", "guidance": "തിരുത്തൽ നിർദ്ദേശം",
        "pitch_mismatch": "സ്വര വ്യതിയാനം", "duration_error": "മാത്രാ പിശക്",
        "pitch_guidance": "'{char}' എന്ന അക്ഷരത്തിലെ സ്വരം പരിശീലകന്റേതുമായി പൊരുത്തപ്പെടുന്നില്ല।",
        "duration_guidance": "'{char}' എന്ന അಕ್ಷരം ഹ്രസ്വമായി ഉച്ചരിക്കേണ്ടതായിരുന്നു, നീട്ടരുത്।",
        "master_audio_error": "പരിശീലകന്റെ ഓഡിയോ ഡൗൺലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല।", "demo_notice": "പ്രധാനം: യഥാർത്ഥ ഓഡിയോ എൻജിൻ ബന്ധിപ്പിക്കുന്നതുവരെ ഈ മൂല്യങ്ങൾ പ്രദർശനത്തിന് മാത്രമുള്ളതാണ്।",
    },
    "mni": {
        "language": "ইন্টারফেস লোন", "title": "🕉️ লর্ন গীতা - শ্লোক উচ্চারণ অমসুং লয় বিশ্লেষক",
        "subtitle": "অনী লিপি, মতম, লয় অমসুং স্বর তুলনা।", "chapter": "অধ্যায় খনবীয়ু",
        "from_shloka": "শ্লোক নম্বরদগী", "to_shloka": "শ্লোক নম্বর ফাওবা", "audio": "পাঠ অডিও আপলোড তৌবীয়ু",
        "run": "🔍 পাঠ মূল্যায়ন তৌবীয়ু", "select_required": "অধ্যায় অমসুং শ্লোক সীমা খনবীয়ু।",
        "audio_required": "অডিও ফাইল আপলোড তৌবীয়ু।", "analyzing": "পাঠ বিশ্লেষণ তৌরি...",
        "verse_not_found": "শ্লোক ফংদে।", "chapter_word": "অধ্যায়", "shloka_word": "শ্লোক",
        "tempo_waveform": "মতম অমসুং লয়গী লেংদবা মতৌ", "timing_title": "📊 1. মতম অমসুং গতিগী টেবিল",
        "segment": "শ্লোক খায়দোকপা", "target": "ওজা (ট্রেনার)", "actual": "অশেংবা", "offset": "খেন্নবা",
        "speed_status": "গতিগী ফীভম", "total": "অপুনবা", "segment_1": "শ্লোক শরুক 1", "segment_2": "শ্লোক শরুক 2",
        "slow": "তপ্না (লয় হোংলকপা)", "close": "নক্না", "pause_long": "লেপ্পা মতম সাংথবা",
        "matrix_title": "🗣️ 2. ময়েক অমসুং লয়", "trainer_rhythm": "ওজাগী লয়", "your_chanting": "নহাক্কী পাঠ",
        "swar": "স্বর", "murdha": "মূর্ধা", "matra": "মাত্রা", "rhythm": "লয়", "low_scale": "নেম্বা স্বর", "unwanted_pause": "মথৌ তাদবা লেপ্পা",
        "pitch_title": "🎵 3. স্বর / পিচ চার্ট", "trainer_melody": "ওজাগী পান্দম স্বর", "your_scale": "নহাক্কী স্বর",
        "corrections_title": "📝 ময়েক ময়েক্কী চুমথোকপা", "target_syllable": "পান্দম ময়েক", "error_type": "অশোকপগী মখল", "guidance": "চুমথোক্নবা লমজিং",
        "pitch_mismatch": "স্বর মান্নদবা", "duration_error": "মাত্রাগী অশোকপা",
        "pitch_guidance": "'{char}' ময়েক অসি ওজাগী স্বরগা মান্নদে। স্বর চুমথোকীয়ু।",
        "duration_guidance": "'{char}' ময়েক অসি তেন্না থোক্কদবনি, সাংনা চিংশিনবগী অশোকপনি।",
        "master_audio_error": "ওজাগী অডিও ডাউনলোড তৌবা ঙমদ্রে।", "demo_notice": "মরুওইবা: অশেংবা অডিও ইঞ্জিন কাঙলুপ অসিগা শম্নদ্রিফাওবা অসি উৎনবা খক্তনি।",
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
        "pitch_guidance": "'{char}' या अक्षराचा स्वर प्रशिक्षकाच्या स्वराशी जुळत नाही। स्वर प्रशिक्षकाच्या पट्टीत आणा।",
        "duration_guidance": "'{char}' हे अक्षर ह्रस्व (लहान) हवे होते, पण ते लांबवले गेले। ते संक्षिप्त व स्पष्ट ठेवा।",
        "master_audio_error": "प्रशिक्षकाचा ऑडिओ डाउनलोड झाला नाही।", "demo_notice": "महत्त्वपूर्ण: वास्तविक ऑडिओ विश्लेषण इंजिन जोडले जाईपर्यंत हे आकडे केवळ निदर्शनासाठी आहेत।",
    },
    "ne": {
        "language": "इन्टरफेस भाषा", "title": "🕉️ लर्न गीता - श्लोक उच्चारण र लय विश्लेषक",
        "subtitle": "द्विलिपि पाठ, समय, लय र स्वरको तुलना।", "chapter": "अध्याय छान्नुहोस्",
        "from_shloka": "श्लोक नम्बरदेखि", "to_shloka": "श्लोक नम्बरसम्म", "audio": "पाठको अडियो अपलोड गर्नुहोस्",
        "run": "🔍 पाठ मूल्याङ्कन गर्नुहोस्", "select_required": "अध्याय र श्लोक सीमा छान्नुहोस्।",
        "audio_required": "अडियो फाइल अपलोड गर्नुहोस्।", "analyzing": "पाठ विश्लेषण हुँदैछ...",
        "verse_not_found": "श्लोक फेला परेन।", "chapter_word": "अध्याय", "shloka_word": "श्लोक",
        "tempo_waveform": "गति र लयको निरन्तरता", "timing_title": "📊 1. समय र गति तालिका",
        "segment": "श्लोक खण्ड", "target": "लक्ष्य (प्रशिक्षक)", "actual": "वास्तविक", "offset": "अन्तर",
        "speed_status": "गतिको अवस्था", "total": "कुल", "segment_1": "खण्ड 1", "segment_2": "खण्ड 2",
        "slow": "ढिलो (लय परिवर्तन)", "close": "नजिक", "pause_long": "विराम लामो",
        "matrix_title": "🗣️ 2. अक्षर र लय", "trainer_rhythm": "प्रशिक्षकको लय", "your_chanting": "तपाईंको पाठ",
        "swar": "स्वर", "murdha": "मूर्धा", "matra": "मात्रा", "rhythm": "लय", "low_scale": "तल्लो स्वर", "unwanted_pause": "अनावश्यक विराम",
        "pitch_title": "🎵 3. स्वर / पिच चार्ट", "trainer_melody": "प्रशिक्षकको लक्ष्य स्वर", "your_scale": "तपाईंको स्वर",
        "corrections_title": "📝 अक्षरगत सुधार", "target_syllable": "लक्षित अक्षर", "error_type": "त्रुटिको प्रकार", "guidance": "सुधार निर्देशन",
        "pitch_mismatch": "स्वर फरक", "duration_error": "मात्रा त्रुटि",
        "pitch_guidance": "'{char}' अक्षरको स्वर प्रशिक्षकको स्वरभन्दा फरक छ। यसलाई मिलाउनुहोस्।",
        "duration_guidance": "'{char}' अक्षर छोटो हुनुपर्थ्यो, तर लामो भयो। यसलाई संक्षिप्त राख्नुहोस्।",
        "master_audio_error": "प्रशिक्षकको अडियो डाउनलोड भएन। रिपोर्ट भने देखाइनेछ।",
        "demo_notice": "महत्त्वपूर्ण: वास्तविक अडियो विश्लेषण नजोडिएसम्म यी मानहरू प्रदर्शनका लागि हुन्।",
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
        "matrix_title": "🗣️ 2. ଅକ୍ଷର ଓ ଲୟ ବିଶ୍ଳେଷଣ", "trainer_rhythm": "ପ୍ରଶିକ୍ଷକଙ୍କ ଲୟ", "your_chanting": "ଆପଣଙ୍କ ପାଠ",
        "swar": "ସ୍ୱର", "murdha": "ମୂର୍ଦ୍ଧା", "matra": "ମାତ୍ରା", "rhythm": "ଲୟ", "low_scale": "ନିମ୍ନ ସ୍ୱର", "unwanted_pause": "ଅନାବଶ୍ୟକ ବିରାମ",
        "pitch_title": "🎵 3. ସ୍ୱର / ପିଚ୍ ଚାର୍ଟ", "trainer_melody": "ପ୍ରଶିକ୍ଷକଙ୍କ ଲକ୍ଷ୍ୟ ସ୍ୱର", "your_scale": "ଆପଣଙ୍କ ସ୍ୱର",
        "corrections_title": "📝 ଅକ୍ଷରଭିତ୍ତିକ ସଂଶୋଧନ", "target_syllable": "ଲକ୍ଷିତ ଅକ୍ଷର", "error_type": "ତ୍ରୁଟିର ପ୍ରକାର", "guidance": "ସଂଶୋଧନ ମାର୍ଗଦର୍ଶନ",
        "pitch_mismatch": "ସ୍ୱର ଅମେଳ", "duration_error": "ମାତ୍ରା ତ୍ରୁଟି",
        "pitch_guidance": "'{char}' ଅକ୍ଷରର ସ୍ୱର ପ୍ରଶିକ୍ଷକଙ୍କ ସ୍ୱର ସହ ମିଶୁନାହିଁ।",
        "duration_guidance": "'{char}' ଅକ୍ଷରଟି ହ୍ରସ୍ୱ ହେବା ଉଚିତ୍ ଥିଲା, କିନ୍ତୁ ଦୀର୍ଘ ହୋଇଛି। ଏହାକୁ ସଂକ୍ଷିପ୍ତ ରଖନ୍ତୁ।",
        "master_audio_error": "ପ୍ରଶିକ୍ଷକଙ୍କ ଅଡିଓ ଡାଉନଲୋଡ୍ ହୋଇପାରିଲା ନାହିଁ।", "demo_notice": "ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ: ପ୍ରକୃତ ଅଡିଓ ଇଞ୍ଜିନ ସଂଯୋଗ ହେବା ପର୍ଯ୍ୟନ୍ତ ଏହି ମୂଲ୍ୟଗୁଡ଼ିକ କେବଳ ପ୍ରଦର୍ଶନ ପାଇଁ।",
    },
    "sd": {
        "language": "انٽرفيس ٻولي", "title": "🕉️ لرن گيتا - شلوڪ اچار ۽ لئه تجزيو",
        "subtitle": "ٻٽي لپي، وقت، لئه ۽ سُر جو مقابلو۔", "chapter": "باب چونڊيو",
        "from_shloka": "شلوڪ نمبر کان", "to_shloka": "شلوڪ نمبر تائين", "audio": "پاٺ جو آڊيو اپلوڊ ڪريو",
        "run": "🔍 پاٺ جو جائزو وٺو", "select_required": "باب ۽ شلوڪ جي حد چونڊيو۔",
        "audio_required": "آڊيو فائل اپلوڊ ڪريو۔", "analyzing": "پاٺ جو تجزيو ٿي رهيو آهي...",
        "verse_not_found": "شلوڪ نه مليو۔", "chapter_word": "باب", "shloka_word": "شلوڪ",
        "tempo_waveform": "وقت ۽ لئه جي برابري", "timing_title": "📊 1. وقت ۽ رفتار جو نقشو",
        "segment": "شلوڪ جو حصو", "target": "استاد (ٽرينر)", "actual": "اصل", "offset": "فرق",
        "speed_status": "رفتار جي حالت", "total": "ڪُل", "segment_1": "حصو 1", "segment_2": "حصو 2",
        "slow": "سست (لئه جي تبديلي)", "close": "ويجهو", "pause_long": "وڌيڪ وقفو",
        "matrix_title": "🗣️ 2. اکر ۽ لئه تجزيو", "trainer_rhythm": "استاد جي لئه", "your_chanting": "توهان جو پاٺ",
        "swar": "سُر", "murdha": "مُورڌا", "matra": "ماترا", "rhythm": "لئه", "low_scale": "پست سُر", "unwanted_pause": "غير ضروري وقفو",
        "pitch_title": "🎵 3. پچ / سُر جو چارٽ", "trainer_melody": "استاد جو مقرر سُر", "your_scale": "توهان جو سُر",
        "corrections_title": "📝 اکرن جي درستگي", "target_syllable": "مقرر اکر", "error_type": "غلطي جو قسم", "guidance": "درستگي جي هدايت",
        "pitch_mismatch": "سُر جو تفاوت", "duration_error": "ماترا جي غلطي",
        "pitch_guidance": "اکر '{char}' تي توهان جو سُر استاد جي سُر سان نٿو ملي۔ ان کي صحيح ڪريو۔",
        "duration_guidance": "اکر '{char}' ننڍو هجڻ گهرجي ها، پر توهان ان کي ڊگهو ڪيو آهي۔ ننڍو ۽ صاف اچاريو۔",
        "master_audio_error": "استاد جو آڊيو ڊائون لوڊ نه ٿي سگهيو۔", "demo_notice": "اهم نوٽ: اصل آڊيو انجڻ جوڙڻ تائين هي انگ اکر صرف ڏيکارڻ لاءِ آهن۔",
    },
    "ta": {
        "language": "இடைமுக மொழி", "title": "🕉️ லேர்ன் கீதா - சுலோக உச்சரிப்பு மற்றும் லய பகுப்பாய்வி",
        "subtitle": "இரட்டை எழுத்து, நேரம், லயம் மற்றும் சுருதி ஒப்பீடு।", "chapter": "அத்தியாயத்தைத் தேர்ந்தெடுக்கவும்",
        "from_shloka": "சுலோக எண் முதல்", "to_shloka": "சுலோக எண் வரை", "audio": "பாராயண ஆடியோவைப் பதிவேற்றவும்",
        "run": "🔍 பாராயணத்தை மதிப்பிடவும்", "select_required": "அத்தியாயம் மற்றும் சுலோக வரம்பைத் தேர்ந்தெடுக்கவும்।",
        "audio_required": "ஆடியோ கோப்பைப் பதிவேற்றவும்।", "analyzing": "பாராயணம் பகுப்பாய்வு செய்யப்படுகிறது...",
        "verse_not_found": "சுலோகம் கிடைக்கவில்லை।", "chapter_word": "அத்தியாயம்", "shloka_word": "சுலோகம்",
        "tempo_waveform": "லயத்தின் சீரான தன்மை", "timing_title": "📊 1. நேரம் மற்றும் வேக அட்டவணை",
        "segment": "சுலோகப் பகுதி", "target": "இலக்கு (ஆசிரியர்)", "actual": "உண்மை", "offset": "வேறுபாடு",
        "speed_status": "வேக நிலை", "total": "மொத்தம்", "segment_1": "பகுதி 1", "segment_2": "பகுதி 2",
        "slow": "மெதுவான (லய மாற்றம்)", "close": "நெருக்கமானது", "pause_long": "நீண்ட இடைவெளி",
        "matrix_title": "🗣️ 2. அசை மற்றும் லயம்", "trainer_rhythm": "ஆசிரியரின் லயம்", "your_chanting": "உங்கள் பாராயணம்",
        "swar": "சுரம்", "murdha": "மூர்த்தா", "matra": "மாத்திரை", "rhythm": "லயம்", "low_scale": "தாழ்ந்த சுருதி", "unwanted_pause": "தேவையற்ற இடைவெளி",
        "pitch_title": "🎵 3. சுருதி சீரமைப்பு வரைபடம்", "trainer_melody": "ஆசிரியரின் இலக்கு சுருதி", "your_scale": "உங்களது சுருதி",
        "corrections_title": "📝 அசைவாரி திருத்தங்கள்", "target_syllable": "இலக்கு அசை", "error_type": "பிழை வகை", "guidance": "திருத்த வழிகாட்டுதல்",
        "pitch_mismatch": "சுருதி விலகல்", "duration_error": "மாத்திரைப் பிழை",
        "pitch_guidance": "'{char}' என்ற அசையின் சுருதி ஆசிரியரின் சுருதியோடு பொருந்தவில்லை। சுருதியைச் சரிசெய்யவும்।",
        "duration_guidance": "'{char}' என்ற அசை குறிலாக ஒலிக்க வேண்டும், நெடிலாக நீட்டக் கூடாது। சுருக்கமாக ஒலிக்கவும்।",
        "master_audio_error": "ஆசிரியரின் ஆடியோவை பதிவிறக்க முடியவில்லை।", "demo_notice": "முக்கியம்: உண்மையான ஆடியோ எஞ்சின் இணைக்கப்படும் வரை இந்த மதிப்புகள் மாதிரி மட்டுமே।",
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
        "pitch_guidance": "'{char}' అక్షరం వద్ద మీ స్వరం శిక్షకుడి స్వరంతో సరిపోలడం లేదు। శృతి సవరించుకోండి।",
        "duration_guidance": "'{char}' అక్షరాన్ని హ్రస్వంగా పలకాలి, ఎక్కువ సాగదీశారు। క్లుప్తంగా, స్పష్టంగా పలకండి।",
        "master_audio_error": "శిక్షకుడి ఆడియో డౌన్‌లోడ్ కాలేదు।", "demo_notice": "ముఖ్య గమనిక: నిజమైన ఆಡಿಯೊ ఇంజిన్ అనుసంధానించబడే వరకు ఈ విలువలన్నీ కేవలం ప్రదర్శన కోసం మాత్రమే।",
    }
}

# Master Fallback Control Function
def get_texts(lang_code: str) -> dict:
    return {**I18N["en"], **I18N.get(lang_code, {})}

# ============================================================
# PREMIUM CSS STYLING
# ============================================================
st.markdown(
    """
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     "Noto Sans", "Noto Sans Devanagari",
                     "Noto Sans Bengali", "Noto Sans Gujarati",
                     "Noto Sans Gurmukhi", "Noto Sans Kannada",
                     "Noto Sans Malayalam", "Noto Sans Oriya",
                     "Noto Sans Tamil", "Noto Sans Telugu", sans-serif;
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
    .matrix-line { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; background: #f1f3f4; padding: 9px; border-radius: 7px; margin: 5px 0; white-space: pre-wrap; }
    .badge-pitch { display: inline-block; background: #ffe5e5; color: #d70015; padding: 4px 7px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .badge-matra { display: inline-block; background: #fff2e5; color: #c75b00; padding: 4px 7px; border-radius: 6px; font-weight: 700; font-size: 11px; }
    .highlight-char { background: #ffd60a; color: #000000; padding: 2px 4px; border-radius: 4px; font-weight: 700; }
    .demo-notice { border: 1px solid #ffcc00; background: #fff9db; color: #5c4b00; border-radius: 10px; padding: 10px 12px; font-size: 12px; margin: 12px 0; }
    @media (max-width: 600px) {
        .heading-text h1 { font-size: 23px; }
        .shloka-container { padding: 15px; }
        .shloka-devanagari { font-size: 18px; }
        .shloka-iast { font-size: 14px; }
        .analysis-table { min-width: 620px; }
    }
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
    pattern = r"([bcdfghjklmnpqrstvwxyz]h?[āīūṛṝḷḹeaiouṃṁḥ]?|[aeiouāīūṛṝḷḹ])"
    return re.findall(pattern, word, flags=re.IGNORECASE)

def replace_first(text: str, old: str, new: str) -> str:
    if not old: return text
    return text.replace(old, new, 1)

def render_html(html: str) -> None:
    clean_html = textwrap.dedent(html).strip()
    st.html(clean_html)

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

def make_waveform_svg(chapter: int, shloka: int) -> str:
    rng = np.random.default_rng(chapter * 1000 + shloka)
    bars = []
    for index in range(60):
        height = int(rng.integers(14, 39))
        y = 43 - height
        fill = "#ff3b30" if index in (17, 41) else "#34c759"
        bars.append(f"<rect x='{index * 12 + 10}' y='{y}' width='8' height='{height}' rx='3' fill='{fill}' />")

    return (
        "<svg width='100%' height='45' viewBox='0 0 740 45' preserveAspectRatio='none' style='background:#f1f3f4;border-radius:8px;'>"
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

# ============================================================
# DYNAMIC INTERFACE CONTROLS
# ============================================================
selected_language_name = st.selectbox(
    "🌐 Interface Language",
    options=[name for name, _ in LANGUAGE_OPTIONS],
    index=0,
    key="interface_language",
)

language_code = LANGUAGE_NAME_TO_CODE[selected_language_name]
lex = get_texts(language_code)
page_direction = "rtl" if language_code in {"ur", "sd"} else "ltr"

render_html(
    f"""
    <div dir="{page_direction}" class="heading-text">
        <h1>{escape(lex["title"])}</h1>
        <p>{escape(lex["subtitle"])}</p>
    </div>
    """
)

hin_db, eng_db = load_geeta_databases()

# Form Inputs
col1, col2, col3 = st.columns(3)
with col1:
    chapter_sel = st.selectbox(
        lex["chapter"], options=list(range(1, 19)), index=None, placeholder="-",
        format_func=lambda value: f"{lex['chapter_word']} {value}", key="chapter_sel"
    )
with col2:
    start_shloka = st.selectbox(lex["from_shloka"], options=list(range(1, 79)), index=None, placeholder="-", key="start_shloka")
with col3:
    end_shloka = st.selectbox(lex["to_shloka"], options=list(range(1, 79)), index=None, placeholder="-", key="end_shloka")

student_audio = st.file_uploader(lex["audio"], type=["mp3", "wav", "m4a", "aac", "ogg", "flac"], key="student_audio")

render_html(f'<div dir="{page_direction}" class="demo-notice">{escape(lex["demo_notice"])}</div>')

# ============================================================
# PROCESS EVALUATION
# ============================================================
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
                                <line x1="50" y1="30" x2="550" y2="30" stroke="#0071e3" stroke-width="2" />
                                <path d="M 50 30 L 550 30" stroke="#34c759" stroke-width="3" fill="none" />
                                <path d="M 50 48 Q 150 54 250 42 T 450 50 T 550 45" stroke="#ff3b30" stroke-width="2" stroke-dasharray="4 3" fill="none" />
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
            if master_audio_path and os.path.exists(master_audio_path): st.remove(master_audio_path)
