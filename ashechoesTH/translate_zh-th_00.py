import pandas as pd
import requests
import time
from typing import Optional

def translate_text(text: str, api_url: str = "http://localhost:11434/api/generate") -> Optional[str]:
    """
    Translate text from Chinese to Thai using Ollama API
    """
    prompt = f"""Translate the following Chinese text to Thai:
    {text}
    Only return the Thai translation, nothing else."""
    
    try:
        response = requests.post(
            api_url,
            json={
                "model": "llama2:3b",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return None

def translate_excel_file(input_file: str, output_file: str, source_col: str = 'C', target_col: str = 'D'):
    """
    Read Excel file, translate content from source column to target column
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
                print(f"Translating row {idx + 1} of {total_rows}...")
                translation = translate_text(source_text)
                if translation:
                    df.at[idx, target_column] = translation
                # Add a small delay to avoid overwhelming the API
                time.sleep(1)
        
        # Save the translated file
        df.to_excel(output_file, index=False)
        print(f"Translation completed. Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_file = "input.xlsx"
    output_file = "output_translated.xlsx"
    
    # Make sure Ollama is running and the model is installed
    translate_excel_file(input_file, output_file)