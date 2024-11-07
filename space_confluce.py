import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
confluence_domain = os.getenv("CONFLUENCE_DOMAIN")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")

# Set up headers with Personal Access Token
headers = {
    "Authorization": f"Basic {personal_access_token}",
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
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
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

    else:
        print(f"Failed to fetch pages for space '{space_key}' and page ID '{parent_page_id}'. Status code: {response.status_code}")

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
