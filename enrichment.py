from google import genai
from google.genai import types
import json
import os
import time
import typing_extensions as typing
from pydantic import BaseModel

# Define the schema for structured output using Pydantic
class EnrichmentResult(BaseModel):
    pinyin: str
    english: str
    sentence: str
    image_prompt: str

class VocabularyEnricher:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash'
        
    def enrich_word(self, chinese, english_context=None, level="Novice 2 (A2)"):
        """
        Enriches a single Chinese word with Pinyin, English definition, 
        and a Traditional Chinese sentence.
        """
        prompt = f"""
        You are a Chinese language teacher specializing in TOCFL (Taiwan) standards.
        Target Word: "{chinese}"
        Context: "{english_context if english_context else ''}"
        Target Level: {level}

        Please provide:
        1. Pinyin for the word (Taiwan hanyu pinyin numbers or accents okay).
        2. English definition (if context provided, match it; otherwise common meaning).
        3. A sentence in Traditional Chinese (Taiwan usage) appropriate for {level} students.
           - Vocabulary and grammar should match the {level} difficulty.
           - Format: "Traditional Sentence (English translation - Pinyin)"
           - Example: "這很有趣 (This is interesting - Zhe4 hen3 you3 qu4)"
        4. A visual description for an illustration.
           - Style: Minimalist, flat vector art, clear and simple.
           - **For Concrete Nouns**: Show the object ONLY. Do NOT include text. (e.g. a picture of a dog).
           - **For Abstract/Ambiguous Concepts**: Describe a visual scenario/metaphor. You MAY include the English word stylistically in the image to help clarity if the concept is hard to depict visually.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", 
                    response_schema=EnrichmentResult
                )
            )
            # The new SDK returns a parsed object if schema is provided
            if response.parsed:
                return response.parsed.model_dump()
            return json.loads(response.text)
        except Exception as e:
            print(f"Error enriching {chinese}: {e}")
            return None

    def generate_image(self, prompt, output_path):
        """
        Attempts to generate an image using Imagen if available.
        """
        try:
            # Note: Using the new SDK's image generation capability
            # We try 'imagen-4.0-generate-001' as requested
            response = self.client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="1:1"
                )
            )
            if response.generated_images:
                image = response.generated_images[0]
                image.image.save(output_path)
                return True
        except Exception as e:
            # Fail silently for images as it's an optional feature
            print(f"Image generation failed: {e}")
            pass
        return False

    def process_dataframe(self, df, level="Novice 2 (A2)", progress_callback=None):
        """
        Iterates through a DataFrame and enriches missing fields.
        """
        total = len(df)
        enriched_count = 0
        
        # Ensure columns exist
        for col in ['Pinyin', 'Sentence', 'Image']:
            if col not in df.columns:
                df[col] = ""

        # Make sure images directory exists
        if not os.path.exists('images'):
            os.makedirs('images')

        for index, row in df.iterrows():
            chinese = str(row['Chinese']).strip()
            if not chinese:
                continue

            # Skip if already enriched (has Sentence)
            if row.get('Sentence') and str(row['Sentence']).strip():
                if progress_callback:
                    progress_callback(index + 1, total)
                continue

            english_ctx = row.get('English', '')
            
            # 1. Text Enrichment
            result = self.enrich_word(chinese, english_ctx, level=level)
            if result:
                df.at[index, 'Pinyin'] = result['pinyin']
                # Only update English if it was empty, or maybe update it to be better?
                # Let's keep original English if present, else use new one.
                if not english_ctx:
                    df.at[index, 'English'] = result['english']
                
                df.at[index, 'Sentence'] = result['sentence']
                
                # 2. Image Generation
                img_filename = f"{chinese}.png"
                img_path = os.path.join("images", img_filename)
                
                # Check if image already exists
                if not os.path.exists(img_path):
                    success = self.generate_image(result['image_prompt'], img_path)
                    if success:
                        df.at[index, 'Image'] = img_filename
                else:
                     df.at[index, 'Image'] = img_filename

            # Rate Limit Protection (free tier is ~15 RPM, so sleep 10s is safer)
            time.sleep(10) 
            
            if progress_callback:
                progress_callback(index + 1, total)
        
        return df
