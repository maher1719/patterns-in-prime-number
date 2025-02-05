# app.py
import nest_asyncio
nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
from your_ollama_script import query_ollama, expand_question_with_ollama
import bleach
import os
import datetime
import re

app = Flask(__name__)

# --- Helper Functions ---

def sanitize_filename(filename):
    """Sanitizes a filename for safe storage."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_conversation(user_question, expanded_questions_and_answers):
    """Saves the conversation to a text file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_question = sanitize_filename(user_question)
    filename = f"{safe_question}_{timestamp}.txt"
    filepath = os.path.join("conversations", filename)

    os.makedirs("conversations", exist_ok=True)  # Ensure the directory exists

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Original Question: {user_question}\n\n")
        for qa in expanded_questions_and_answers:
            f.write(f"Question: {qa['question']}\n")
            f.write(f"Answer: {qa['answer']}\n\n")

    return filename  # Return the filename for later use (if needed)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ask", methods=['POST'])
async def ask_ollama():
    try:
        user_question = request.form['question']
        user_question = bleach.clean(user_question)
        expand_checked = request.form.get('expand') == 'true'

        messages = []  # List to store *all* messages (user and bot)
        messages.append({"role": "user", "content": user_question})
        expanded_questions_and_answers = []

        if expand_checked:
            # need how many questions be asked in number input
            expanded_questions = expand_question_with_ollama(user_question)
            
            for q in expanded_questions:
                print(f"\n--- Answering Expanded Question to llama: '{q}' ---")
                expanded_answer = query_ollama(f"Answer for question with extreme rigor and as long as you can {q}")
                expanded_questions_and_answers.append({"question": q, "answer": expanded_answer})
                messages.append({"role": "bot", "content": f"**Question:** {q}\n\n**Answer:** {expanded_answer}"}) # Bot answers both

            if len(expanded_questions_and_answers) > 0:
                #options will be made only if checkbox "expand" is checked
                print("making general answers from previous")
                # need option for summary
                all_answers = "\n".join([item["answer"] for item in expanded_questions_and_answers])  # Build answers string
                synthesis_answer = query_ollama(f"Summerize the text into an essay considering all the points and relating them together: {all_answers}")
                expanded_questions_and_answers.append({"question": "Synthesis on previous responses", "answer": synthesis_answer})
                messages.append({"role": "bot", "content": f"**Synthesis:** {synthesis_answer}"})
                print("Answering textbooks")
                # need option for textbooks
                synthesis_answer = query_ollama(f"suggest best textbooks on the topics in this text?: {all_answers}")
                expanded_questions_and_answers.append({"question": "more resources", "answer": synthesis_answer})
                messages.append({"role": "bot", "content": f"**More resources:** {synthesis_answer}"})
                print("more questions")
                # need option for questions
                synthesis_answer = query_ollama(f"Provide questions in the topics in this text that will deepen the understanding and link to other related topics?: {all_answers}")
                expanded_questions_and_answers.append({"question": "more resources", "answer": synthesis_answer})
                messages.append({"role": "bot", "content": f"**More resources:** {synthesis_answer}"})
        else:
            llm_response_text = query_ollama(f"Answer this with great rigor and comperhensive way as long as you can: {user_question}")
            messages.append({"role": "bot", "content": llm_response_text})
            expanded_questions_and_answers.append({"question":user_question, "answer":llm_response_text})

        # Save the conversation
        filename = save_conversation(user_question, expanded_questions_and_answers)


        return jsonify({
            'messages': messages, # Send all messages for unified chat
            'is_expanded': expand_checked,
            'filename': filename  # Send filename (optional - could be used for a download link)
        })

    except Exception as e:
        print(f"Error in ask_ollama: {e}")
        return jsonify({
            'messages': [{"role": "bot", "content": "An error occurred. Please try again."}],
            'is_expanded': False,
            'filename': None
        }), 500



@app.route('/download/<filename>')
def download_file(filename):
    """Allows downloading of conversation files."""
    return send_from_directory("conversations", filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)