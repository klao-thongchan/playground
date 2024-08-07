# app.py
from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text = request.json['text']
    
    # Use Ollama for translation
    prompt = f"Translate the following Chinese text to Thai: {text}"
    response = ollama.generate(model="your_translation_model", prompt=prompt)
    
    translated_text = response['response']
    
    return jsonify({'translation': translated_text})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)