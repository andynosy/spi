import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
confluence_domain = os.getenv("CONFLUENCE_DOMAIN")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")  # Store your PAT in an environment variable

# Function to fetch a Confluence page's content using PAT
def fetch_page_content(page_id):
    """
    Fetches the HTML content of a Confluence page by page ID.

    Args:
        page_id (str): The ID of the Confluence page to fetch.

    Returns:
        str: The HTML content of the Confluence page, or None if fetching failed.
    """
    url = f'{confluence_domain}/rest/api/content/{page_id}?expand=body.storage'
    headers = {
        'Authorization': f'Basic {personal_access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('body', {}).get('storage', {}).get('value', '')
        elif response.status_code == 404:
            print("Error: Page not found.")
        elif response.status_code == 401:
            print("Error: Authentication failed. Check your token.")
        elif response.status_code == 500:
            print("Error: Internal server error.")
        else:
            print(f"Failed to fetch page content: HTTP status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    return None

# Function to process and clean the content using BeautifulSoup
def extract_text_from_html(html_content):
    """
    Extracts and cleans the text content from raw HTML using BeautifulSoup.

    Args:
        html_content (str): The raw HTML content of the Confluence page.

    Returns:
        str: The extracted, clean text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text = ' '.join(soup.stripped_strings)
    return text

# Main function to retrieve and process a single Confluence page
def main(page_id):
    """
    Main function to fetch and process Confluence page content.

    Args:
        page_id (str): The ID of the Confluence page to fetch.

    Returns:
        None
    """
    content = fetch_page_content(page_id)
    
    if content:
        print("Successfully fetched page content!")
        clean_text = extract_text_from_html(content)
        print("Extracted Content (First 500 characters):")
        print(clean_text[:500])
    else:
        print("Failed to fetch or process page content.")

# Usage example: Replace with the actual page ID you want to retrieve
if __name__ == "__main__":
    # Replace '12345' with the actual page ID you want to fetch
    page_id = '12345'
    main(page_id)
