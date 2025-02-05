#your_ollama_script.py
import nest_asyncio
nest_asyncio.apply()

import requests  # Keep requests import for Ollama API fallback (if needed)
import json
import asyncio
import os

# --- Configuration ---
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")


# --- Ollama Query Function ---

def query_ollama(prompt, model_name=OLLAMA_MODEL):
    """Queries a local Ollama model."""
    try:
        import ollama
        response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except ImportError:
        import requests
        api_url = "http://localhost:11434/api/chat"
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error querying Ollama: {e}")
        return "Error communicating with Ollama."

# --- Question Expansion Function ---
def expand_question_with_ollama(question, num_questions=5):
    """Expands the initial question using Ollama, generating a specified number of related questions."""
    expansion_prompt = f"""Please expand on the question: "{question}".
Generate {num_questions} additional questions that are meaningful, delve deeper into the subject incrementally, and are related to the original question.
Return the original question and the {num_questions + 1} expanded questions as a JSON array of strings.

Example JSON output (if num_questions is 3):
[
  "{question}",
  "Question 1",
  "Question 2",
  "Question 3"
]

Only output the JSON array."""
    print("\nExpanding question with Ollama...")
    try:
        json_response = query_ollama(expansion_prompt)
        print(f"Ollama Question Expansion Response: {json_response}")

        try:
            expanded_questions = json.loads(json_response)
            if isinstance(expanded_questions, list):
                print(f"Expanded Questions (Parsed as JSON array): {expanded_questions}")
                return expanded_questions
            else:
                print(f"Warning: Parsed JSON, but not a list. Unexpected format. Raw response: {json_response}")
                return [question]

        except json.JSONDecodeError as json_err:
            print(f"JSON Decode Error: {json_err}.  Falling back to original question.")
            return [question]

    except Exception as e:
        print(f"Error during question expansion: {e}. Falling back to original question.")
        return [question]

# --- Main Function --- (For testing your_ollama_script.py independently) ---
async def main(user_question):
    # user_question = input("Ask me anything: ") # No input here for web interface

    # --- Expand the question using Ollama ---
    expanded_questions = expand_question_with_ollama(user_question)

    expanded_questions_and_answers = [] # List to store expanded questions and answers
    for q in expanded_questions:
        print(f"\n--- Answering Expanded Question to llama: '{q}' ---")
        expanded_answer = query_ollama(f"Answer for question with extreme rigor and as long as you can {q}") # Get answer for each expanded question (NO SCRAPING)
        print(f"Answer for question with extreme rigor and as long as you can '{q}': {expanded_answer}")
        expanded_questions_and_answers.append({"question": q, "answer": expanded_answer}) # Store question and answer
    print(f"length expanded {len(expanded_questions_and_answers)}----------------")
    if len(expanded_questions_and_answers)>0:
        print("making general answers from previous")
        all_answers = "\n".join([item["answer"] for item in expanded_questions_and_answers])  # Build answers string
        synthesis_answer=query_ollama(f"Synthesis on this provided answer rigorously and answer comperhensivly as much as you can and elaborate on its compoponents as much as you can: {all_answers}")
        expanded_questions_and_answers.append({"question": "synthesise on previous responses", "answer": synthesis_answer})

    # For simplicity, for final answer, let's just use the answer to the original question (first in expanded list)
    llm_response = expanded_questions_and_answers[0]['answer'] if expanded_questions_and_answers else "No expanded answers generated." # Fallback if no expanded answers


    print("\n--- Final Response from Ollama ---")
    print(llm_response)

    return llm_response, None, [] # Return response, no error message, EMPTY webpages list

if __name__ == "__main__":
    user_input_question = input("Ask me anything: ")
    response, error_msg, webpages = asyncio.run(main(user_input_question)) # webpages will always be empty
    if error_msg:
        print(f"Error: {error_msg}")
    elif response:
        print("\n--- Final Response: ---")
        print(response)