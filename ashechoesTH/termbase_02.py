import pandas as pd
from openpyxl import load_workbook
import requests
import json
from tqdm import tqdm
import jieba  # For Chinese word segmentation
import re
import os

def segment_chinese(text):
    """
    Segment Chinese text into meaningful words/phrases using jieba
    """
    segments = jieba.cut(text, cut_all=False)
    return list(segments)

def is_valid_term(term):
    """
    Check if a term is valid for term base
    - Not just numbers
    - Not just punctuation
    - Has some minimum length
    """
    if len(term.strip()) < 2:
        return False
    if re.match(r'^[\d\s\p{P}]+$', term, re.UNICODE):
        return False
    return True

def get_llm_verification(source_term, target_term, context=""):
    """
    Use LLama to verify if source and target terms are equivalent
    Returns confidence score and explanation
    """
    prompt = f"""Task: Verify if these terms are equivalent translations between Chinese and Thai.
Source (Chinese): {source_term}
Target (Thai): {target_term}
Context: {context}

Answer these questions:
1. Are these terms equivalent translations? (Yes/No)
2. Confidence score (0-100)
3. Brief explanation

Format: JSON with keys: equivalent (boolean), confidence (integer), explanation (string)"""

    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "llama2:3b",
                                   "prompt": prompt,
                                   "stream": False
                               })
        response.raise_for_status()
        result = response.json()['response']
        
        # Parse the response as JSON
        try:
            analysis = json.loads(result)
            return analysis
        except json.JSONDecodeError:
            # Fallback parsing if LLM doesn't return valid JSON
            if 'yes' in result.lower():
                return {'equivalent': True, 'confidence': 70, 'explanation': result}
            return {'equivalent': False, 'confidence': 30, 'explanation': result}
            
    except Exception as e:
        print(f"Error in LLM verification: {str(e)}")
        return {'equivalent': False, 'confidence': 0, 'explanation': str(e)}

def extract_candidate_terms(text, min_length=2, max_length=20):
    """
    Extract potential terms from text
    """
    # For Chinese text
    if re.search(r'[\u4e00-\u9fff]', text):
        terms = segment_chinese(text)
        # Also get longer combinations
        combined_terms = []
        for i in range(len(terms)):
            current_term = terms[i]
            if is_valid_term(current_term):
                combined_terms.append(current_term)
            for j in range(i + 1, min(i + 3, len(terms))):
                combined_term = ''.join(terms[i:j+1])
                if is_valid_term(combined_term):
                    combined_terms.append(combined_term)
        return combined_terms
    
    # For Thai text
    else:
        # Split by spaces and common Thai delimiters
        terms = re.findall(r'\S+', text)
        combined_terms = []
        for i in range(len(terms)):
            current_term = terms[i]
            if is_valid_term(current_term):
                combined_terms.append(current_term)
            for j in range(i + 1, min(i + 3, len(terms))):
                combined_term = ' '.join(terms[i:j+1])
                if is_valid_term(combined_term):
                    combined_terms.append(combined_term)
        return combined_terms

def create_term_base(input_file, output_file, confidence_threshold=70):
    """
    Create terminology base using LLM verification
    """
    # Read input Excel file
    df = pd.read_excel(input_file)
    
    # Initialize term base entries
    term_base_entries = []
    
    print("Processing translations...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        source_text = str(row[0])  # Chinese text
        target_text = str(row[1])  # Thai text
        
        # Extract candidate terms from both source and target
        source_candidates = extract_candidate_terms(source_text)
        target_candidates = extract_candidate_terms(target_text)
        
        # Cross-verify promising pairs
        for source_term in source_candidates:
            for target_term in target_candidates:
                # Skip very short or very long terms
                if len(source_term) < 2 or len(target_term) < 2:
                    continue
                if len(source_term) > 20 or len(target_term) > 20:
                    continue
                
                # Use LLM to verify the pair
                verification = get_llm_verification(
                    source_term, 
                    target_term,
                    context=f"From translation pair: {source_text} → {target_text}"
                )
                
                # If confident enough, add to term base
                if (verification['equivalent'] and 
                    verification['confidence'] >= confidence_threshold):
                    term_base_entries.append({
                        'Source (Chinese)': source_term,
                        'Target (Thai)': target_term,
                        'Confidence': verification['confidence'],
                        'Explanation': verification['explanation']
                    })
    
    # Create term base DataFrame
    term_base_df = pd.DataFrame(term_base_entries)
    
    # Remove duplicates, keeping highest confidence entries
    term_base_df = term_base_df.sort_values('Confidence', ascending=False)
    term_base_df = term_base_df.drop_duplicates(subset=['Source (Chinese)', 'Target (Thai)'])
    
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
    
    # Add custom terms to jieba
    jieba.add_word("同调者收集")
    jieba.add_word("เอคโคแมนเซอร์")
    
    term_base = create_term_base(
        INPUT_FILE, 
        OUTPUT_FILE, 
        confidence_threshold=70
    )