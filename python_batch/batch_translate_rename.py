import os
import subprocess
import json

def translate_filename(filename, model="qwen2:7b"):
    # Remove the file extension for translation
    name_without_ext = os.path.splitext(filename)[0]
    
    # Prepare the prompt for translation
    prompt = f"Translate the following filename from Chinese to English, maintaining the meaning: {name_without_ext}"
    
    # Run ollama command
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True
    )
    
    # Extract the translated text from the output
    translated_name = result.stdout.strip()
    
    # Replace spaces with underscores
    translated_name = translated_name.replace(" ", "_")
    
    return translated_name

def rename_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            # Get the full path of the file
            old_file = os.path.join(folder_path, filename)
            
            # Translate the filename
            new_name = translate_filename(filename)
            
            # Add the .jpg extension back
            new_name = f"{new_name}.jpg"
            
            # Create the new file path
            new_file = os.path.join(folder_path, new_name)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f"Renamed: {filename} -> {new_name}")

# Specify the folder path here
folder_path = "/Users/klao/Downloads/Card JPG/SSR Card"

# Run the renaming function
rename_files(folder_path)