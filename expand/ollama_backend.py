import nest_asyncio
nest_asyncio.apply()

import requests
import json
import asyncio

# --- Configuration ---
OLLAMA_MODEL = "llama3:3b"  # Or your desired Ollama model
USE_SCRAPING = False  # Keep USE_SCRAPING False as we are now in no-scraping mode

# --- Search Engine Functions (REMOVED) ---
# --- Website Content Scraping Function (REMOVED) ---


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

# --- Question Expansion Function (NO CHANGES) ---
def expand_question_with_ollama(question): # No changes needed here - always expand
    """Expands the initial question using Ollama to generate related deeper questions."""
    expansion_prompt = f"""Please expand on the question: "{question}".
Generate 5 additional questions that are meaningful, delve deeper into the subject incrementally, and are related to the original question.
Ensure that each expanded question is a maximum of 6 words long, while preserving its meaning and relevance.
Return the original question and the 5 expanded questions as a JSON array of strings.

Example JSON output:
[
  "{question}",
  "Question 1 (max 6 words)",
  "Question 2 (max 6 words)",
  "Question 3 (max 6 words)",
  "Question 4 (max 6 words)",
  "Question 5 (max 6 words)"
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
                print(f"Warning: Parsed JSON, but not a list (array). Unexpected format. Raw response: {json_response}")
                return [question]

        except json.JSONDecodeError as json_err:
            print(f"JSON Decode Error: {json_err}. Raw response was: {json_response}. Falling back to original question.")
            return [question]

    except Exception as e:
        print(f"Error during question expansion with Ollama: {e}. Falling back to original question.")
        return [question]

# --- Main Function (MODIFIED to use expand_question parameter) ---
async def main(user_question, expand_question=False): # Added expand_question parameter, defaults to False
    # global USE_SCRAPING # No longer need to modify global USE_SCRAPING - controlled by parameter

    # --- Expand the question using Ollama (always happens now) ---
    expanded_questions = expand_question_with_ollama(user_question)

    all_scraped_content = "" # No scraping, content is always empty
    scraped_webpages = [] # No scraping, webpages always empty
    captcha_detected = False # Not relevant as no scraping

    # --- Prepare Prompt for LLM (Conditional on expand_question) ---
    if expand_question: # Use prompt with expanded questions if checkbox checked
        questions_for_prompt = ""
        for i, q in enumerate(expanded_questions):
            questions_for_prompt += f"{i+1}. {q}\n"

        final_prompt_for_llm = f"""Answer the following question based on your knowledge, considering these related questions for a more comprehensive answer:

Questions to consider:
--- Questions ---
{questions_for_prompt}
--- End Questions ---

Question to answer: {user_question}
Give a comprehensive and detailed answer."""

    else: # Simpler prompt if expand_question is False (checkbox unchecked)
        final_prompt_for_llm = f"""Answer the question: '{user_question}' directly based on your knowledge.
Give a comprehensive and detailed answer."""


    print("\nSending to Ollama for final answer...")
    llm_response = query_ollama(final_prompt_for_llm)
    print("\n--- Final Response from Ollama ---")
    print(llm_response)

    return llm_response, None, scraped_webpages # Return response, no error, empty webpages


if __name__ == "__main__":
    user_input_question = input("Ask me anything: ")
    response, error_msg, webpages = asyncio.run(main(user_input_question, expand_question=True)) # Test with expand_question=True for direct script run
    if error_msg:
        print(f"Error: {error_msg}")
    elif response:
        print("\n--- Final Response: ---")
        print(response)
        if webpages:
            print("\n--- Scraped Webpages: ---")
            for page in webpages:
                print(f"- {page['question']}: {page['url']}")