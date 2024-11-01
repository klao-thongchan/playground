import pandas as pd
import json
from typing import Dict, Tuple, List
import os
from datetime import datetime
import anthropic
import numpy as np

class TranslationSystem:
    def __init__(self, api_key: str):
        """Initialize translation system with Claude API key"""
        self.client = anthropic.Client(api_key=api_key)
        self.translation_memory = {}
        self.term_base = {}
        
    def build_translation_assets(self, training_file: str) -> None:
        """Build translation memory and term base from training data"""
        print("Building translation assets...")
        
        # Read all sheets from training file
        xlsx = pd.ExcelFile(training_file)
        
        # Dictionary to track term frequencies and translations
        term_candidates = {}
        
        # Process each sheet
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            
            # Process all cells in the sheet
            for col in df.columns:
                for idx, cell_value in df[col].items():
                    source = str(cell_value).strip()
                    
                    # Skip invalid entries
                    if pd.isna(source) or not source:
                        continue
                        
                    # Process each valid cell for translation memory and term base
                    if source in self.translation_memory:
                        self.translation_memory[source]['frequency'] += 1
                    else:
                        self.translation_memory[source] = {
                            'target': '',  # Will be filled during translation
                            'frequency': 1,
                            'alternatives': set()
                        }
                    
                    # Process terms for term base
                    words = source.split()
                    for n in range(1, min(5, len(words) + 1)):
                        for i in range(len(words) - n + 1):
                            term = ' '.join(words[i:i+n])
                            
                            if len(term) < 2:
                                continue
                                
                            if term not in term_candidates:
                                term_candidates[term] = {
                                    'translations': {},
                                    'frequency': 0
                                }
                            
                            term_candidates[term]['frequency'] += 1
        
        # Build term base with criteria
        for term, data in term_candidates.items():
            if (data['frequency'] >= 1 and 
                1 <= len(term) <= 500 and
                len(term.split()) <= 80):
                
                self.term_base[term] = ''  # Will be filled during translation
        
        print(f"Built translation memory with {len(self.translation_memory)} entries")
        print(f"Built term base with {len(self.term_base)} entries")

    def save_assets(self, output_dir: str) -> None:
        """Save translation memory and term base to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        tm_for_save = {
            k: {
                **v,
                'alternatives': list(v['alternatives'])
            } for k, v in self.translation_memory.items()
        }
        
        with open(os.path.join(output_dir, 'translation_memory.json'), 'w', encoding='utf-8') as f:
            json.dump(tm_for_save, f, ensure_ascii=False, indent=2)
            
        with open(os.path.join(output_dir, 'term_base.json'), 'w', encoding='utf-8') as f:
            json.dump(self.term_base, f, ensure_ascii=False, indent=2)
    
    def load_assets(self, input_dir: str) -> None:
        """Load translation memory and term base from files"""
        with open(os.path.join(input_dir, 'translation_memory.json'), 'r', encoding='utf-8') as f:
            tm_data = json.load(f)
            self.translation_memory = {
                k: {
                    **v,
                    'alternatives': set(v['alternatives'])
                } for k, v in tm_data.items()
            }
            
        with open(os.path.join(input_dir, 'term_base.json'), 'r', encoding='utf-8') as f:
            self.term_base = json.load(f)
    
    def _create_context(self, source_text: str) -> str:
        """Create context for Claude using translation memory and term base"""
        context = []
        
        # Add relevant terms from term base
        relevant_terms = [
            f"'{term}' → '{translation}'"
            for term, translation in self.term_base.items()
            if term.lower() in source_text.lower() and translation
        ]
        
        if relevant_terms:
            context.append("Key terms:")
            context.extend(relevant_terms)
        
        # Find similar segments from translation memory
        similar_segments = []
        for seg, data in self.translation_memory.items():
            if seg != source_text and data['target']:  # Only use segments with translations
                source_words = set(source_text.lower().split())
                seg_words = set(seg.lower().split())
                if len(source_words & seg_words) > 0:
                    similar_segments.append({
                        'segment': seg,
                        'translation': data['target'],
                        'overlap': len(source_words & seg_words) / len(source_words | seg_words)
                    })
        
        similar_segments.sort(key=lambda x: x['overlap'], reverse=True)
        if similar_segments[:3]:
            context.append("\nSimilar translated segments:")
            for seg in similar_segments[:3]:
                context.append(f"Source: {seg['segment']}\nTranslation: {seg['translation']}")
        
        return "\n".join(context)
    
    def translate_text(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Translate a single text segment using Claude"""
        # Check translation memory for exact match
        if source_text in self.translation_memory and self.translation_memory[source_text]['target']:
            return self.translation_memory[source_text]['target']
        
        # Create context for Claude
        context = self._create_context(source_text)
        
        # Create prompt for Claude
        prompt = f"""Please translate the following text from {source_lang} to {target_lang}, using the provided translation memory and term base as reference.

Context:
{context}

Text to translate:
{source_text}

Please maintain consistency with the provided translations while ensuring natural flow in the target language. Return only the translated text without any explanations or notes."""

        # Get translation from Claude
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        translation = message.content[0].text
        
        # Update translation memory
        if source_text in self.translation_memory:
            self.translation_memory[source_text]['target'] = translation
        
        return translation
    
    def translate_file(self, input_file: str, output_file: str, source_lang: str, target_lang: str) -> None:
        """Translate an Excel file including all sheets and cells"""
        print(f"Translating {input_file}...")
        
        # Read input file
        xlsx = pd.ExcelFile(input_file)
        
        # Create Excel writer for output
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Process each sheet
            for sheet_name in xlsx.sheet_names:
                print(f"\nProcessing sheet: {sheet_name}")
                
                # Read the sheet
                df = pd.read_excel(xlsx, sheet_name=sheet_name)
                
                # Create output DataFrame
                df_out = df.copy()
                
                # Get total number of cells for progress tracking
                total_cells = df.size
                processed_cells = 0
                skipped_cells = 0
                
                # Translate each cell in the sheet
                for col in df.columns:
                    for idx, cell_value in df[col].items():
                        # Check for empty cells first - multiple conditions for emptiness
                        if (pd.isna(cell_value) or  # Check for NaN
                            cell_value == "" or     # Empty string
                            str(cell_value).strip() == ""): # Whitespace only
                            df_out.at[idx, col] = cell_value  # Keep original empty value
                            processed_cells += 1
                            skipped_cells += 1
                            continue
                        
                        source_text = str(cell_value).strip()
                        
                        # Skip if cell contains only numbers
                        if str(cell_value).replace('.', '').replace('-', '').isdigit():
                            df_out.at[idx, col] = cell_value
                            processed_cells += 1
                            skipped_cells += 1
                            continue
                        
                        # Translate and store result
                        try:
                            translation = self.translate_text(source_text, source_lang, target_lang)
                            df_out.at[idx, col] = translation
                        except Exception as e:
                            print(f"Error translating cell [{idx}, {col}]: {str(e)}")
                            df_out.at[idx, col] = f"ERROR: {str(e)}"
                        
                        processed_cells += 1
                        
                        # Show progress every 10 cells
                        if processed_cells % 10 == 0:
                            progress = (processed_cells / total_cells) * 100
                            print(f"Progress: {processed_cells}/{total_cells} cells ({progress:.1f}%)")
                            print(f"Skipped {skipped_cells} empty or numeric cells")
                
                # Save the translated sheet
                df_out.to_excel(writer, sheet_name=sheet_name, index=False)
                
        print(f"Translation completed. Output saved to {output_file}")
        print(f"Total empty or numeric cells skipped: {skipped_cells}")

def main():
    # Configuration
    API_KEY = "AAA"  # Replace with your API key
    TRAINING_FILE = "training_data.xlsx"
    INPUT_FILE = "th_new_append_1101_totranslate.xlsx"
    OUTPUT_FILE = "th_new_append_1101_HB.xlsx"
    SOURCE_LANG = "Chinese"
    TARGET_LANG = "Thai"
    
    # Initialize translation system
    translator = TranslationSystem(API_KEY)
    
    # Build translation assets from training data
    translator.build_translation_assets(TRAINING_FILE)
    
    # Save assets for later use
    translator.save_assets("translation_assets")
    
    # Translate new file
    translator.translate_file(INPUT_FILE, OUTPUT_FILE, SOURCE_LANG, TARGET_LANG)

if __name__ == "__main__":
    main()