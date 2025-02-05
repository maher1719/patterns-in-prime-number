import nest_asyncio
nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify
import asyncio
from your_ollama_script import query_ollama, expand_question_with_ollama # Import only needed functions

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ask", methods=['POST'])
async def ask_ollama():
    user_question = request.form['question']
    expand_checked = request.form.get('expand') == 'true' # Get checkbox state

    llm_response_text = ""
    expanded_questions_and_answers = [] # List to store expanded questions and answers

    if expand_checked: # If "Expand" checkbox is checked
        expanded_questions = expand_question_with_ollama(user_question) # Expand questions

        for q in expanded_questions:
            print(f"\n--- Answering Expanded Question: '{q}' ---")
            expanded_answer = query_ollama(q) # Get answer for each expanded question (NO SCRAPING)
            print(f"Answer for '{q}': {expanded_answer}")
            expanded_questions_and_answers.append({"question": q, "answer": expanded_answer}) # Store question and answer

        # For simplicity, for final answer, let's just use the answer to the original question (first in expanded list)
        llm_response_text = expanded_questions_and_answers[0]['answer'] if expanded_questions_and_answers else "No expanded answers generated." # Fallback if no expanded answers
    else: # If "Expand" is NOT checked - direct answer
        print(f"\n--- Answering Directly: '{user_question}' ---")
        llm_response_text = query_ollama(user_question) # Direct answer (NO SCRAPING)
        print(f"Direct Answer: {llm_response_text}")


    return jsonify({
        'response': llm_response_text,
        'expanded_questions_and_answers': expanded_questions_and_answers if expand_checked else [], # Only send if expand was checked
        'is_expanded': expand_checked, # Send flag to frontend
        'webpages': [] # Webpages will ALWAYS be empty now
    })

if __name__ == '__main__':
    app.run(debug=True)