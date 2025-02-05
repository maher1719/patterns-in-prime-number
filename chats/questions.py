# your_ollama_script.py
import nest_asyncio
nest_asyncio.apply()

import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import asyncio
from playwright.async_api import async_playwright
from newspaper import Article

# --- Configuration ---
OLLAMA_MODEL = "llama3.2" # Or "llama3.2" if that's your model name in Ollama
SEARCH_ENGINE = "brave"
SEARCH_API_KEY = "YOUR_SERP_API_KEY"
USE_SCRAPING = True

# --- Search Engine Functions ---
async def search_brave_direct(query):
    """Directly scrapes Brave search results using Playwright Async API."""
    if not USE_SCRAPING:
        return []

    search_query = urllib.parse.quote_plus(query)
    url = f"https://search.brave.com/search?q={search_query}"

    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=30000)

            # --- Captcha Detection Logic ---
            page_title = await page.title()
            if "captcha" in page_title.lower() or "robot verification" in page_title.lower():
                print(f"Warning: Captcha page detected for query: '{query}'.") # No stopping scraping here, just warn

                return None  # Indicate captcha, but let main function decide how to handle it

            # --- CSS Selector for Brave Search result links ---
            link_elements = await page.locator('div.snippet a.heading-serpresult div div.title').all()

            if not link_elements:
                print(f"Warning: No search result link elements found on Brave Search page for query: '{query}'.")
                return []

            for link_element in link_elements:
                href = await link_element.locator('xpath=..').get_attribute('href')
                if href and href.startswith("http") and "brave.com" not in href:
                    links.append(href)

        except Exception as e:
            print(f"Error during Playwright navigation or scraping Brave Search: {e}")
        finally:
            if browser:
                await browser.close()

    if not links:
        print(f"Warning: No external links extracted from Brave Search results for query: '{query}'.")

    return links

async def get_search_links(query, search_engine=SEARCH_ENGINE, search_api_key=SEARCH_API_KEY):
    """Orchestrates search using Brave search engine, handles captcha detection."""
    if not USE_SCRAPING:
        return []

    if search_engine == "brave":
        search_results = await search_brave_direct(query)
        if search_results is None: # Captcha is now handled in main function
            return None # Indicate captcha, but let main function decide how to handle it
        return search_results
    else:
        print(f"Warning: Search engine '{search_engine}' is not 'brave'. Defaulting to direct Brave search.")
        search_results = await search_brave_direct(query)
        if search_results is None: # Captcha is now handled in main function
            return None # Indicate captcha, but let main function decide how to handle it
        return search_results


# --- Website Content Scraping Function ---

async def scrape_website_content(url):
    """Scrapes text content from a website URL using Playwright Async API, newspaper3k, and BeautifulSoup as fallback."""
    if not USE_SCRAPING:
        return ""

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            html_content = await page.content()

            try:
                # --- Attempt to use newspaper3k for better article extraction ---
                article = Article(url)
                article.set_html(html_content)
                article.parse()
                text_content = article.text
                if text_content.strip():
                    print(f"Successfully extracted content using newspaper3k from: {url}")
                    return text_content
                else:
                    print(f"newspaper3k failed to extract meaningful content, falling back to basic parsing for: {url}")

            except Exception as newspaper_err:
                print(f"Error using newspaper3k for {url}: {newspaper_err}. Falling back to basic parsing.")

            # --- Fallback to basic BeautifulSoup parsing (if newspaper3k fails or extracts nothing) ---
            soup = BeautifulSoup(html_content, 'html.parser')
            paragraphs = soup.find_all('p')
            text_content = "\n".join([p.get_text() for p in paragraphs])
            return text_content

    except Exception as e:
        print(f"Error scraping {url} with Playwright: {e}")
        return ""


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
def expand_question_with_ollama(question):
    """Expands the initial question using Ollama to generate related deeper questions."""
    if not USE_SCRAPING:
        return [question]

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

# --- Main Function ---
async def main(user_question, use_scraping=USE_SCRAPING):
    global USE_SCRAPING
    USE_SCRAPING = use_scraping

    # --- Expand the question using Ollama ---
    expanded_questions = expand_question_with_ollama(user_question)

    all_scraped_content = "" # Initialize as empty string
    scraped_webpages = []
    captcha_detected = False # Flag to track captcha

    if USE_SCRAPING:
        for q in expanded_questions:
            print(f"\n--- Searching and Scraping for Expanded Question: '{q}' ---")
            search_results_links = await get_search_links(q)

            if search_results_links is None: # Captcha detected
                print("Captcha detected, stopping scraping for remaining questions.")
                captcha_detected = True # Set flag
                break # Stop scraping, but continue to LLM with whatever content we have

            if not search_results_links:
                print(f"No search results found for expanded question: '{q}'.")
                continue

            print(f"Found search results for expanded question: '{q}'. Scraping content...")
            for link in search_results_links[:2]:
                print(f"Scraping: {link}")
                content = await scrape_website_content(link)
                all_scraped_content += f"\n\n---\n\nURL for Question '{q}': {link}\nContent:\n{content}"
                scraped_webpages.append({"question": q, "url": link})

    # --- Prepare Prompt for LLM ---
    if all_scraped_content and USE_SCRAPING and not captcha_detected: # Use context prompt only if we have content AND scraping was enabled and no captcha
        questions_for_prompt = ""
        for i, q in enumerate(expanded_questions):
            questions_for_prompt += f"{i+1}. {q}\n"

        final_prompt_for_llm = f"""Answer the following question based on the information provided below.
Consider ALL the questions listed below when formulating your answer. And give long answer as you could.
If the information is not in the context, or not relevant to ANY of the questions, say "I cannot find the answer in the provided context."

Questions to consider:
--- Questions ---
{questions_for_prompt}
--- End Questions ---

--- Context ---
{all_scraped_content}
--- End Context ---

Answer:
"""
    else: # Fallback prompt - answer from own knowledge if no scraped content OR scraping disabled OR captcha
        fail="Sorry, I encountered a captcha while searching, so I'm answering based on my own knowledge."
        final_prompt_for_llm = f"""Answer the question: '{user_question}' directly based on your knowledge.
Give a comprehensive and detailed answer."""
        if captcha_detected: # Inform user about captcha in response too
            return None, "Sorry, I encountered a captcha while searching, so I'm answering based on my own knowledge.", [] # Return captcha message
        elif USE_SCRAPING: # If scraping was intended but failed to get content (no search results, scraping errors etc.)
            print("Warning: No scraped content available. Answering based on own knowledge.")


    print("\nSending to Ollama for final answer...")
    llm_response = query_ollama(final_prompt_for_llm)
    print("\n--- Final Response from Ollama ---")
    print(llm_response)

    return llm_response, None, scraped_webpages

if __name__ == "__main__":
    user_input_question = input("Ask me anything: ")
    response, error_msg, webpages = asyncio.run(main(user_input_question, use_scraping=True))
    if error_msg:
        print(f"Error: {error_msg}")
    elif response:
        print("\n--- Final Response: ---")
        print(response)
        if webpages:
            print("\n--- Scraped Webpages: ---")
            for page in webpages:
                print(f"- {page['question']}: {page['url']}")