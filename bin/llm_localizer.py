import pandas as pd
from ollama.translate import Translator
from tqdm import tqdm

# Function to localize sentences using Ollama
def localize_sentences(sentences):
    translator = Translator.from_pretrained("ollama/llama-3")
    localized_sentences = []
    for sentence in tqdm(sentences, desc="Localizing sentences"):
        localized_sentence = translator.translate(sentence, target_lang="en")
        localized_sentences.append(localized_sentence)
    return localized_sentences

# Read Excel file
def localize_excel_file(input_file, output_file):
    # Read Excel file
    df = pd.read_excel(input_file)
    
    # Extract English sentences from row A
    english_sentences = df['A']
    
    # Localize sentences
    localized_sentences = localize_sentences(english_sentences)
    
    # Add localized sentences to row B
    df['B'] = localized_sentences
    
    # Write localized data to output file
    df.to_excel(output_file, index=False)

# Example usage
input_file = "input.xlsx"
output_file = "output.xlsx"
localize_excel_file(input_file, output_file)
