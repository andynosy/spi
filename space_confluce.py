import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
confluence_domain = os.getenv("CONFLUENCE_DOMAIN")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")

# Set up headers with Personal Access Token using Bearer authentication
headers = {
    "Authorization": f"Bearer {personal_access_token}",
    "Content-Type": "application/json"
}

def fetch_pages_in_space(space_key, parent_page_id=None):
    """
    Recursively fetches all pages within a given Confluence space, optionally starting from a parent page ID.
    
    Args:
        space_key (str): The Confluence space key to limit the pages fetched.
        parent_page_id (str, optional): The parent page ID to start from. If None, it fetches all pages in the space.
        
    Returns:
        list: A list of page data dictionaries for all pages in the specified space.
    """
    all_pages = []

    # Build URL based on whether we're fetching a root space or subpages of a specific parent page
    if parent_page_id:
        # Fetch child pages of the given parent page within the space
        url = f"{confluence_domain}/rest/api/content/{parent_page_id}/child/page?expand=body.storage"
    else:
        # Fetch all root pages in the specified space
        url = f"{confluence_domain}/rest/api/content?spaceKey={space_key}&expand=body.storage&limit=100"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx, 5xx)
        
        data = response.json()
        pages = data.get("results", [])

        for page in pages:
            page_id = page.get("id")
            title = page.get("title")
            body_content = page["body"]["storage"]["value"]  # HTML content of the page

            # Add the current page to the list
            all_pages.append({
                "id": page_id,
                "title": title,
                "content": body_content
            })

            # Recursively fetch subpages of this page, but keep it within the same space
            all_pages.extend(fetch_pages_in_space(space_key, page_id))

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Error: Authentication failed. Check your personal access token.")
        elif response.status_code == 404:
            print(f"Error: Page not found for ID {parent_page_id if parent_page_id else 'root of space'}.")
        elif response.status_code == 500:
            print("Error: Internal server error at Confluence.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Network connection error: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
    except ValueError as val_err:
        print(f"Error: Failed to parse JSON response - {val_err}")
    except KeyError as key_err:
        print(f"Error: Missing expected data in the response - {key_err}")

    return all_pages

def main():
    # Define the Confluence space key you want to limit to (e.g., "UGLY")
    space_key = "UGLY"  # Replace with your specific space key
    all_pages = fetch_pages_in_space(space_key)
    
    print(f"Total pages fetched in space '{space_key}': {len(all_pages)}")
    for page in all_pages:
        print(f"Page ID: {page['id']}, Title: {page['title']}")

# Run the main function to start the recursive fetch
if __name__ == "__main__":
    main()
