import streamlit as st
import io
import re
from collections import defaultdict
import random # Import random for better salutation rotation

# --- CORE LOGIC: DEFINITIONS AND RULES ---

# Simplified Lexicon for style refinement (TP.HCM slang and common phrases)
LEXICON = {
    # Pronoun simplification (for general phrases)
    "I'm": "Tui",
    "You are": "Ông",
    "You've": "Ông",
    "we are": "tụi mình",
    
    # Slang and intensity
    "Let's go": "Chơi thôi",
    "Go! Go!": "Tiến lên! Tiến lên!",
    "ready": "sẵn sàng",
    "think": "nghĩ là",
    "Oh my gosh": "Trời đất ơi",
    "What the": "Cái gì vậy cha nội",
    "insane": "điên quá xá",
    "awesome": "quá đã",
    "Thank you": "Cảm ơn",
    "well done": "ngon lành"
}

# 2. Salutation Table (Internal Logic for Pronoun Replacement)
# This logic will replace generic pronouns like 'I', 'you' with 'Tui', 'Ông'
# and add a custom end phrase to localize the style.
def apply_salutation_and_style(line_text, speaker_tag):
    
    # 1. Base Pronoun/Salutation Replacement (I -> Tui, you -> Ông/Bạn)
    # Note: Use list to randomize the phrase ending for better "luân phiên" style
    end_phrases = ["đó nha!", "luôn!", "quá chừng!", "hả ta?"]
    random_end = random.choice(end_phrases)

    # Convert pronouns
    if speaker_tag in ['Tyler', 'Cody', 'Cory', 'Coby', 'Garrett', 'Sparky']:
        line_text = re.sub(r'\bI\b', 'Tui', line_text, flags=re.IGNORECASE)
        # Use more intimate 'Ông' for internal Dudes
        line_text = re.sub(r'\b(you|you\'re|your)\b', 'ông', line_text, flags=re.IGNORECASE)
        
    elif speaker_tag in ['Wife', 'Bethany', 'Allison', 'Amy']:
        # Wives often use 'Anh' for their husband (Tyler/Cody)
        line_text = re.sub(r'\b(I|we)\b', 'Em', line_text, flags=re.IGNORECASE)
        line_text = re.sub(r'\b(you|your)\b', 'Anh', line_text, flags=re.IGNORECASE)
    
    # 2. Add localization/Slang (very simplified example)
    line_text = line_text.replace("so close", "sát nút")
    line_text = line_text.replace("perfect", "ngon lành")
    line_text = line_text.replace("good", "ổn áp")

    # 3. Add emotional ending to the last sentence
    # This is a key style requirement for TP.HCM tone
    if line_text and line_text.strip():
        # Check if the last character is a punctuation mark that can be replaced
        if line_text.strip()[-1] in ['.', '!', '?']:
            line_text = line_text.strip()[:-1] + random_end
        else:
            line_text += ' ' + random_end.strip('!')
            
    return line_text

def translate_and_refine(text_to_translate, speaker=""):
    """Applies the localization and style refinement rules."""
    
    # A. Apply Lexicon for TP.HCM Slang (This performs the basic 'translation')
    translated = text_to_translate
    for en_word, vn_word in LEXICON.items():
        # Use regex to replace whole words only, case-insensitively
        translated = re.sub(r'\b' + re.escape(en_word) + r'\b', vn_word, translated, flags=re.IGNORECASE)

    # B. Apply intimate style and salutations
    translated = apply_salutation_and_style(translated, speaker)
    
    return translated

def parse_and_translate_content(file_content):
    """Parses text line by line, preserving timecodes, and applies translation."""
    
    lines = file_content.split('\n')
    output_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # 1. Preserve empty lines and numerical indices
        if not stripped_line or re.match(r'^\d+$', stripped_line):
            output_lines.append(line)
            continue
        
        # 2. Preserve Timecode lines (e.g., 00:00:01,000 --> 00:00:03,000)
        if re.match(r'^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}', stripped_line):
            output_lines.append(line)
            continue

        # 3. Process Dialogue Line (Speaker: Text, handling both 'SRT-like' and plain text)
        speaker = ""
        text_to_translate = line
        
        # Simple attempt to extract Speaker: Text
        speaker_match = re.match(r"(\w+):\s*(.*)", line)
        if speaker_match:
            speaker = speaker_match.group(1)
            text_to_translate = speaker_match.group(2).strip()
            
            translated_text = translate_and_refine(text_to_translate, speaker)
            output_lines.append(f"{speaker}: {translated_text}")
        else:
            # Handle lines without explicit speaker (e.g., just dialogue/VO)
            translated_text = translate_and_refine(text_to_translate)
            output_lines.append(translated_text)
            
    return "\n".join(output_lines)


# --- STREAMLIT INTERFACE ---

st.set_page_config(layout="wide", page_title="DP-Viet-Translator App")

st.title("🚀 DP-Viet-Translator: Ứng Dụng Dịch Thuật Độc Quyền")
st.subheader("Chuyên nghiệp hóa phụ đề Dude Perfect theo văn phong Miền Nam/TP.HCM.")
st.markdown("---")
st.markdown("### 1. Tải lên Script Gốc")

uploaded_file = st.file_uploader(
    "Vui lòng tải lên file phụ đề (.srt) hoặc văn bản (.txt) có ghi rõ tên người nói (ví dụ: Tyler: Let's go!)", 
    type=['srt', 'txt']
)

st.markdown("---")

if st.button("Translate", type="primary"): # Updated button text
    if uploaded_file is not None:
        try:
            # Safely read file content
            bytes_data = uploaded_file.getvalue()
            # Try decoding as UTF-8 (standard)
            try:
                file_content = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1 for older/non-standard encoding
                file_content = bytes_data.decode("iso-8859-1")
            
            # Process and translate
            translated_content = parse_and_translate_content(file_content)
            
            st.success("✅ Dịch thuật và Tinh chỉnh Văn phong hoàn tất!")
            
            st.markdown("### 3. Kết Quả Dịch (Văn phong Miền Nam Tinh tế)")
            
            st.text_area("File đã dịch:", value=translated_content, height=500, key="translated_output")
            
            st.download_button(
                label="📥 Tải xuống File Phụ đề Hoàn Thiện",
                data=translated_content.encode("utf-8"),
                file_name=f"DP_VN_Sub_{uploaded_file.name}",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {e}")
            st.warning("Lỗi thường gặp là do định dạng file. Vui lòng đảm bảo file SRT có cấu trúc tiêu chuẩn.")
            
    else:
        st.warning("Vui lòng tải lên một file script để bắt đầu!")
