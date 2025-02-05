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
OLLAMA_MODEL = "llama3.2"
SEARCH_ENGINE = "brave"
SEARCH_API_KEY = "YOUR_SERP_API_KEY"

# --- Search Engine Functions ---
async def search_brave_direct(query):
    """Directly scrapes Brave search results using Playwright Async API."""
    search_query = urllib.parse.quote_plus(query)
    url = f"https://search.brave.com/search?q={search_query}"

    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=30000)

            # --- Selector for Brave Search result links (inspect Brave Search page to refine if needed) ---
            link_elements = await page.locator('div#web-results div.snippet-item a.url').all()

            for link_element in link_elements:
                href = await link_element.get_attribute('href')
                if href and href.startswith("http") and "brave.com" not in href:
                    links.append(href)

        except Exception as e:
            print(f"Error during Playwright navigation or scraping Brave Search: {e}")
        finally:
            await browser.close()
    return links

def search_google_api(query, api_key):
    """Searches Google using a SERP API (example using SerpAPI).
       Replace with your chosen API or direct scraping if needed (less reliable)."""
    url = "https://serpapi.com/search"  # Example for SerpAPI
    params = {
        "api_key": api_key,
        "q": query,
        "engine": "google"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    results_json = response.json()
    links = [result.get('link') for result in results_json.get('organic_results', []) if result.get('link')]
    return links

def search_google_direct(query):
    """Directly scrapes Google search results (fragile, use with caution, may violate TOS)."""
    search_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} # Mimic browser user-agent
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link_element in soup.select('a'): # You'll need to refine selectors based on Google's HTML
        href = link_element.get('href')
        if href and href.startswith("http") and "google" not in href: # Basic filtering - improve this
            links.append(href)
    return links

async def get_search_links(query, search_engine=SEARCH_ENGINE, search_api_key=SEARCH_API_KEY):
    """Orchestrates search based on configured search engine."""
    if search_engine == "brave":
        return await search_brave_direct(query)
    elif search_engine == "google" and search_api_key:
        return search_google_api(query, search_api_key)
    elif search_engine == "google":
        return search_google_direct(query)
    else:
        print(f"Warning: Search engine '{search_engine}' not fully configured or API key missing. Defaulting to direct Brave search.")
        return await search_brave_direct(query) # Default to Brave if misconfigured


# --- Website Content Scraping Function ---

async def scrape_website_content(url):
    """Scrapes text content from a website URL using Playwright Async API, newspaper3k, and BeautifulSoup as fallback."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            html_content = await page.content()

            try:
                # --- Attempt to use newspaper3k for better article extraction ---
                article = Article(url) # URL is still needed by newspaper
                article.set_html(html_content) # Pass HTML from Playwright
                article.parse()
                text_content = article.text
                if text_content.strip(): # Check if newspaper3k extracted content
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
    """Expands the initial question using Ollama to generate related deeper questions.
       Now requests JSON array format and max 6-word questions."""
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

Only output the JSON array.""" # Updated prompt with word limit and array format
    print("\nExpanding question with Ollama...")
    try:
        json_response = query_ollama(expansion_prompt)
        print(f"Ollama Question Expansion Response: {json_response}") # Print raw response for debugging

        # --- Attempt to parse JSON array ---
        try:
            expanded_questions = json.loads(json_response) # Directly parse as JSON array
            if isinstance(expanded_questions, list): # Verify it's a list
                print(f"Expanded Questions (Parsed as JSON array): {expanded_questions}")
                return expanded_questions
            else:
                print(f"Warning: Parsed JSON, but not a list (array). Unexpected format. Raw response: {json_response}")
                return [question] # Fallback to original question

        except json.JSONDecodeError as json_err:
            print(f"JSON Decode Error: {json_err}. Raw response was: {json_response}. Falling back to original question.")
            return [question] # Fallback to original question

    except Exception as e:
        print(f"Error during question expansion with Ollama: {e}. Falling back to original question.")
        return [question] # Fallback to original question


# --- Main Function ---

async def main():
    user_question = input("Ask me anything: ")

    # --- Expand the question using Ollama ---
    expanded_questions = expand_question_with_ollama(user_question)

    all_scraped_content = "" # Accumulate content from all expanded questions

    for q in expanded_questions:
        print(f"\n--- Searching and Scraping for Expanded Question: '{q}' ---")
        search_results_links = await get_search_links(q)

        if not search_results_links:
            print(f"No search results found for expanded question: '{q}'.")
            continue # Go to the next expanded question

        print(f"Found search results for expanded question: '{q}'. Scraping content...")
        for link in search_results_links[:2]: # Scrape content from top 2 links for each expanded question (adjust as needed)
            print(f"Scraping: {link}")
            content = await scrape_website_content(link)
            all_scraped_content += f"\n\n---\n\nURL for Question '{q}': {link}\nContent:\n{content}"

    # --- Prepare Prompt for LLM with ALL scraped content and ALL questions ---
    questions_for_prompt = ""
    for i, q in enumerate(expanded_questions):
        questions_for_prompt += f"{i+1}. {q}\n"

    final_prompt_for_llm = f"""Answer the following question based on the information provided below.
Consider ALL the questions listed below when formulating your answer.
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

    print("\nSending to Ollama for final answer...")
    llm_response = query_ollama(final_prompt_for_llm)
    print("\n--- Final Response from Ollama ---")
    print(llm_response)


if __name__ == "__main__":
    asyncio.run(main())