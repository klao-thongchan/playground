import os
import pandas as pd
import openai
from openai import OpenAI

# Setup OpenAI client
client = OpenAI(api_key="YOUR_API_KEY")

# Path to your Downloads folder
downloads_path = os.path.expanduser("~/Downloads/")
file_name = "your_file.xlsx"  # replace with your actual filename
file_path = os.path.join(downloads_path, file_name)

# Define function to check if cell needs translation
def needs_translation(cell):
    if pd.isna(cell):
        return False
    if isinstance(cell, (int, float)) or (isinstance(cell, str) and cell.strip().isdigit()):
        return False
    return True

# Translation function using OpenAI
def translate_to_thai(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Mini variant assumed available
            messages=[
                {"role": "system", "content": "You are a translator that converts Chinese to Thai."},
                {"role": "user", "content": f"Translate this from Chinese to Thai: {text}"},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error translating text: {text}\n{e}")
        return text

# Read Excel with all sheets
sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

# Process each sheet
writer = pd.ExcelWriter(file_path.replace(".xlsx", "_translated.xlsx"), engine="openpyxl")
for sheet_name, df in sheets.items():
    df_copy = df.copy()
    for col_index in range(0, 11):  # Columns A to K
        col_name = df.columns[col_index]
        for row_index, value in df[col_name].items():
            if needs_translation(value):
                translated = translate_to_thai(str(value))
                df_copy.at[row_index, col_name] = translated
    df_copy.to_excel(writer, sheet_name=sheet_name, index=False)

writer.save()
print("Translation complete. Saved new file with '_translated' suffix.")
