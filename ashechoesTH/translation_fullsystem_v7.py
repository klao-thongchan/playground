import pandas as pd
import openai
from typing import Dict, Tuple, List
import os
import re
import json
import time

class TranslationSystem:
    def __init__(self, api_key: str, training_file: str, input_file: str, output_file: str, save_interval: int = 100):
        """Initialize translation system with OpenAI's GPT-4o-mini"""
        self.api_key = api_key
        self.training_file = training_file
        self.input_file = input_file
        self.output_file = output_file
        self.save_interval = save_interval
        self.translation_memory = {}
        self.term_base = {}
        self.training_data_buffer = []
        
    def build_translation_assets(self):
        """
        Build translation memory and term base from training data with improved term base criteria
        """
        print("Building translation assets...")
        
        # Read training data - use None for header to get column letters
        df = pd.read_excel(self.training_file, header=None)
        
        # Dictionary to track term frequencies and translations
        term_candidates = {}
        
        # Process each translation pair
        for idx, row in df.iterrows():
            zh_text = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None  # Column B is index 1
            en_text = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None  # Column C is index 2
            th_text = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None  # Column D is index 3
            
            # Skip invalid entries
            if not zh_text or not th_text:
                continue
            
            # Add to translation memory
            if zh_text in self.translation_memory:
                self.translation_memory[zh_text]['frequency'] += 1
                if th_text != self.translation_memory[zh_text]['target']:
                    self.translation_memory[zh_text]['alternatives'].add(th_text)
            else:
                self.translation_memory[zh_text] = {
                    'target': th_text,
                    'frequency': 1,
                    'alternatives': set()
                }
                
            # Add English to translation memory if available
            if en_text and en_text != "N/A":
                if en_text in self.translation_memory:
                    self.translation_memory[en_text]['frequency'] += 1
                    if th_text != self.translation_memory[en_text]['target']:
                        self.translation_memory[en_text]['alternatives'].add(th_text)
                else:
                    self.translation_memory[en_text] = {
                        'target': th_text,
                        'frequency': 1,
                        'alternatives': set()
                    }
            
            # Process terms for term base
            for source_text in [zh_text, en_text]:
                if not source_text or source_text == "N/A":
                    continue
                    
                words = source_text.split()
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
                        if th_text not in term_candidates[term]['translations']:
                            term_candidates[term]['translations'][th_text] = 0
                        term_candidates[term]['translations'][th_text] += 1
        
        # Build term base with improved criteria
        for term, data in term_candidates.items():
            # Criteria for including in term base:
            # 1. Term appears at least once
            # 2. Has a dominant translation (used >50% of the time)
            # 3. Term is between 1 and 500 characters
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
    
    def _create_context(self, zh_text: str, en_text: str) -> str:
        """Create context for translation using translation memory and term base"""
        context = []
        
        # Add relevant terms from term base for both Chinese and English
        relevant_terms = []
        
        for source_text in [zh_text, en_text]:
            if not source_text or source_text == "N/A":
                continue
                
            for term, translation in self.term_base.items():
                if term.lower() in source_text.lower():
                    relevant_terms.append(f"'{term}' → '{translation}'")
        
        if relevant_terms:
            context.append("Key terms:")
            context.extend(relevant_terms)
        
        # Find similar segments from translation memory
        similar_segments = []
        
        for source_text in [zh_text, en_text]:
            if not source_text or source_text == "N/A":
                continue
                
            for seg, data in self.translation_memory.items():
                if seg != source_text:  # Don't include exact matches
                    # Check for word overlap
                    source_words = set(source_text.lower().split())
                    seg_words = set(seg.lower().split())
                    overlap = len(source_words & seg_words)
                    if overlap > 0:
                        similar_segments.append({
                            'segment': seg,
                            'translation': data['target'],
                            'overlap': overlap / len(source_words | seg_words)
                        })
        
        # Sort by overlap and take top 3
        similar_segments.sort(key=lambda x: x['overlap'], reverse=True)
        if similar_segments[:3]:
            context.append("\nSimilar translated segments:")
            for seg in similar_segments[:3]:
                context.append(f"Source: {seg['segment']}\nTranslation: {seg['translation']}")
        
        return "\n".join(context)
    
    def contains_chinese(self, text):
        """Check if a string contains Chinese characters."""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def update_training_data(self, zh_text, en_text, th_text):
        """Buffer new translations to be saved to training data."""
        self.training_data_buffer.append([zh_text, en_text, th_text])
        print(f"Added to training data buffer: {zh_text} -> {th_text}")
    
    def save_training_data_buffer(self):
        """Save accumulated translations from buffer to training data file."""
        if not self.training_data_buffer:
            return
            
        try:
            # Read existing training data
            try:
                df = pd.read_excel(self.training_file)
            except FileNotFoundError:
                # Create a new dataframe if file doesn't exist
                df = pd.DataFrame(columns=['Chinese', 'English', 'Thai'])
            
            # Create a dataframe from buffer
            buffer_df = pd.DataFrame(self.training_data_buffer, columns=['Chinese', 'English', 'Thai'])
            
            # Concatenate with existing data
            df = pd.concat([df, buffer_df], ignore_index=True)
            
            # Create backup of existing file if it exists
            training_file_base = os.path.splitext(self.training_file)[0]
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_file = f"{training_file_base}_backup_{timestamp}.xlsx"
            
            if os.path.exists(self.training_file):
                os.rename(self.training_file, backup_file)
                print(f"Created backup of training data: {backup_file}")
            
            # Save to file
            df.to_excel(self.training_file, index=False)
            print(f"Saved {len(self.training_data_buffer)} entries to training data")
            
            # Clear buffer
            self.training_data_buffer = []
        except Exception as e:
            print(f"Error saving training data: {str(e)}")

    def translate_text(self, zh_text: str, en_text: str, retries=3) -> str:
        """Translate text using OpenAI GPT-4o-mini with contextual integration, limiting retries"""
        if retries <= 0:
            print(f"Error: Unable to fully translate '{zh_text}'. Returning last attempt.")
            return "[Translation Unavailable]"
            
        # Check translation memory for exact match
        if zh_text in self.translation_memory:
            return self.translation_memory[zh_text]['target']
        if en_text and en_text in self.translation_memory:
            return self.translation_memory[en_text]['target']
        
        # Create context for translation
        context = self._create_context(zh_text, en_text)

        prompt = f"""
        Translate the following in-game text into Thai, ensuring it accurately reflects the tone, style, and meaning while maintaining a natural reading experience.
        
        **Localization Rules:**
        - Prioritize **game-specific terminology** from established translations where available.
        - Adapt cultural references appropriately for Thai players while preserving the original intent.
        - Maintain consistency in naming conventions, character dialogue styles, and tone.
        - **Do not transliterate** names unless necessary, prefer localized naming conventions.
        - Ensure commands, UI texts, and short labels are concise and intuitive.
        - Avoid unnecessary punctuation, and do **not** end sentences with a period (".") unless grammatically required.
        - **IMPORTANT**: Every single Chinese character MUST be translated. If a character or phrase has no meaningful translation, provide the Thai pronunciation instead.
        
        **Translation Context:**
        {context}
        
        **Translation Priorities:**
        1. **Use the English source if both Chinese and English are available**, as it may provide clearer context.
        2. If **English is missing**, rely on the Chinese text for meaning.
        3. If a character or term has no meaning or is unfamiliar, provide the Thai phonetic pronunciation instead of leaving Chinese characters.
        
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
        
        # Buffer the translation for later saving
        self.update_training_data(zh_text, en_text, translated_text)
        
        return translated_text
    
    def process_translation(self):
        """Process localization from input file and save to output file at regular intervals."""
        print("Processing translation...")
        
        try:
            df = pd.read_excel(self.input_file)
        except Exception as e:
            print(f"Error reading input file: {str(e)}")
            return
            
        total_rows = len(df)
        localized_count = 0
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create timestamped backup filename for auto-saves
        output_file_base = os.path.splitext(self.output_file)[0]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_pattern = f"{output_file_base}_autosave"
        
        start_time = time.time()
        for idx in range(len(df)):
            try:
                zh_text = str(df.iloc[idx, 1]).strip() if pd.notna(df.iloc[idx, 1]) else ""
                en_text = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
                
                # Skip if we already have a translation
                if pd.notna(df.iloc[idx, 12]) and df.iloc[idx, 12]:
                    print(f"Row {idx+1}: Translation already exists, skipping")
                    localized_count += 1
                    continue
                
                translated_text = self.translate_text(zh_text, en_text)
                df.at[idx, 12] = translated_text  # Output to column M (index 12)
                localized_count += 1
                
                # Calculate and display progress
                progress = (localized_count / total_rows) * 100
                elapsed_time = time.time() - start_time
                items_per_second = localized_count / elapsed_time if elapsed_time > 0 else 0
                estimated_remaining = (total_rows - localized_count) / items_per_second if items_per_second > 0 else "unknown"
                
                print(f"Progress: {progress:.2f}% ({localized_count}/{total_rows}) | "
                      f"Speed: {items_per_second:.2f} items/sec | "
                      f"Est. remaining: {estimated_remaining if isinstance(estimated_remaining, str) else f'{estimated_remaining:.2f} sec'}")
                
                # Periodically save progress
                if localized_count % self.save_interval == 0:
                    # Create a backup with timestamp for this autosave
                    autosave_file = f"{backup_pattern}_{timestamp}_{localized_count}.xlsx"
                    df.to_excel(autosave_file, index=False)
                    print(f"Autosaved progress to: {autosave_file}")
                    
                    # Save the training data buffer
                    self.save_training_data_buffer()
                    
                    # Update the term base and save assets
                    if localized_count % (self.save_interval * 5) == 0:
                        self.build_translation_assets()
                        self.save_assets("translation_assets")
            
            except Exception as e:
                print(f"Error processing row {idx+1}: {str(e)}")
                # Save on error to prevent data loss
                error_save_file = f"{output_file_base}_error_at_row_{idx+1}.xlsx"
                df.to_excel(error_save_file, index=False)
                print(f"Saved progress before error to: {error_save_file}")
        
        # Final save
        df.to_excel(self.output_file, index=False)
        self.save_training_data_buffer()
        print("Translation complete. Output saved to:", self.output_file)
        
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
        
        # Create backups of existing files
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        tm_file = os.path.join(output_dir, 'translation_memory.json')
        tb_file = os.path.join(output_dir, 'term_base.json')
        
        if os.path.exists(tm_file):
            os.rename(tm_file, os.path.join(output_dir, f'translation_memory_backup_{timestamp}.json'))
        
        if os.path.exists(tb_file):
            os.rename(tb_file, os.path.join(output_dir, f'term_base_backup_{timestamp}.json'))
        
        with open(tm_file, 'w', encoding='utf-8') as f:
            json.dump(tm_for_save, f, ensure_ascii=False, indent=2)
            
        with open(tb_file, 'w', encoding='utf-8') as f:
            json.dump(self.term_base, f, ensure_ascii=False, indent=2)
            
        print(f"Saved translation assets to {output_dir}")
    
    def load_assets(self, input_dir: str) -> None:
        """Load translation memory and term base from files"""
        try:
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
                
            print(f"Loaded translation memory with {len(self.translation_memory)} entries")
            print(f"Loaded term base with {len(self.term_base)} entries")
        except Exception as e:
            print(f"Error loading assets: {str(e)}")
            print("Building assets from training data instead...")
            self.build_translation_assets()

# Usage
api_key = "SECRET"
translator = TranslationSystem(
    api_key=api_key, 
    training_file="training_data.xlsx", 
    input_file="1st_th-en_new_append_0226.xlsx", 
    output_file="1st_th_new_append_0226_output_fix_v3.xlsx",
    save_interval=100  # Save every 100 rows
)

# Either load existing assets or build from training data
try:
    translator.load_assets("translation_assets")
except:
    translator.build_translation_assets()
    # Save assets for future use
    translator.save_assets("translation_assets")

translator.process_translation()