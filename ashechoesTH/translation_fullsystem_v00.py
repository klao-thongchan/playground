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
        Build translation memory and term base from training data
        
        Args:
            training_file: Excel file with historical translations (B: source, C: target)
        """
        print("Building translation assets...")
        
        # Read training data
        df = pd.read_excel(training_file)
        
        # Process each translation pair
        for _, row in df.iterrows():
            source = str(row['B']).strip()
            target = str(row['C']).strip()
            
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
            
            # Add to term base if it meets criteria:
            # - 1-3 words
            # - Appears at least 3 times
            # - Consistent translation (no alternatives)
            words = source.split()
            if (1 <= len(words) <= 3 and 
                self.translation_memory[source]['frequency'] >= 3 and
                len(self.translation_memory[source]['alternatives']) == 0):
                self.term_base[source] = target
        
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
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content
    
    def translate_file(self, input_file: str, output_file: str, source_lang: str, target_lang: str) -> None:
        """Translate an Excel file"""
        print(f"Translating {input_file}...")
        
        # Read input file
        df = pd.read_excel(input_file)
        
        # Create output DataFrame
        df_out = df.copy()
        
        # Translate each row
        total_rows = len(df)
        for idx, row in df.iterrows():
            source_text = str(row['B']).strip()
            
            # Skip empty or invalid entries
            if pd.isna(source_text) or not source_text:
                df_out.at[idx, 'C'] = ''
                continue
            
            # Translate and store result
            try:
                translation = self.translate_text(source_text, source_lang, target_lang)
                df_out.at[idx, 'C'] = translation
            except Exception as e:
                print(f"Error translating row {idx + 1}: {str(e)}")
                df_out.at[idx, 'C'] = f"ERROR: {str(e)}"
            
            # Show progress
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{total_rows} rows")
        
        # Save output file
        df_out.to_excel(output_file, index=False)
        print(f"Translation completed. Output saved to {output_file}")

def main():
    # Configuration
    API_KEY = "your_anthropic_api_key"  # Replace with your API key
    TRAINING_FILE = "training_data.xlsx"
    INPUT_FILE = "to_translate.xlsx"
    OUTPUT_FILE = "translated_output.xlsx"
    SOURCE_LANG = "English"
    TARGET_LANG = "Spanish"  # Change as needed
    
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