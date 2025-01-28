import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_page_content(url):
    """
    Fetch the HTML content of the page.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_product_data(html):
    """
    Parse product details (name, price, and rating) from the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    # Find all product containers
    product_containers = soup.find_all("article", class_="product_pod")
    
    for product in product_containers:
        name = product.h3.a["title"]
        price = product.find("p", class_="price_color").text
        rating = product.p["class"][1]  # Get the second class name (e.g., "One", "Two")
        products.append({"Name": name, "Price": price, "Rating": rating})
    
    return products

def save_to_csv(data, filename="products.csv"):
    """
    Save the scraped data to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    # Base URL of the website to scrape
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    all_products = []
    
    # Scrape multiple pages (e.g., first 5 pages)
    for page in range(1, 6):
        url = base_url.format(page)
        print(f"Scraping page {page}: {url}")
        
        html = fetch_page_content(url)
        if html:
            products = parse_product_data(html)
            all_products.extend(products)
        
    # Save the data to a CSV file
    save_to_csv(all_products)

if __name__ == "__main__":
    main()
