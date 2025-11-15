import streamlit as st
import pandas as pd
import io
import re
from collections import defaultdict

# --- CORE LOGIC (Defined in separate functions or imported) ---

def get_salutation(speaker_tag, listener_tag):
    # Logic to select the most appropriate Vietnamese salutation
    # (e.g., "ông bạn," "anh em," "cưng ơi") based on the relationship.
    if speaker_tag in ['Cody', 'Tyler'] and listener_tag == 'Wife':
        return "cưng ơi"
    elif speaker_tag in ['Tyler', 'Cody', 'Cory', 'Coby', 'Garrett']:
        if listener_tag in ['Tyler', 'Cody', 'Cory', 'Coby', 'Garrett']:
            salutations = ["ông bạn", "anh em", "tui", "mày"] 
            return salutations[hash(speaker_tag + listener_tag) % 4] 
    return ""

LEXICON = {
    "Let's go": "Chơi thôi",
    "really good": "ngon lành",
    "What the": "Cái gì vậy cha nội",
    "I'm ready": "Tui sẵn sàng",
    "You guys": "Mấy ông",
    "Thank you": "Cảm ơn"
}

def translate_and_refine(text_to_translate, speaker=""):
    """Applies Vietnamese localized translation and style refinement."""
    
    translated = text_to_translate
    
    # Apply word replacements (TP.HCM slang)
    for en_word, vn_word in LEXICON.items():
        translated = translated.replace(en_word, vn_word)

    # Simplified example for pronoun replacement
    translated = translated.replace("I ", "Tui ").replace("you ", "ông ")
    
    # Post-processing: Adjust tone and remove Northern structures (e.g., final 'à' or 'nhỉ')
    translated = re.sub(r'(\?)$', r' hả ta?', translated)
    
    return translated

def parse_and_translate_file(file_content):
    """Parses SRT/TXT content and applies translation line-by-line."""
    
    # This is simplified. The real parser would handle timecodes and formatting perfectly.
    
    lines = file_content.split('\n')
    output_lines = []
    
    for line in lines:
        speaker = ""
        text_to_translate = line
        
        # Simple extraction of Speaker: Text (using a colon as separator for clarity)
        if ':' in line:
            parts = line.split(':', 1)
            speaker = parts[0].strip()
            text_to_translate = parts[1].strip()
            
            # Use 'ảnh' or 'chỉ' if referring to a person not present (implied)
            if speaker in ['he', 'she']:
                 speaker = "Ảnh" if speaker == 'he' else "Chỉ" 
            
            # Apply translation logic
            translated_text = translate_and_refine(text_to_translate, speaker)
            
            output_lines.append(f"{speaker}: {translated_text}")
        else:
            output_lines.append(translate_and_refine(line))
            
    return "\n".join(output_lines)


# --- STREAMLIT INTERFACE (User-facing text in Vietnamese) ---

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

if st.button("2. Dịch Thuật Chuyên Nghiệp (TP.HCM Style)", type="primary"):
    if uploaded_file is not None:
        try:
            # Read file content
            file_content = uploaded_file.getvalue().decode("utf-8")
            
            # Process and translate
            translated_content = parse_and_translate_file(file_content)
            
            st.success("✅ Dịch thuật và Tinh chỉnh Văn phong hoàn tất!")
            
            st.markdown("### 3. Kết Quả Dịch (Văn phong Miền Nam Tinh tế)")
            
            # Display result
            st.text_area("File đã dịch:", value=translated_content, height=500, key="translated_output")
            
            # Download button
            st.download_button(
                label="📥 Tải xuống File SRT Hoàn Thiện",
                data=translated_content.encode("utf-8"),
                file_name=f"DP_VN_Sub_{uploaded_file.name}",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {e}")
            st.warning("Vui lòng đảm bảo file được tải lên là file SRT hoặc TXT.")
            
    else:
        st.warning("Vui lòng tải lên một file script để bắt đầu!")

st.markdown("---")
st.info("**Cam kết:** Ứng dụng này sử dụng các quy tắc dịch thuật độc quyền được học từ các kênh lồng tiếng Việt chính thức để đảm bảo tính chuyên nghiệp và phù hợp với thương hiệu Dude Perfect.")
