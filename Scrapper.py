import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse

def fetch_robots_txt(base_url):
    """
    Fetch and parse the robots.txt file from the website.
    """
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch robots.txt: {e}")
        return None

def is_scraping_allowed(base_url, path="/"):
    """
    Check if scraping is allowed for the given path based on robots.txt.
    """
    robots_txt = fetch_robots_txt(base_url)
    if not robots_txt:
        print("No robots.txt found. Proceeding with scraping.")
        return True  # If robots.txt is missing, assume scraping is allowed.

    # Parse robots.txt
    user_agent = "User-agent: *"
    disallowed_paths = []
    for line in robots_txt.split("\n"):
        if line.startswith(user_agent):
            continue
        if line.startswith("Disallow:"):
            disallowed_path = line.split(":", 1)[1].strip()
            disallowed_paths.append(disallowed_path)

    # Check if the given path is disallowed
    for disallowed in disallowed_paths:
        if path.startswith(disallowed):
            return False

    return True

def fetch_page_content(url):
    """
    Fetch the HTML content of the page.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_content(html, element, class_name=None):
    """
    Parse user-specified content (e.g., headings, links) from the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Find elements based on user input
    if class_name:
        elements = soup.find_all(element, class_=class_name)
    else:
        elements = soup.find_all(element)

    for elem in elements:
        if element == "a":  # Special case for links
            data.append(elem.get("href"))
        else:
            data.append(elem.get_text(strip=True))

    return data

def find_next_page(soup, base_url):
    """
    Find the 'Next' page link to continue scraping.
    """
    next_page = soup.find("a", text="Next")
    if next_page and next_page.get("href"):
        return urljoin(base_url, next_page.get("href"))
    return None

def save_to_csv(data, filename="scraped_data.csv"):
    """
    Save the scraped data to a CSV file.
    """
    df = pd.DataFrame(data, columns=["Data"])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    # Ask the user for the website to scrape
    website = input("Enter the website URL (e.g., https://example.com): ").strip()
    parsed_url = urlparse(website)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Check if scraping is allowed
    print("Checking robots.txt...")
    if not is_scraping_allowed(base_url, parsed_url.path):
        print("Scraping is not allowed on this website according to robots.txt. Exiting.")
        return

    print("Scraping is allowed. Proceeding...")

    # Ask the user what type of content they are looking for
    print("\nWhat type of content are you looking for?")
    print("1. Links")
    print("2. Headings")
    print("3. Paragraphs")
    print("4. Custom (Advanced Users)")
    choice = input("Enter your choice (1-4): ").strip()

    # Map user choice to HTML elements
    if choice == "1":
        element, class_name = "a", None
    elif choice == "2":
        element, class_name = "h1", None  # For simplicity, this looks for h1 tags; you can expand it to h2, h3, etc.
    elif choice == "3":
        element, class_name = "p", None
    elif choice == "4":
        element = input("Enter the HTML element (e.g., div, span): ").strip()
        class_name = input("Enter the class name to filter (leave blank if none): ").strip()
        class_name = class_name if class_name else None
    else:
        print("Invalid choice. Exiting.")
        return

    # Start scraping from the first page
    current_url = website
    all_data = []

    while current_url:
        print(f"Scraping: {current_url}")
        html = fetch_page_content(current_url)
        if not html:
            print(f"Failed to fetch content from {current_url}.")
            break

        # Parse the specified content
        page_data = parse_content(html, element, class_name)
        all_data.extend(page_data)

        # Find the next page link
        soup = BeautifulSoup(html, "html.parser")
        current_url = find_next_page(soup, base_url)

    # Save the scraped data
    if all_data:
        print(f"Scraped {len(all_data)} items. Saving to CSV...")
        save_to_csv(all_data)
    else:
        print("No data found. Exiting.")

if __name__ == "__main__":
    main()
