# app.py (Updated for Renamed Files and Folders)
import nest_asyncio
nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify
import asyncio
from ollama_backend import main as ollama_backend # Import from renamed backend file

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('templates/index.html') # Use renamed template folder and file

@app.route("/ask", methods=['POST'])
async def ask_ollama_expanded(): # Keep function name as ask_ollama_expanded (or rename to just ask_ollama if you prefer)
    user_question = request.form['question']
    expand_question = request.form.get('expand_question') == 'true'
    llm_response_text = ""
    scraped_webpages = []
    expanded_questions_list = []
    error_message = None

    use_scraping_param = expand_question

    llm_response_tuple = await ollama_backend(user_question, use_scraping=use_scraping_param)
    llm_response_text, error_message, scraped_webpages = llm_response_tuple

    if expand_question and not error_message and llm_response_tuple[0] is not None:
        expanded_questions_list = await get_expanded_questions_for_display(user_question)

    if error_message:
        return jsonify({'response': "Error: " + error_message, 'webpages': [], 'expanded_questions': [], 'error': error_message})
    else:
        return jsonify({'response': llm_response_text, 'webpages': scraped_webpages, 'expanded_questions': expanded_questions_list, 'error': None})


async def get_expanded_questions_for_display(user_question):
    expanded_questions = expand_question_with_ollama(user_question)
    if expanded_questions and expanded_questions != [user_question]:
        return expanded_questions[1:]
    return []

from ollama_backend import expand_question_with_ollama # Import from renamed backend file

if __name__ == '__main__':
    app.run(debug=True)