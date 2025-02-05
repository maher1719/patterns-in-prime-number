# app.py
import nest_asyncio
#nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify
import asyncio
from your_ollama_script import query_ollama, expand_question_with_ollama  # Import only needed functions
import bleach # Import bleach

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ask", methods=['POST'])
async def ask_ollama():
    try:
        user_question = request.form['question']
        user_question = bleach.clean(user_question) # Sanitize!
        expand_checked = request.form.get('expand') == 'true' # Get checkbox state

        llm_response_text = ""
        expanded_questions_and_answers = [] # List to store expanded questions and answers

        if expand_checked: # If "Expand" checkbox is checked
            expanded_questions = expand_question_with_ollama(user_question) # Expand questions

            for q in expanded_questions:
                print(f"\n--- Answering Expanded Question to llama: '{q}' ---")
                expanded_answer = query_ollama(f"Answer for question with extreme rigor and as long as you can with in full comperhensive way {q}") # Get answer for each expanded question (NO SCRAPING)
                print(f"Answer for question with extreme rigor and as long as you can '{q}': {expanded_answer}")
                expanded_questions_and_answers.append({"question": q, "answer": expanded_answer}) # Store question and answer
            print(f"length expanded {len(expanded_questions_and_answers)}----------------")
            if len(expanded_questions_and_answers)>0:
                print("making general answers from previous")
                all_answers = "\n".join([item["answer"] for item in expanded_questions_and_answers])  # Build answers string
                synthesis_answer=query_ollama(f"please make hidden insights about this: {all_answers}")
                expanded_questions_and_answers.append({"question": "synthesise on previous responses", "answer": synthesis_answer})
                text_books=query_ollama(f"give best textbooks about the components of this : {all_answers}")
                expanded_questions_and_answers.append({"question": "textbooks", "answer": text_books})

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
    except Exception as e:
        print(f"Error in ask_ollama: {e}")
        return jsonify({
            'messages': [{"role": "bot", "content": "An error occurred. Please try again."}],
            'is_expanded': False,
            'filename': None
        }), 500


async def ask_ollama():
    try:
        user_question = request.form['question']
        user_question = bleach.clean(user_question)
        expand_checked = request.form.get('expand') == 'true'

        messages = []  # List to store *all* messages (user and bot)
        messages.append({"role": "user", "content": user_question})
        expanded_questions_and_answers = []

        if expand_checked:
            expanded_questions = expand_question_with_ollama(user_question)
            for q in expanded_questions:
                expanded_answer = query_ollama(f"Answer for question with extreme rigor and as long as you can {q}")
                expanded_questions_and_answers.append({"question": q, "answer": expanded_answer})
                messages.append({"role": "bot", "content": f"**Question:** {q}\n\n**Answer:** {expanded_answer}"}) # Bot answers both

            if len(expanded_questions_and_answers) > 0:
                all_answers = "\n".join([item["answer"] for item in expanded_questions_and_answers])  # Build answers string
                synthesis_answer = query_ollama(f"Synthesis on this provided answer rigorously and answer comprehensively as much as you can and elaborate on its components as much as you can: {all_answers}")
                expanded_questions_and_answers.append({"question": "Synthesis on previous responses", "answer": synthesis_answer})
                messages.append({"role": "bot", "content": f"**Synthesis:** {synthesis_answer}"})

        else:
            llm_response_text = query_ollama(user_question)
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


if __name__ == '__main__':
    app.run(
    debug=True, passthrough_errors=True,
    use_debugger=False, use_reloader=True
)