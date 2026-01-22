---
description: How to enrich a Chinese vocabulary CSV using AI internal tools
---

This workflow describes how to leverage the AI's internal capabilities to enrich a Chinese vocabulary CSV file with Pinyin, Traditional Chinese sentences, and AI-generated illustrations.

### Steps:

1. **Provide the CSV File**: Ensure the CSV file is in the `csv_files/` directory.
2. **AI Enrichment**: Ask the AI to "enrich [filename].csv". 
3. **AI Tasks**:
    - **Select Difficulty**: Sentences should be appropriate for the specified **TOCFL Level** (e.g., Novice A1/A2, Level B1/B2).
    - **Generate Pinyin**: AI provides Hanyu Pinyin for missing entries.
    - **Generate Sentences**: AI creates Traditional Chinese sentences fitting the selected TOCFL level.
        - **Topics**: Cover a wide range (business, social, shopping, technology, travel, hobbies).
        - **Locations**: DO NOT feel obligated to include a city/location. If mentioned, ONLY use places in Taiwan.
        - **Format**: MUST follow EXACTLY `[Traditional Chinese Sentence] ([English Translation] - [Sentence Pinyin])`.
    - **Generate Illustrations**: AI uses its internal `generate_image` tool (using `imagen-4.0-generate-001`).
        - **Style**: Minimalist, flat vector art, clear and simple.
        - **Concrete Nouns**: Show the object ONLY. Do NOT include text. (e.g., a picture of a dog).
        - **Abstract/Ambiguous Concepts**: Describe a visual scenario/metaphor. You MAY include the English word stylistically in the image to help clarity if the concept is hard to depict visually.
    - **Save Media**: AI saves the generated images to the `images/` folder.
    - **Update CSV**: AI updates the CSV file ensuring it contains exactly these columns: `Chinese`, `Pinyin`, `English`, `Sentence`, `Image`.
4. **Finish**: Once enriched, you can run `python generate_deck.py [filename].csv` to create the Anki deck.

### Prompt Example:
"Please enrich B2L1.csv using the AI enrichment workflow. Use TOCFL Level 3 (B1) for sentences. For images, use the 'Concrete (No Text) / Abstract (Text Allowed)' strategy."
