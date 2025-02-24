import pandas as pd
import openai
from typing import Dict
import os

class TranslationSystem:
    def __init__(self, api_key: str):
        """Initialize translation system with OpenAI's GPT-4o-mini"""
        self.api_key = api_key
        self.translation_memory = {}
        self.term_base = {}
        
    def build_translation_assets(self, training_file: str) -> None:
        """
        Build translation memory and term base from training data.
        Args:
            training_file: Excel file with historical translations
        """
        print("Building translation assets...")
        
        df = pd.read_excel(training_file, header=None)
        
        for _, row in df.iterrows():
            zh_text = str(row[0]).strip() if pd.notna(row[0]) else None
            en_text = str(row[1]).strip() if pd.notna(row[1]) else None
            th_text = str(row[2]).strip() if pd.notna(row[2]) else None
            
            if zh_text and th_text:
                self.translation_memory[zh_text] = th_text
                if en_text:
                    self.translation_memory[en_text] = th_text
    
    def translate_text(self, zh_text: str, en_text: str, location: str, old_translation: str) -> str:
        """Translate text using OpenAI GPT-4o-mini with contextual integration"""
        prompt = f"""
        You are a professional Thai game localizer. Your task is to accurately localize in-game text from Chinese and/or English into Thai.
        
        - Ensure the translation maintains the correct tone and style according to the text's placement in the game.
        - Use both Chinese and English sources to determine the intended meaning and mood, giving priority to the Chinese text if English is unavailable.
        - Consider previous Thai translations for reference but do not rely on them if they are inaccurate.
        - The text placement in the game is indicated as: {location}, use this to adjust tone appropriately.
        
        Chinese Source: {zh_text if zh_text else 'N/A'}
        English Source: {en_text if en_text else 'N/A'}
        
        Previous Thai Translation (for reference only): {old_translation if old_translation else 'N/A'}
        
        Provide only the final localized Thai text, with no additional comments or explanations.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional Thai game localizer."},
                      {"role": "user", "content": prompt}],
            api_key=self.api_key
        )
        
        return response["choices"][0]["message"]["content"].strip()
    
    def process_translation(self, input_file: str, output_file: str):
        """Process localization from input file and save to output file."""
        print("Processing translation...")
        df = pd.read_excel(input_file)
        localized_count = 0
        
        for idx, row in df.iterrows():
            if pd.notna(row[9]) and str(row[9]).strip():
                continue  # Skip rows with existing localized text
            
            zh_text = str(row[1]).strip() if pd.notna(row[1]) else ""
            en_text = str(row[2]).strip() if pd.notna(row[2]) else ""
            location = str(row[5]).strip() if pd.notna(row[5]) else ""
            old_translation = str(row[3]).strip() if pd.notna(row[3]) else ""
            
            translated_text = self.translate_text(zh_text, en_text, location, old_translation)
            df.at[idx, 9] = translated_text
            localized_count += 1
            
            if localized_count >= 100:
                break  # Stop processing after 100 localized rows
        
        df.to_excel(output_file, index=False)
        print("Translation complete. Output saved to:", output_file)

# Usage
api_key = "YOUR_OPENAI_API_KEY"
translator = TranslationSystem(api_key)
translator.build_translation_assets("training.xlsx")
translator.process_translation("input.xlsx", "output.xlsx")
