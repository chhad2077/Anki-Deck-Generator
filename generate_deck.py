import os
import csv
import genanki
import hashlib
import io
from gtts import gTTS

# --- Configuration ---
CSV_DIR = "csv_files"
IMAGE_DIR = "images"
AUDIO_DIR = "audio"
OUTPUT_DIR = "output"

# Ensure directories exist
for directory in [CSV_DIR, IMAGE_DIR, AUDIO_DIR, OUTPUT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Anki Note Model Definition
MODEL_ID = 1607392319 # Genetic random ID
CHINESE_MODEL = genanki.Model(
    MODEL_ID,
    'Chinese Vocabulary Model',
    fields=[
        {'name': 'Chinese'},
        {'name': 'Pinyin'},
        {'name': 'English'},
        {'name': 'Sentence'},
        {'name': 'Audio'},
        {'name': 'Image'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div style="font-family: Arial; font-size: 60px; text-align: center;">{{Chinese}}</div>',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div style="font-family: Arial; font-size: 24px; text-align: center; color: gray;">{{Pinyin}}</div>
                <div style="font-family: Arial; font-size: 30px; text-align: center;">{{English}}</div>
                <br>
                <div style="font-family: Arial; font-size: 20px; text-align: center; font-style: italic;">{{Sentence}}</div>
                <br>
                <div style="text-align: center;">{{Image}}</div>
                {{Audio}}
            ''',
        },
    ],
    css='.card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }'
)

def get_deterministic_id(string):
    """Produces a consistent 10-digit integer from a string."""
    return int(hashlib.md5(string.encode()).hexdigest(), 16) % 10**10

def generate_audio_file(text, filename):
    """Generates audio file if it doesn't exist and returns the filename."""
    audio_path = os.path.join(AUDIO_DIR, filename)
    # Always regenerate to ensure we have the latest content (word + sentence)
    if True: # Force regeneration
        clean_text = text
        # If text contains a definition in parens (like the sentence format), strip it.
        # But we want "Word. Sentence."
        # The input text is passed as f"{chinese}. {sentence}"
        # We need to process the sentence part to remove (English - Pinyin)
        
        parts = text.split('.', 1)
        if len(parts) > 1:
            word = parts[0]
            sentence = parts[1]
            # Strip parens from sentence: "Chinese (English)" -> "Chinese"
            clean_sentence = sentence.split('(')[0].strip()
            clean_text = f"{word}. {clean_sentence}"
        else:
             clean_text = text.split('(')[0].strip()
        
        try:
            tts = gTTS(text=clean_text, lang='zh-tw')
            tts.save(audio_path)
        except Exception as e:
            print(f"Error generating audio for {text}: {e}")
    return filename

def create_anki_package(rows, book_name, lesson_part):
    """
    Core logic to create a genanki.Package from a list of dictionaries (rows).
    Returns (package, output_filename_base)
    """
    deck_id = get_deterministic_id(book_name)
    deck = genanki.Deck(deck_id, book_name)
    
    package_media = []
    
    for row in rows:
        chinese = row.get('Chinese', '').strip()
        pinyin = row.get('Pinyin', '').strip()
        english = row.get('English', '').strip()
        sentence = row.get('Sentence', '').strip()
        img_file = row.get('Image', '').strip()
        
        if not chinese:
            continue

        # Generate Audio
        audio_file = f"{chinese}.mp3"
        generate_audio_file(f"{chinese}. {sentence}", audio_file)
        
        # Add audio to media list if it exists (it should)
        if os.path.exists(os.path.join(AUDIO_DIR, audio_file)):
            package_media.append(os.path.join(AUDIO_DIR, audio_file))
        
        # Handle Image
        img_tag = ""
        if img_file:
            # Check if image file actually exists locally
            img_path = os.path.join(IMAGE_DIR, img_file)
            if os.path.exists(img_path):
                img_tag = f'<img src="{img_file}">'
                package_media.append(img_path)
            else:
                print(f"Warning: Image file not found: {img_path}")
        
        # Create Note
        note_id = get_deterministic_id(chinese)
        note = genanki.Note(
            model=CHINESE_MODEL,
            fields=[chinese, pinyin, english, sentence, f"[sound:{audio_file}]", img_tag],
            tags=[f"Lesson_{lesson_part}"],
            guid=note_id
        )
        deck.add_note(note)
            
    package = genanki.Package(deck)
    package.media_files = package_media
    return package

def create_deck_from_csv(filename):
    """Legacy wrapper for CLI usage."""
    # Parse filename for Book and Lesson
    base_name = os.path.splitext(filename)[0] # B2L1
    book_part = base_name.split('L')[0] if 'L' in base_name else base_name # B2
    lesson_part = base_name.split('L')[1] if 'L' in base_name else "1" # 1
    
    book_name = f"Chinese {book_part}"
    input_path = os.path.join(CSV_DIR, filename)
    
    rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    package = create_anki_package(rows, book_name, lesson_part)
    
    output_filename = f"{base_name}.apkg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    package.write_to_file(output_path)
    print(f"Deck created: {output_path}")
    return output_path

def get_anki_package_bytes(rows, book_name="Chinese Vocabulary", lesson_part="1"):
    """Generates an Anki package and returns it as bytes (for Streamlit download)."""
    package = create_anki_package(rows, book_name, lesson_part)
    
    # Write to in-memory byte stream
    # genanki's write_to_file accepts a file-like object
    buffer = io.BytesIO()
    package.write_to_file(buffer)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        create_deck_from_csv(sys.argv[1])
    else:
        print("Usage: python generate_deck.py <filename.csv>")

