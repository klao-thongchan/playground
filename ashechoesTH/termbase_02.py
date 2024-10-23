import pandas as pd
from openpyxl import load_workbook
import requests
import json
from tqdm import tqdm
import jieba
import re
import os

def is_valid_term(term):
    """
    Check if a term is valid for term base
    - Not just numbers
    - Not just punctuation
    - Has some minimum length
    """
    if len(term.strip()) < 2:
        return False
    
    # Check if term contains only numbers and punctuation
    if re.match(r'^[\d\s.,!?;:"\'\-\(\)]+$', term):
        return False
    
    # Check if term contains at least one Chinese or Thai character
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', term))
    has_thai = bool(re.search(r'[\u0e00-\u0e7f]', term))
    
    return has_chinese or has_thai

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
    Returns a list of valid terms
    """
    # Check if text contains Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text):
        # Use jieba for Chinese text
        terms = list(jieba.cut(text, cut_all=False))
        
        # Get combinations of terms
        combined_terms = []
        for i in range(len(terms)):
            current_term = terms[i]
            if len(current_term.strip()) >= min_length and is_valid_term(current_term):
                combined_terms.append(current_term)
            
            # Try combining with next terms
            current_combo = current_term
            for j in range(i + 1, min(i + 3, len(terms))):
                current_combo += terms[j]
                if len(current_combo) <= max_length and is_valid_term(current_combo):
                    combined_terms.append(current_combo)
        
        return list(set(combined_terms))  # Remove duplicates
    
    # For Thai text
    elif re.search(r'[\u0e00-\u0e7f]', text):
        # Split by spaces and common Thai delimiters
        basic_terms = re.findall(r'\S+', text)
        
        combined_terms = []
        for i in range(len(basic_terms)):
            current_term = basic_terms[i]
            if len(current_term) >= min_length and is_valid_term(current_term):
                combined_terms.append(current_term)
            
            # Try combining with next terms
            current_combo = current_term
            for j in range(i + 1, min(i + 3, len(basic_terms))):
                current_combo = ' '.join([current_combo, basic_terms[j]])
                if len(current_combo) <= max_length and is_valid_term(current_combo):
                    combined_terms.append(current_combo)
        
        return list(set(combined_terms))  # Remove duplicates
    
    return []

def create_term_base(input_file, output_file, confidence_threshold=70):
    """
    Create terminology base using LLM verification
    """
    # Read input Excel file
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return None
    
    # Initialize term base entries
    term_base_entries = []
    
    print("Processing translations...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        try:
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
        except Exception as e:
            print(f"Error processing row {idx}: {str(e)}")
            continue
    
    # Create term base DataFrame
    if not term_base_entries:
        print("No valid term pairs found")
        return None
        
    term_base_df = pd.DataFrame(term_base_entries)
    
    # Remove duplicates, keeping highest confidence entries
    term_base_df = term_base_df.sort_values('Confidence', ascending=False)
    term_base_df = term_base_df.drop_duplicates(subset=['Source (Chinese)', 'Target (Thai)'])
    
    # Save to Excel
    try:
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
    except Exception as e:
        print(f"Error saving term base: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    INPUT_FILE = "translations.xlsx"
    OUTPUT_FILE = "term_base.xlsx"
    
    # Add custom terms to jieba
    jieba.add_word("同调者收集")
    jieba.add_word("เอคโคแมนเซอร์")
    
    term_base = create_term_base(
        INPUT_FILE, 
        OUTPUT_FILE, 
        confidence_threshold=70
    )