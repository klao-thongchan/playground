import pandas as pd
import requests
import time
import re
from typing import Optional

def preserve_special_content(text: str) -> tuple[str, list, list, list]:
    """
    Extract and preserve content within brackets and tags
    """
    # Store original special content
    square_brackets = re.findall(r'\[.*?\]', text)
    angle_brackets = re.findall(r'<.*?>', text)
    newlines = re.findall(r'\\n', text)
    
    # Replace with placeholders
    text = re.sub(r'\[.*?\]', '[BRACKET]', text)
    text = re.sub(r'<.*?>', '<TAG>', text)
    text = re.sub(r'\\n', 'NEWLINE', text)
    
    return text, square_brackets, angle_brackets, newlines

def restore_special_content(text: str, square_brackets: list, angle_brackets: list, newlines: list) -> str:
    """
    Restore preserved content back into the translated text
    """
    for bracket in square_brackets:
        text = text.replace('[BRACKET]', bracket, 1)
    for tag in angle_brackets:
        text = text.replace('<TAG>', tag, 1)
    for newline in newlines:
        text = text.replace('NEWLINE', '\\n', 1)
    return text

def translate_text(text: str, api_url: str = "http://localhost:11434/api/generate") -> Optional[str]:
    """
    Localize text from Chinese to Thai using Ollama API while preserving special content
    """
    # Preserve special content before translation
    modified_text, square_brackets, angle_brackets, newlines = preserve_special_content(text)
    
    prompt = f"""As a professional Thai localizer, localize the following Chinese text to Thai. 
    Make sure the translation is natural and culturally appropriate for Thai audience.
    
    Rules:
    1. Keep formatting elements exactly as is: [BRACKET], <TAG>, and NEWLINE
    2. Ensure the Thai text flows naturally
    3. Consider Thai cultural context
    4. Maintain the original meaning and tone
    5. Only return the Thai localized text, nothing else
    
    Text to localize:
    {modified_text}"""
    
    try:
        response = requests.post(
            api_url,
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        translated_text = response.json()["response"].strip()
        
        # Restore special content in the translated text
        final_text = restore_special_content(translated_text, square_brackets, angle_brackets, newlines)
        return final_text
    except Exception as e:
        print(f"Error localizing text: {str(e)}")
        return None

def translate_excel_file(input_file: str, output_file: str, source_col: str = 'C', target_col: str = 'D'):
    """
    Read Excel file, localize content from source column to target column
    """
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        
        # Get the source column name (convert letter to index)
        source_column = df.columns[ord(source_col.upper()) - ord('A')]
        
        # Create new column for translations if it doesn't exist
        target_column = df.columns[ord(target_col.upper()) - ord('A')] if len(df.columns) > ord(target_col.upper()) - ord('A') else target_col
        df[target_column] = ""
        
        # Translate each cell
        total_rows = len(df)
        for idx, row in df.iterrows():
            source_text = str(row[source_column])
            if source_text and source_text.strip():
                print(f"Localizing row {idx + 1} of {total_rows}...")
                translation = translate_text(source_text)
                if translation:
                    df.at[idx, target_column] = translation
                # Add a small delay to avoid overwhelming the API
                time.sleep(1)
        
        # Save the translated file
        df.to_excel(output_file, index=False)
        print(f"Localization completed. Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_file = "input_example.xlsx"
    output_file = "output_localized.xlsx"
    
    # Make sure Ollama is running and the model is installed
    translate_excel_file(input_file, output_file)