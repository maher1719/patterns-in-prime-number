# app.py (Corrected save_conversation_to_file and /ask route)

import nest_asyncio
nest_asyncio.apply()

from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
from your_ollama_script import query_ollama, expand_question_with_ollama
import bleach
import os
import datetime
import re
import sqlite3

app = Flask(__name__)

# --- Database Setup ---
DB_PATH = 'conversations.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_question TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES threads (thread_id)
            )
        """)
        conn.commit()
init_db()

def get_thread_messages(thread_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM messages WHERE thread_id = ? ORDER BY message_id", (thread_id,))
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def create_thread(user_question):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (user_question) VALUES (?)", (user_question,))
        thread_id = cursor.lastrowid
        conn.commit()
        return thread_id

def add_message(thread_id, role, content):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, role, content))
        conn.commit()


def get_previous_messages_string(thread_id):
    messages = get_thread_messages(thread_id)
    formatted_messages = ""
    for message in messages:
        formatted_messages += f"{message['role']}: {message['content']}\n"
    return formatted_messages

def get_all_threads():
    """Retrieves all threads for the sidebar."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id, user_question, timestamp FROM threads ORDER BY timestamp DESC")
        return [{"id": row[0], "user_question": row[1], "timestamp": row[2]} for row in cursor.fetchall()]

# --- Helper Functions ---
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_conversation_to_file(thread_id):
    """Saves the conversation from the database to a text file."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Get the original user question from the threads table
        cursor.execute("SELECT user_question, timestamp FROM threads WHERE thread_id = ?", (thread_id,))
        user_question, timestamp = cursor.fetchone()  # Fetch the result
        if user_question is None or timestamp is None:  # Add this check
            print(f"Error: Could not find thread with ID {thread_id}")
            return None

        timestamp_str = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d_%H%M%S")

        safe_question = sanitize_filename(user_question)
        filename = f"{safe_question}_{timestamp_str}.txt"
        filepath = os.path.join("conversations", filename)
        os.makedirs("conversations", exist_ok=True)

        # Get all messages associated with the thread
        cursor.execute("SELECT role, content FROM messages WHERE thread_id = ? ORDER BY message_id", (thread_id,))
        messages = cursor.fetchall()


    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Original Question: {user_question}\n\n")
        for role, content in messages:
            if role == 'user':
                f.write(f"Question: {content}\n")
            else:
                if "Question:" in content:
                    f.write(f"{content}\n")
                else:
                    f.write(f"Answer: {content}\n\n")
    return filename

# --- Routes ---

@app.route("/")
def index():
    threads = get_all_threads()
    return render_template('index.html', threads=threads, current_thread_id=None, filename=None)

@app.route("/thread/<int:thread_id>")
def get_thread(thread_id):
    messages = get_thread_messages(thread_id)
    threads = get_all_threads()
    filename = save_conversation_to_file(thread_id) #get the file name for download

    formatted_messages = []
    for message in messages:
      formatted_content = message['content']

      formatted_messages.append({
          "role": message["role"],
          "content": formatted_content,
      })

    return render_template('index.html', messages=formatted_messages, threads=threads, current_thread_id=thread_id, filename=filename)


@app.route("/ask", methods=['POST'])
async def ask_ollama():
    try:
        user_question = request.form['question']
        user_question = bleach.clean(user_question)
        expand_checked = request.form.get('expand') == 'true'
        num_questions = request.form.get('num_questions', type=int, default=5)
        summarize_checked = request.form.get('summarize') == 'true'
        textbooks_checked = request.form.get('textbooks') == 'true'
        more_questions_checked = request.form.get('more_questions') == 'true'
        current_thread_id = request.form.get('current_thread_id', type=int)

        if current_thread_id:
            thread_id = current_thread_id
            add_message(thread_id, "user", user_question)
        else:
            thread_id = create_thread(user_question)
            add_message(thread_id, "user", user_question)

        messages = []
        messages.append({"role": "user", "content": user_question})
        expanded_questions_and_answers = []
        previous_messages_context = get_previous_messages_string(thread_id)

        if expand_checked:
            expanded_questions = expand_question_with_ollama(user_question, num_questions)
            for q in expanded_questions:
                print(f"answering question {q}")
                prompt = f" Answer for question with extreme rigor and as long as you can: {q}. "
                #prompt = f"{previous_messages_context} Answer for question with extreme rigor and as long as you can: {q}"
                expanded_answer = query_ollama(prompt)
                expanded_questions_and_answers.append({"question": q, "answer": expanded_answer})
                add_message(thread_id, "bot", f"Question: {q}\nAnswer: {expanded_answer}")
                messages.append({"role": "bot", "content": f"**Question:** {q}\n\n**Answer:** {expanded_answer}"})
                previous_messages_context = get_previous_messages_string(thread_id)

            if len(expanded_questions_and_answers) > 0:
                all_answers = "\n".join([item["answer"] for item in expanded_questions_and_answers])

                if summarize_checked:
                    print("answering summerization")
                    prompt = f"Summarize the text into an essay considering all the points and relating them together if it possible : {all_answers}"
                    #prompt = f"{previous_messages_context}Summarize the text into an essay considering all the points and relating them together if it possible : {all_answers}"

                    synthesis_answer = query_ollama(prompt)
                    expanded_questions_and_answers.append({"question": "Summary", "answer": synthesis_answer})
                    add_message(thread_id, "bot", f"Summary: {synthesis_answer}")
                    messages.append({"role": "bot", "content": f"**Summary:** {synthesis_answer}"})
                    previous_messages_context = get_previous_messages_string(thread_id)

                if textbooks_checked:
                    print("answering textbooks")
                    prompt = f"Suggest best textbooks on the topics in this text?: {all_answers}"
                    textbooks_answer = query_ollama(prompt)
                    expanded_questions_and_answers.append({"question": "Textbook Recommendations", "answer": textbooks_answer})
                    add_message(thread_id, "bot", f"Textbook Recommendations: {textbooks_answer}")
                    messages.append({"role": "bot", "content": f"**Textbook Recommendations:** {textbooks_answer}"})
                    previous_messages_context = get_previous_messages_string(thread_id)

                if more_questions_checked:
                    print("answering more questions")
                    prompt = f"Provide questions in the topics in this text that will deepen the understanding and link to other related topics?: {all_answers}"
                    more_questions_answer = query_ollama(prompt)
                    expanded_questions_and_answers.append({"question": "Further Questions", "answer": more_questions_answer})
                    add_message(thread_id, "bot", f"Further Questions: {more_questions_answer}")
                    messages.append({"role": "bot", "content": f"**Further Questions:** {more_questions_answer}"})
                    previous_messages_context = get_previous_messages_string(thread_id)
        else:
            prompt = f"Answer this with great rigor and in a comprehensive way as long as you can: {user_question}. if the answer contains any math notations wrap the math in $...$ for inline or $$...$$ Obligatory!!."
            llm_response_text = query_ollama(prompt)
            add_message(thread_id, "bot", llm_response_text)
            messages.append({"role": "bot", "content": llm_response_text})
            expanded_questions_and_answers.append({"question": user_question, "answer": llm_response_text})

        filename = save_conversation_to_file(thread_id)

        return jsonify({
            'messages': messages,
            'is_expanded': expand_checked,
            'filename': filename,
            'thread_id': thread_id
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
    return send_from_directory("conversations", filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)