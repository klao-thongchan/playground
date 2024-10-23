import pandas as pd
from openpyxl import load_workbook
import requests
import json
from tqdm import tqdm
import re
import os

def extract_phrases(text, min_length=2, max_length=6):
    """
    Extract phrases from text using basic word count boundaries
    Returns list of phrases that are between min_length and max_length words
    """
    # Split text into words while preserving Chinese characters
    words = re.findall(r'[\u4e00-\u9fff]+|[^\s]+', text)
    phrases = []
    
    for i in range(len(words)):
        for j in range(i + min_length, min(i + max_length + 1, len(words) + 1)):
            phrase = ' '.join(words[i:j])
            phrases.append(phrase)
            
    return phrases

def get_llama_translation(text, source_lang="Chinese", target_lang="Thai"):
    """
    Get translation suggestion from local Llama model via Ollama API
    """
    prompt = f"Translate this {source_lang} phrase to {target_lang}: {text}\n\nTranslation:"
    
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "llama3.2:3b",
                                   "prompt": prompt,
                                   "stream": False
                               })
        response.raise_for_status()
        result = response.json()
        return result['response'].strip()
    except Exception as e:
        print(f"Error getting translation for '{text}': {str(e)}")
        return None

def create_term_base(input_file, output_file, min_occurrences=2):
    """
    Create terminology base from translated Excel file
    """
    # Read input Excel file
    df = pd.read_excel(input_file)
    
    # Initialize phrase counters
    phrase_pairs = {}
    
    print("Analyzing phrases...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        source_text = str(row[0])  # Chinese text
        target_text = str(row[1])  # Thai text
        
        # Extract phrases from source text
        source_phrases = extract_phrases(source_text)
        
        for source_phrase in source_phrases:
            # Get translation suggestion from Llama
            suggested_translation = get_llama_translation(source_phrase)
            
            if suggested_translation:
                # If translation appears in target text, count the pair
                if suggested_translation.lower() in target_text.lower():
                    pair = (source_phrase, suggested_translation)
                    phrase_pairs[pair] = phrase_pairs.get(pair, 0) + 1
    
    # Filter pairs that appear multiple times
    consistent_pairs = {k: v for k, v in phrase_pairs.items() if v >= min_occurrences}
    
    # Create term base DataFrame
    term_base_data = {
        'Source (Chinese)': [pair[0] for pair in consistent_pairs.keys()],
        'Target (Thai)': [pair[1] for pair in consistent_pairs.keys()],
        'Occurrences': list(consistent_pairs.values())
    }
    
    term_base_df = pd.DataFrame(term_base_data)
    
    # Sort by occurrence count
    term_base_df = term_base_df.sort_values('Occurrences', ascending=False)
    
    # Save to Excel
    if os.path.exists(output_file):
        # If file exists, append to it
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            start_row = writer.sheets['Sheet1'].max_row
            term_base_df.to_excel(writer, index=False, startrow=start_row)
    else:
        # Create new file
        term_base_df.to_excel(output_file, index=False)
    
    print(f"Term base created with {len(term_base_df)} entries")
    return term_base_df

# Example usage
if __name__ == "__main__":
    INPUT_FILE = "translations.xlsx"  # Your input file with translations
    OUTPUT_FILE = "term_base.xlsx"    # Output term base file
    
    term_base = create_term_base(INPUT_FILE, OUTPUT_FILE, min_occurrences=2)