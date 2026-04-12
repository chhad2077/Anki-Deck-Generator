---
description: How to enrich a Chinese vocabulary CSV using AI internal tools
---

This workflow describes how to leverage the AI's internal capabilities to enrich a Chinese vocabulary CSV file with Pinyin, Traditional Chinese sentences, and AI-generated illustrations, mirroring the logic in `enrichment.py`.

### Steps:

1. **Provide the CSV File**: Ensure the CSV file is in the `csv_files/` directory.
2. **AI Enrichment**: Ask the AI to "enrich [filename].csv".
3. **AI Task Execution**:
    - **Role**: Act as a Chinese language teacher specializing in TOCFL (Taiwan) standards.
    - **Input Data**: Use the target word and english context (if provided) from the CSV.
    - **Select Difficulty**: Use the specified **TOCFL Level** (default: Novice 2 (A2) or as requested).
    - **Generate Pinyin**: Provide Pinyin for the word (Taiwan hanyu pinyin numbers or accents are okay).
    - **Generate English**: Provide English definition (match context if provided, otherwise common meaning).
    - **Generate Sentences**: Create a sentence in Traditional Chinese (Taiwan usage) appropriate for the student level.
        - **Difficulty**: Vocabulary and grammar should match the target level.
        - **Format**: `Traditional Sentence (English translation - Pinyin)`
        - **Example**: `這很有趣 (This is interesting - Zhe4 hen3 you3 qu4)`
    - **Generate Illustrations**: Use the `generate_image` tool (model: `imagen-4.0-generate-001`) with a visual description:
        - **Style**: Minimalist, flat vector art, clear and simple.
        - **For Concrete Nouns**: Show the object ONLY. Do NOT include text. (e.g. a picture of a dog).
        - **For Abstract/Ambiguous Concepts**: Describe a visual scenario/metaphor. You MAY include the English word stylistically in the image to help clarity if the concept is hard to depict visually.
    - **Save Media**: AI saves the generated images to the `images/` folder.
    - **Update CSV**: AI updates the CSV file ensuring it contains exactly these columns: `Chinese`, `Pinyin`, `English`, `Sentence`, `Image`.
4. **Finish**: Once enriched, you can run `python generate_deck.py [filename].csv` to create the Anki deck.

### Prompt Example:
"Please enrich B2L1.csv using the AI enrichment workflow. Use TOCFL Level 3 (B1) for sentences. For images, use the 'Concrete (No Text) / Abstract (Text Allowed)' strategy."
