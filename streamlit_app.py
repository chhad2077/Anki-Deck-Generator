import streamlit as st
import pandas as pd
import io
import os
import generate_deck
import enrichment
import re

# Configuration
MAX_ROWS = 50

def sanitize_string(s):
    """Prevents CSV Injection by prepending a quote to dangerous starting characters."""
    if not isinstance(s, str):
        return s
    # Excel/Sheets injection characters: =, +, -, @
    if s and s[0] in ['=', '+', '-', '@']:
        return "'" + s
    return s

def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))


# Page Config
st.set_page_config(
    page_title="Anki Chinese Deck Generator",
    page_icon="🎴",
    layout="centered"
)

# --- Sidebar: Configuration ---
st.sidebar.header("🔑 API Access")

api_mode = st.sidebar.radio("Choose API Key Source", ["BYO Key (Free)", "Friend Access Code"])

# Level Configuration
tocfl_level = st.sidebar.selectbox(
    "Select TOCFL Level (Difficulty)", 
    ["Novice 1 (A1)", "Novice 2 (A2)", "Level 3 (B1)", "Level 4 (B2)", "Level 5 (C1)", "Level 6 (C2)"],
    index=1,
    help="Determines the complexity of the example sentences."
)

api_key = None

if api_mode == "BYO Key (Free)":
    api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
    st.sidebar.markdown("""
    **Don't have a key?**  
    [Get a free Gemini API key here](https://aistudio.google.com/app/apikey)  
    *(Requires a Google Account)*
    """)
else:
    access_code = st.sidebar.text_input("Enter Access Code", type="password")
    if access_code:
        # Check against secrets
        try:
            if access_code == st.secrets["ACCESS_PASSWORD"]:
                api_key = st.secrets["GEMINI_API_KEY"]
                st.sidebar.success("Access Granted! Using shared key.")
            else:
                st.sidebar.error("Invalid Access Code")
        except FileNotFoundError:
             st.sidebar.error("Secrets not configured on this server.")



st.sidebar.markdown("---")
if st.sidebar.button("🔄 Start Over / Reset"):
    # Clear session state for data, but keep API key input active
    for key in ['df', 'enrichment_complete', 'generated_apkg', 'generated_csv']:
        if key in st.session_state:
            del st.session_state[key]
    # Increment uploader key to reset the widget
    st.session_state.uploader_key += 1
    
    # Clean up physical files to prevent disk usage bloat
    import shutil
    for folder in ['images', 'audio', 'output']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder) # Recreate empty folder
            
    st.rerun()

# --- Main Interface ---
st.title("🎴 Anki Chinese Deck Generator")
st.markdown("""
Turn a simple list of words into a powerful **Anki Flashcard Deck** with:
- ✨ Pinyin & English Translations
- 🗣️ Sentences (Taiwan Context)
- 🖼️ Minimalist Illustrations (Experimental)
""")

# Session State Initialization
if 'df' not in st.session_state:
    st.session_state.df = None
if 'enrichment_complete' not in st.session_state:
    st.session_state.enrichment_complete = False
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# Step 1: Upload
st.header("1️⃣ Upload Vocabulary")

st.info("💡 **Tip:** You only need to provide 'Chinese' and (optionally) 'English' columns. The AI will do the rest!")

# Template Download
template_df = pd.DataFrame(columns=['Chinese', 'English'])
template_csv = template_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📄 Download CSV Template",
    data=template_csv,
    file_name="vocabulary_template.csv",
    mime="text/csv",
    help="Start with this file. Fill in the 'Chinese' column. 'English' is optional but helps with context."
)

uploaded_file = st.file_uploader("Upload your filled CSV", type=['csv'], key=f"uploader_{st.session_state.uploader_key}")

