import pandas as pd
from anthropic import Anthropic
import time

# Replace this with your actual Anthropic API key
ANTHROPIC_API_KEY = "y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"  # Replace this line with your actual API key

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def translate_text(text):
    """
    Localize text from Chinese to Thai using Claude while preserving HTML tags and special characters
    """
    try:
        message = f"""Localize the following Chinese text to Thai. 
Rules:
1. Preserve all HTML tags and what is inside the brackets [] <> exactly as they appear
2. Keep \n characters exactly as they appear
3. Maintain consistent translations for repeated terms
4. Only return the Thai translation, nothing else

Text to Localize: {text}"""

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Error translating text: {str(e)}")
        return None

def process_excel(input_file, output_file):
    """
    Process Excel file and translate content from column C to column D
    """
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        
        # Create translation memory dictionary for consistency
        translation_memory = {}
        
        # Process each row
        total_rows = len(df)
        for index in range(total_rows):
            try:
                # Get source text from column C
                source_text = str(df.iloc[index, 2])  # Column C is index 2
                
                # Skip empty cells
                if pd.isna(source_text) or source_text.strip() == '':
                    continue
                    
                # Check translation memory first
                if source_text in translation_memory:
                    translated_text = translation_memory[source_text]
                else:
                    # Translate text
                    translated_text = translate_text(source_text)
                    
                    # Store in translation memory if translation successful
                    if translated_text:
                        translation_memory[source_text] = translated_text
                    
                # Store translation in column D
                if translated_text:
                    df.iloc[index, 3] = translated_text  # Column D is index 3
                
                # Print progress and source/target text for verification
                print(f"\nProcessed row {index + 1}/{total_rows}")
                print(f"Source: {source_text}")
                print(f"Translation: {translated_text}")
                
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
    output_file = "output_claude.xlsx"  # Replace with your desired output file path
    
    # Process the file
    process_excel(input_file, output_file)