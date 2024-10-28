import pandas as pd
import requests
import json
from pathlib import Path
import time
import re

def preserve_special_chars(text):
    """
    Extract and preserve tags and newlines before translation
    """
    # Create placeholders for tags and newlines
    square_brackets = []
    angle_brackets = []
    newlines = []
    
    # Extract tags and newlines
    square_pattern = r'\[.*?\]'
    angle_pattern = r'<.*?>'
    newline_pattern = r'\\n'
    
    # Save square brackets
    square_matches = re.finditer(square_pattern, text)
    for i, match in enumerate(square_matches):
        square_brackets.append(match.group())
        text = text.replace(match.group(), f'[SQUARETAG{i}]')
    
    # Save angle brackets
    angle_matches = re.finditer(angle_pattern, text)
    for i, match in enumerate(angle_matches):
        angle_brackets.append(match.group())
        text = text.replace(match.group(), f'<ANGLETAG{i}>')
    
    # Save newlines
    newline_matches = re.finditer(newline_pattern, text)
    for i, match in enumerate(newline_matches):
        newlines.append(match.group())
        text = text.replace(match.group(), f'NEWLINE{i}')
    
    return text, square_brackets, angle_brackets, newlines

def restore_special_chars(text, square_brackets, angle_brackets, newlines):
    """
    Restore tags and newlines after translation
    """
    # Restore square brackets
    for i, tag in enumerate(square_brackets):
        text = text.replace(f'[SQUARETAG{i}]', tag)
    
    # Restore angle brackets
    for i, tag in enumerate(angle_brackets):
        text = text.replace(f'<ANGLETAG{i}>', tag)
    
    # Restore newlines
    for i, newline in enumerate(newlines):
        text = text.replace(f'NEWLINE{i}', '\\n')
    
    return text

def post_process_translation(text):
    """
    Post-process translated text to ensure proper newline handling
    """
    # Replace any actual newlines with \n
    text = text.replace('\r\n', '\\n')  # Handle Windows-style newlines
    text = text.replace('\n', '\\n')     # Handle Unix-style newlines
    
    # Remove any duplicate \n that might have been created
    text = re.sub(r'\\n\\n+', '\\n', text)
    
    # Ensure there's no whitespace around \n
    text = re.sub(r'\s*\\n\s*', '\\n', text)
    
    return text.strip()

def translate_text(text, model="qwen2.5:3b"):
    """
    Translate text using Ollama API while preserving tags and newlines
    """
    if not text or pd.isna(text):
        return text
    
    # Convert to string if not already
    text = str(text)
    
    # Preserve special characters
    preserved_text, square_brackets, angle_brackets, newlines = preserve_special_chars(text)
    
    # Prepare the prompt
    prompt = f"Translate the following text to English. Keep all formatting and spacing exactly as is. Return only translated text, no comment, no instruction, no additional context, nothing else: {preserved_text}"
    
    # Ollama API endpoint
    url = "http://localhost:11434/api/generate"
    
    # Request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        translated_text = result['response'].strip()
        
        # Restore special characters
        final_text = restore_special_chars(translated_text, square_brackets, angle_brackets, newlines)
        
        # Post-process to ensure proper newline handling
        final_text = post_process_translation(final_text)
        
        return final_text
    except Exception as e:
        print(f"Translation error for text '{text}': {str(e)}")
        return text

def validate_translation(text):
    """
    Validate the translation output to ensure proper formatting
    """
    if '\n' in text and '\\n' not in text:
        print(f"Warning: Found actual newline in translation. Converting to \\n")
        return post_process_translation(text)
    return text

def translate_excel(input_path, output_path, model="qwen2.5:3b"):
    """
    Translate the third column (column C) in an Excel file to English
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {input_path}")
        df = pd.read_excel(input_path)
        
        if len(df.columns) < 3:
            print("Excel file has fewer than 3 columns!")
            return False
        
        # Get the name of the third column
        third_column = df.columns[2]
        
        # Initialize progress tracking
        total_cells = len(df)
        processed_cells = 0
        
        # Process only the third column
        print("Translating third column (column C) contents...")
        for idx in df.index:
            cell_value = df.iloc[idx, 2]  # Access third column by index 2
            if isinstance(cell_value, (str, int, float)):
                # Translate the text
                translated_text = translate_text(cell_value, model)
                # Validate and fix if necessary
                translated_text = validate_translation(translated_text)
                df.iloc[idx, 2] = translated_text
                
            # Update progress
            processed_cells += 1
            if processed_cells % 10 == 0:  # Show progress every 10 cells
                progress = (processed_cells / total_cells) * 100
                print(f"Progress: {progress:.1f}% ({processed_cells}/{total_cells} cells)")
            
            # Add a small delay to prevent overwhelming the API
            time.sleep(0.1)
        
        # Save the translated file
        print(f"Saving translated file to: {output_path}")
        df.to_excel(output_path, index=False)
        print("Translation completed successfully!")
        
        return True
    
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        return False

def main():
    # Example usage
    input_file = "input_example.xlsx"
    output_file = "output_EN.xlsx"
    
    # Ensure Ollama is running and the model is available
    try:
        # Check if model exists
        response = requests.post("http://localhost:11434/api/show", 
                               json={"name": "qwen2.5:3b"})
        if response.status_code != 200:
            print("Please ensure the qwen2.5:3b model is pulled in Ollama.")
            print("Run: 'ollama pull qwen2.5:3b' first.")
            return
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Please ensure Ollama is running.")
        return
    
    # Translate the file
    if Path(input_file).exists():
        translate_excel(input_file, output_file)
    else:
        print(f"Input file '{input_file}' not found!")

if __name__ == "__main__":
    main()