if uploaded_file:
    # Load CSV
    if st.session_state.df is None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # 1. Sanitize all string columns
            df = df.applymap(sanitize_string)
            
            # 2. Limit Rows
            if len(df) > MAX_ROWS:
                st.warning(f"⚠️ File too large! Only the first {MAX_ROWS} rows will be processed to keep API usage efficient.")
                df = df.head(MAX_ROWS)
            
            # Normalize columns
            if 'Chinese' in df.columns:
                st.session_state.df = df
            else:
                st.error("CSV must have a 'Chinese' column.")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# Manual Input (Fallback)
if st.session_state.df is None:
    st.markdown("Or paste your words here:")
    text_input = st.text_area(
        "Format: 'Chinese, English' OR just 'Chinese' (one per line). Order doesn't matter!", 
        height=150,
        placeholder="你好, Hello\n天氣, Weather\n貓\nDog, 狗"
    )
    
    if text_input and st.button("Load Text"):
        data = []
        for line in text_input.split('\n'):
            line = line.strip()
            if not line: continue
            
            if ',' in line:
                parts = [p.strip() for p in line.split(',', 1)]
                part1, part2 = parts[0], parts[1]
                
                # Smart Sort: If part2 is Chinese and part1 isn't, swap them
                if contains_chinese(part2) and not contains_chinese(part1):
                    data.append({'Chinese': part2, 'English': part1})
                else:
                    # Default assumption or if both/neither are Chinese
                    data.append({'Chinese': part1, 'English': part2})
            else:
                # Single word line
                data.append({'Chinese': line, 'English': ''})
                
        if data:
            df = pd.DataFrame(data)
            # Sanitize and Limit
            df = df.applymap(sanitize_string)
            if len(df) > MAX_ROWS:
                st.warning(f"⚠️ Input too large! Truncated to {MAX_ROWS} words.")
                df = df.head(MAX_ROWS)
            
            st.session_state.df = df
            st.rerun()

# Show Data Preview
if st.session_state.df is not None:
    st.dataframe(st.session_state.df.head())
    
    # Step 2: Enrich
    st.header("2️⃣ Enrich with AI")
    
    if st.session_state.enrichment_complete:
        st.success("Enrichment Complete!")
    else:
        if st.button("✨ Enrich Vocabulary"):
            if not api_key:
                st.warning("Please provide an API Key in the sidebar.")
            else:
                enricher = enrichment.VocabularyEnricher(api_key=api_key)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    progress = min(current / total, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing word {current} of {total}...")
                
                try:
                    with st.spinner("Calling Gemini API... (This takes ~4s per word)"):
                        st.session_state.df = enricher.process_dataframe(
                            st.session_state.df, 
                            level=tocfl_level,
                            progress_callback=update_progress
                        )
                    st.session_state.enrichment_complete = True
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# Step 3: Generate
if st.session_state.enrichment_complete:
    st.header("3️⃣ Generate Deck")
    
    # Deck Name Input
    deck_name = st.text_input("Deck Name (e.g. 'Chinese Book 1')", "My Chinese Vocabulary")
    
    # Initialize session state for generated files if not present
    if 'generated_apkg' not in st.session_state:
        st.session_state.generated_apkg = None
    if 'generated_csv' not in st.session_state:
        st.session_state.generated_csv = None
    
    if st.button("🔨 Create Anki Deck"):
        try:
            # Generate the package in memory
            st.session_state.generated_apkg = generate_deck.get_anki_package_bytes(
                st.session_state.df.to_dict('records'),
                book_name=deck_name,
                lesson_part="1" # Default for now
            )
            # Create CSV bytes
            st.session_state.generated_csv = st.session_state.df.to_csv(index=False).encode('utf-8')
            
            st.success("Deck generated successfully! Download below:")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error generating deck: {e}")

    # Persistent Download Buttons
    if st.session_state.generated_apkg:
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="⬇️ Download .apkg Deck",
                data=st.session_state.generated_apkg,
                file_name=f"{deck_name.replace(' ', '_')}.apkg",
                mime="application/octet-stream"
            )
        
        with col2:
            st.download_button(
                label="⬇️ Download Enriched CSV",
                data=st.session_state.generated_csv,
                file_name="enriched_vocabulary.csv",
                mime="text/csv"
            )
