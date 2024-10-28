import pandas as pd
from anthropic import Anthropic
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
anthropic = Anthropic(
    api_key=os.getenv('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')
)

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

        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system="You are a professional translator specializing in Chinese to Thai translation.",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Error translating text: {e}")
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
            
            # Print progress
            print(f"Processed row {index + 1}/{total_rows}")
            
            # Add delay to avoid API rate limits
            time.sleep(0.5)
        
        # Save the result
        df.to_excel(output_file, index=False)
        print(f"Translation completed. Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")

if __name__ == "__main__":
    # File paths
    input_file = "input_example.xlsx"  # Replace with your input file path
    output_file = "output_claude.xlsx"  # Replace with your desired output file path
    
    # Process the file
    process_excel(input_file, output_file)