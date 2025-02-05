# app.py (Flask Backend - Corrected JSON Response for Captcha Fallback)
import nest_asyncio
nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify
import asyncio
from questions import main as ollama_backend

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ask", methods=['POST'])
async def ask_ollama():
    user_question = request.form['question']
    llm_response_text = ""
    scraped_webpages = []
    error_message = None

    llm_response_tuple = await ollama_backend(user_question, use_scraping=True)
    llm_response_text, error_message, scraped_webpages = llm_response_tuple

    if error_message: # Handle potential error message from backend
        # --- Corrected: Use error_message ONLY for the 'error' key ---
        return jsonify({'response': llm_response_text, 'webpages': [], 'expanded_questions': [], 'error': error_message}) # Empty response, webpages, expanded_questions, but include error
    else:
        # --- Corrected: Use llm_response_text for the 'response' key ---
        return jsonify({'response': llm_response_text, 'webpages': scraped_webpages, 'expanded_questions': [], 'error': None}) # Return LLM response, webpages, no error
        

if __name__ == '__main__':
    app.run(debug=True)