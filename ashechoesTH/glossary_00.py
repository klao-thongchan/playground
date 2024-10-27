import pandas as pd
from langchain_community.llms import Ollama
import sqlite3
from tqdm import tqdm
import re

def setup_database():
    """Create SQLite database to store translation pairs"""
    conn = sqlite3.connect('translation_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            source_text TEXT PRIMARY KEY,
            target_text TEXT,
            frequency INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    return conn

def is_short_chinese_text(text, max_chars=10):
    """Check if text is Chinese and within character limit"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    if not chinese_pattern.search(str(text)):
        return False
    return len(str(text)) <= max_chars

def process_excel_file(input_file, output_file):
    """Main function to process Excel file and create glossary"""
    # Initialize Ollama
    llm = Ollama(model="llama2:3b")
    
    # Connect to database
    conn = setup_database()
    cursor = conn.cursor()
    
    # Read input Excel file
    try:
        df = pd.read_excel(input_file)
        source_texts = df.iloc[:, 1]  # Column B
        target_texts = df.iloc[:, 2]  # Column C
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    # Process translations and store in database
    glossary_entries = []
    
    for source, target in tqdm(zip(source_texts, target_texts), total=len(source_texts)):
        if pd.isna(source) or pd.isna(target):
            continue
            
        # Check if text meets criteria (short Chinese text)
        if is_short_chinese_text(source):
            # Check if translation already exists in database
            cursor.execute('SELECT target_text, frequency FROM translations WHERE source_text = ?', (source,))
            result = cursor.fetchone()
            
            if result:
                # Update frequency if exists
                cursor.execute('''
                    UPDATE translations 
                    SET frequency = frequency + 1 
                    WHERE source_text = ?
                ''', (source,))
                if result[0] == target:  # If same translation, add to glossary
                    glossary_entries.append({'source': source, 'target': target})
            else:
                # Add new translation to database
                cursor.execute('''
                    INSERT INTO translations (source_text, target_text) 
                    VALUES (?, ?)
                ''', (source, target))
                glossary_entries.append({'source': source, 'target': target})
    
    conn.commit()
    
    # Create output Excel file
    if glossary_entries:
        output_df = pd.DataFrame(glossary_entries)
        output_df.columns = ['Source', 'Target']
        output_df.to_excel(output_file, index=False)
        print(f"Glossary created successfully with {len(glossary_entries)} entries")
    else:
        print("No suitable entries found for glossary")
    
    conn.close()

if __name__ == "__main__":
    input_file = "input.xlsx"  # Replace with your input file path
    output_file = "glossary.xlsx"  # Replace with desired output file path
    process_excel_file(input_file, output_file)