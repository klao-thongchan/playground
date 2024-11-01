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
        """
        Build translation memory and term base from training data with improved term base criteria
        
        Args:
            training_file: Excel file with historical translations (col B: source, col C: target)
        """
        print("Building translation assets...")
        
        # Read training data - use None for header to get column letters
        df = pd.read_excel(training_file, header=None)
        
        # Dictionary to track term frequencies and translations
        term_candidates = {}
        
        # Process each translation pair
        for idx, row in df.iterrows():
            source = str(row.iloc[1]).strip()  # Column B is index 1
            target = str(row.iloc[2]).strip()  # Column C is index 2
            
            # Skip invalid entries
            if pd.isna(source) or pd.isna(target) or not source or not target:
                continue
            
            # Add to translation memory
            if source in self.translation_memory:
                self.translation_memory[source]['frequency'] += 1
                if target != self.translation_memory[source]['target']:
                    self.translation_memory[source]['alternatives'].add(target)
            else:
                self.translation_memory[source] = {
                    'target': target,
                    'frequency': 1,
                    'alternatives': set()
                }
            
            # Process terms for term base
            words = source.split()
            # Check phrases of 1-4 words
            for n in range(1, min(5, len(words) + 1)):
                for i in range(len(words) - n + 1):
                    term = ' '.join(words[i:i+n])
                    
                    # Skip if term is too short
                    if len(term) < 2:  # Skip single characters
                        continue
                        
                    if term not in term_candidates:
                        term_candidates[term] = {
                            'translations': {},
                            'frequency': 0
                        }
                    
                    term_candidates[term]['frequency'] += 1
                    if target not in term_candidates[term]['translations']:
                        term_candidates[term]['translations'][target] = 0
                    term_candidates[term]['translations'][target] += 1
        
        # Build term base with improved criteria
        for term, data in term_candidates.items():
            # Criteria for including in term base:
            # 1. Term appears at least twice
            # 2. Has a dominant translation (used >50% of the time)
            # 3. Term is between 2 and 30 characters
            if (data['frequency'] >= 1 and 
                1 <= len(term) <= 500 and
                len(term.split()) <= 100):
                
                # Find the most common translation
                most_common_translation = max(
                    data['translations'].items(),
                    key=lambda x: x[1]
                )
                
                # Calculate what percentage this translation represents
                translation_percentage = (
                    most_common_translation[1] / data['frequency']
                ) * 100
                
                # Add to term base if the translation is used more than 50% of the time
                if translation_percentage >= 50:
                    self.term_base[term] = most_common_translation[0]
        
        print(f"Built translation memory with {len(self.translation_memory)} entries")
        print(f"Built term base with {len(self.term_base)} entries")
        
    def save_assets(self, output_dir: str) -> None:
        """Save translation memory and term base to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert sets to lists for JSON serialization
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
            # Convert alternatives back to sets
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
            if term.lower() in source_text.lower()
        ]
        
        if relevant_terms:
            context.append("Key terms:")
            context.extend(relevant_terms)
        
        # Find similar segments from translation memory
        similar_segments = []
        for seg, data in self.translation_memory.items():
            if seg != source_text:  # Don't include exact matches
                # Check for word overlap
                source_words = set(source_text.lower().split())
                seg_words = set(seg.lower().split())
                if len(source_words & seg_words) > 0:
                    similar_segments.append({
                        'segment': seg,
                        'translation': data['target'],
                        'overlap': len(source_words & seg_words) / len(source_words | seg_words)
                    })
        
        # Sort by overlap and take top 3
        similar_segments.sort(key=lambda x: x['overlap'], reverse=True)
        if similar_segments[:3]:
            context.append("\nSimilar translated segments:")
            for seg in similar_segments[:3]:
                context.append(f"Source: {seg['segment']}\nTranslation: {seg['translation']}")
        
        return "\n".join(context)
    
    def translate_text(self, source_text: str, source_lang: str, target_lang: str) -> str:
        """Translate a single text segment using Claude"""
        # Check translation memory for exact match
        if source_text in self.translation_memory:
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
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def translate_file(self, input_file: str, output_file: str, source_lang: str, target_lang: str) -> None:
        """Translate an Excel file"""
        print(f"Translating {input_file}...")
        
        # Read input file without headers
        df = pd.read_excel(input_file, header=None)
        
        # Create output DataFrame
        df_out = df.copy()
        
        # Translate each row
        total_rows = len(df)
        for idx, row in df.iterrows():
            source_text = str(row.iloc[1]).strip()  # Column B is index 1
            
            # Skip empty or invalid entries
            if pd.isna(source_text) or not source_text:
                df_out.iloc[idx, 2] = ''  # Column C is index 2
                continue
            
            # Translate and store result
            try:
                translation = self.translate_text(source_text, source_lang, target_lang)
                df_out.iloc[idx, 2] = translation  # Column C is index 2
            except Exception as e:
                print(f"Error translating row {idx + 1}: {str(e)}")
                df_out.iloc[idx, 2] = f"ERROR: {str(e)}"
            
            # Show progress
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{total_rows} rows")
        
        # Save output file
        df_out.to_excel(output_file, index=False, header=False)
        print(f"Translation completed. Output saved to {output_file}")

def main():
    # Configuration
    API_KEY = "aaa"  # Replace with your API key
    TRAINING_FILE = "training_data.xlsx"
    INPUT_FILE = "th_append_1101_totranslate.xlsx"
    OUTPUT_FILE = "translated_output.xlsx"
    SOURCE_LANG = "Chinese"
    TARGET_LANG = "Thai"  # Change as needed
    
    # Initialize translation system
    translator = TranslationSystem(API_KEY)
    
    # Build translation assets from training data
    translator.build_translation_assets(TRAINING_FILE)
    
    # Optionally save assets for later use
    translator.save_assets("translation_assets")
    
    # Translate new file
    translator.translate_file(INPUT_FILE, OUTPUT_FILE, SOURCE_LANG, TARGET_LANG)

if __name__ == "__main__":
    main()