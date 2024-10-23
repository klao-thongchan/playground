import pandas as pd
from collections import defaultdict
import re
import openpyxl
from datetime import datetime

# Create sample Term Base with 10 rows (example terms for technology domain)
sample_terms = {
    'Chinese': [
        '点击',
        '下载',
        '保存',
        '用户名',
        '密码',
        '登录',
        '注册',
        '确认',
        '取消',
        '设置'
    ],
    'Thai': [
        'คลิก',
        'ดาวน์โหลด',
        'บันทึก',
        'ชื่อผู้ใช้',
        'รหัสผ่าน',
        'เข้าสู่ระบบ',
        'ลงทะเบียน',
        'ยืนยัน',
        'ยกเลิก',
        'ตั้งค่า'
    ]
}

# Create initial Term Base
def create_sample_termbase(output_file='termbase_sample.xlsx'):
    df = pd.DataFrame(sample_terms)
    df.to_excel(output_file, index=False)
    print(f"Sample Term Base created: {output_file}")

def extract_phrases(text, min_length=2, max_length=6):
    """Extract phrases from text based on common delimiters"""
    words = re.split(r'[,.\s]+', str(text))
    phrases = []
    
    for i in range(len(words)):
        for j in range(i + min_length, min(i + max_length + 1, len(words) + 1)):
            phrase = ' '.join(words[i:j])
            if len(phrase.strip()) > 0:
                phrases.append(phrase)
    
    return phrases

def analyze_translations(input_file, min_occurrences=3):
    """Analyze translation file to find consistent phrase pairs"""
    df = pd.read_excel(input_file)
    
    # Dictionary to store phrase pairs and their frequencies
    phrase_pairs = defaultdict(int)
    
    for idx, row in df.iterrows():
        zh_phrases = extract_phrases(row['Chinese'])
        th_phrases = extract_phrases(row['Thai'])
        
        for zh in zh_phrases:
            for th in th_phrases:
                phrase_pairs[(zh.strip(), th.strip())] += 1
    
    # Filter consistent pairs
    consistent_pairs = {
        pair: count for pair, count in phrase_pairs.items()
        if count >= min_occurrences
    }
    
    return consistent_pairs

def append_to_termbase(termbase_file, new_pairs):
    """Append new term pairs to existing termbase"""
    try:
        existing_df = pd.read_excel(termbase_file)
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=['Chinese', 'Thai'])
    
    new_terms = pd.DataFrame(
        [(zh, th) for (zh, th) in new_pairs.keys()],
        columns=['Chinese', 'Thai']
    )
    
    # Remove duplicates
    combined_df = pd.concat([existing_df, new_terms]).drop_duplicates()
    combined_df.to_excel(termbase_file, index=False)

# Create sample termbase
create_sample_termbase()

# Usage example:
"""
# To process a translation file and update termbase:
input_file = 'translations.xlsx'
termbase_file = 'termbase.xlsx'

consistent_pairs = analyze_translations(input_file)
append_to_termbase(termbase_file, consistent_pairs)
"""