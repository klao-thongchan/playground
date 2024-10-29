import pandas as pd
from anthropic import Anthropic
import time
import requests
import json

# Replace this with your actual Anthropic API key
ANTHROPIC_API_KEY = ""

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def post_process_newlines(text):
    """
    Replace actual newlines with \n string
    """
    if text:
        # Replace any actual newlines with \n string
        return text.replace('\n', '\\n').replace('\r', '\\n')
    return text

def translate_with_ollama(text):
    """
    Translate text using Ollama's llama2 3B model
    """
    try:
        # Ollama API endpoint (default local installation)
        url = "http://localhost:11434/api/generate"
        
        # Prepare the prompt
        prompt = f"""Localize following text to Thai. 
Rules:
- Preserve all HTML tags and what is inside the brackets [] <> exactly as they appear. Do not localize or translate anything inside the brackets.
- Keep \n exactly as it is. Do not replace with enter the new line. Do not enter the new line.
- Maintain consistent translations for repeated terms. 
- Most important. Only return the Thai translation, nothing else.
- Do not add any line breaks or newlines in your response.

Text to Localize: {text}"""

        # Prepare the request payload
        payload = {
            "model": "llama2:3b",
            "prompt": prompt,
            "stream": False
        }

        # Make the request
        response = requests.post(url, json=payload)
        response_json = response.json()
        
        # Extract the translation
        translated_text = response_json.get('response', '').strip()
        
        # Post-process the translation
        processed_text = post_process_newlines(translated_text)
        
        return processed_text
        
    except Exception as e:
        print(f"Error translating with Ollama: {str(e)}")
        return None

def translate_with_claude(text):
    """
    Localize text to Thai using Claude while preserving tags.
    """
    try:
        message = f"""Localize following text to Thai. 
Rules:
- Preserve all HTML tags and what is inside the brackets [] <> exactly as they appear. Do not localize or translate anything inside the brackets.
- Keep \n exactly as it is. Do not replaced with enter the new line. Do not enter the new line.
- Maintain consistent translations for repeated terms. 
- Most important. Only return the Thai translation, nothing else.
- Do not add any line breaks or newlines in your response.

Text to Localize: {text}"""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        translated_text = response.content[0].text
        # Apply post-processing to handle any newlines
        processed_text = post_process_newlines(translated_text)
        return processed_text
        
    except Exception as e:
        print(f"Error translating with Claude: {str(e)}")
        return None

def process_excel(input_file, output_file):
    """
    Process Excel file and translate content from column C to columns D (Claude) and E (Ollama)
    """
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        
        # Create translation memory dictionaries for both models
        claude_memory = {}
        ollama_memory = {}
        
        # Process each row
        total_rows = len(df)
        for index in range(total_rows):
            try:
                # Get source text from column C
                source_text = str(df.iloc[index, 2])  # Column C is index 2
                
                # Skip empty cells
                if pd.isna(source_text) or source_text.strip() == '':
                    continue
                
                # Process with Claude
                if source_text in claude_memory:
                    claude_text = claude_memory[source_text]
                else:
                    claude_text = translate_with_claude(source_text)
                    if claude_text:
                        claude_memory[source_text] = claude_text
                
                # Process with Ollama
                if source_text in ollama_memory:
                    ollama_text = ollama_memory[source_text]
                else:
                    ollama_text = translate_with_ollama(source_text)
                    if ollama_text:
                        ollama_memory[source_text] = ollama_text
                
                # Store translations
                if claude_text:
                    df.iloc[index, 3] = claude_text  # Column D is index 3
                if ollama_text:
                    df.iloc[index, 4] = ollama_text  # Column E is index 4
                
                # Print progress
                print(f"\nProcessed row {index + 1}/{total_rows}")
                print(f"Source: {source_text}")
                print(f"Claude Translation: {claude_text}")
                print(f"Ollama Translation: {ollama_text}")
                
                # Add delay to avoid API rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing row {index + 1}: {str(e)}")
                continue
        
        # Save the result
        df.to_excel(output_file, index=False)
        print(f"\nTranslation completed. Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")

if __name__ == "__main__":
    # File paths
    input_file = "input_example.xlsx"  # Replace with your input file path
    output_file = "output_dual_translation.xlsx"  # Replace with your desired output file path
    
    # Process the file
    process_excel(input_file, output_file)