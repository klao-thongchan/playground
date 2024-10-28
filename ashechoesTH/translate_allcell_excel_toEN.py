import pandas as pd
import requests
import json
from pathlib import Path
import time

def translate_text(text, model="qwen2.5:3b"):
    """
    Translate text using Ollama API
    """
    if not text or pd.isna(text):
        return text
    
    # Convert to string if not already
    text = str(text)
    
    # Prepare the prompt
    prompt = f"Translate the following text to English, Return only translated text, no comment, no instruction, no additioncal context, nothing else: {text}"
    
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
        return result['response'].strip()
    except Exception as e:
        print(f"Translation error for text '{text}': {str(e)}")
        return text

def translate_excel(input_path, output_path, model="qwen2.5:3b"):
    """
    Translate all cells in an Excel file to English
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {input_path}")
        df = pd.read_excel(input_path)
        
        # Store original column names
        original_columns = df.columns.tolist()
        
        # Translate column names
        print("Translating column names...")
        translated_columns = [translate_text(col, model) for col in original_columns]
        df.columns = translated_columns
        
        # Initialize progress tracking
        total_cells = df.size
        processed_cells = 0
        
        # Process each cell in the DataFrame
        print("Translating cell contents...")
        for column in df.columns:
            for idx in df.index:
                cell_value = df.at[idx, column]
                if isinstance(cell_value, (str, int, float)):
                    df.at[idx, column] = translate_text(cell_value, model)
                    
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