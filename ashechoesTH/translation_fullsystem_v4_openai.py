import pandas as pd
import openai
from typing import Dict
import os
import re

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
            zh_text = str(row[1]).strip() if pd.notna(row[1]) else None
            en_text = str(row[2]).strip() if pd.notna(row[2]) else None
            
            if zh_text:
                self.translation_memory[zh_text] = en_text if en_text else ""
                if en_text:
                    self.translation_memory[en_text] = zh_text
    
    def contains_chinese(self, text):
        """Check if a string contains Chinese characters."""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def translate_text(self, zh_text: str, en_text: str, retries=3) -> str:
        """Translate text using OpenAI GPT-4o-mini with contextual integration, limiting retries"""
        if retries <= 0:
            print(f"Error: Unable to fully translate '{zh_text}'. Returning last attempt.")
            return "[Translation Unavailable]"

        prompt = f"""
        Translate the following in-game text into Thai, ensuring it accurately reflects the tone, style, and meaning while maintaining a natural reading experience.
        
        **Localization Rules:**
        - Prioritize **game-specific terminology** from established translations where available.
        - Adapt cultural references appropriately for Thai players while preserving the original intent.
        - Maintain consistency in naming conventions, character dialogue styles, and tone.
        - **Do not transliterate** names unless necessary, prefer localized naming conventions.
        - Ensure commands, UI texts, and short labels are concise and intuitive.
        - Avoid unnecessary punctuation, and do **not** end sentences with a period (".") unless grammatically required.
        
        **Translation Priorities:**
        1. **Use the English source if both Chinese and English are available**, as it may provide clearer context.
        2. If **English is missing**, rely on the Chinese text for meaning.
        3. If both sources are ambiguous, adapt using best localization practices.
        
        Chinese Source: {zh_text if zh_text else 'N/A'}
        English Source: {en_text if en_text else 'N/A'}
        
        Provide only the final localized Thai text, with no Chinese characters, and no additional comments.
        """
        
        client = openai.Client(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional Thai game localizer, responsible for accurately adapting in-game text from Chinese and/or English into Thai while maintaining the intended tone, style, and context within the game's world. Your translations must reflect the nuances of game terminology, character personalities, lore, and genre conventions to ensure a seamless player experience. Do remove . at the end of sentence, as it's not Thai. Leave \n or any markdown as it is."},
                      {"role": "user", "content": prompt}]
        )
        
        translated_text = response.choices[0].message.content.strip()

        # If translation still contains Chinese, retry with a decremented retry counter
        if self.contains_chinese(translated_text):
            print(f"Warning: Chinese characters detected in translation for {zh_text}. Retrying... ({retries - 1} attempts left)")
            return self.translate_text(zh_text, en_text, retries=retries-1)
        
        return translated_text
    
    def process_translation(self, input_file: str, output_file: str):
        """Process localization from input file and save to output file."""
        print("Processing translation...")
        df = pd.read_excel(input_file)
        total_rows = len(df)
        localized_count = 0
        completed_rows = 0
        
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[3]) and str(row.iloc[3]).strip():
                completed_rows += 1
                continue  # Skip rows with existing localized text
            
            zh_text = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            en_text = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            
            translated_text = self.translate_text(zh_text, en_text, retries=3)

            # Retry if translation is blank
            if not translated_text.strip():
                print(f"Warning: Empty translation for row {idx}. Retrying...")
                translated_text = self.translate_text(zh_text, en_text, retries=2)

            df.at[idx, df.columns[3]] = translated_text
            localized_count += 1
            completed_rows += 1
            
            progress = (completed_rows / total_rows) * 100
            print(f"Progress: {progress:.2f}% completed")
            
            if localized_count % 100 == 0:
                df.to_excel(output_file, index=False)  # Save progress after every 100 rows
                print(f"Saved progress at {localized_count} translated rows. Continuing...")
        
        df.to_excel(output_file, index=False)
        print("Translation complete. Output saved to:", output_file)
        
        self.perform_lqa(df, output_file)
    
    def perform_lqa(self, df, output_file: str):
        """Perform Localization Quality Assurance (LQA) after translation with progress tracking."""
        print("Performing LQA checks...")
        total_rows = len(df)
        checked_rows = 0
        
        for idx, row in df.iterrows():
            zh_text = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            translated_text = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
            
            if zh_text and not translated_text:
                print(f"Warning: Missing translation at row {idx}. Retrying...")
                df.at[idx, df.columns[3]] = self.translate_text(zh_text, row.iloc[2])
            
            checked_rows += 1
            progress = (checked_rows / total_rows) * 100
            print(f"LQA Progress: {progress:.2f}% completed")
        
        df.to_excel(output_file, index=False)
        print("LQA complete. Final output saved to:", output_file)


# Usage
api_key = "SECRET"
translator = TranslationSystem(api_key)
translator.build_translation_assets("training_data.xlsx")
translator.process_translation("1st_th_new_append_0226_fix.xlsx", "1st_th_new_append_0226_output_fix_v2.xlsx")
