import requests
import re
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

def scrape_page(url):
    """Download page and return a BeautifulSoup object."""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def extract_books(soup):
    """Extract list of books from a page."""
    books = []
    for article in soup.find_all("article", class_="product_pod"):
        title = article.h3.a["title"]
        # Removes every character that is not a digit or decimal point from the price using regular expression
        price = float(re.sub(r'[^\d.]', '', article.find("p", class_="price_color").text))
        availability = article.find("p", class_="instock availability")
        stock = "In stock" if availability and "In stock" in availability.text else "Out of stock"
        rating_class = article.find("p", class_="star-rating")["class"]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = rating_map[rating_class[1]] if len(rating_class) > 1 else None
        books.append({
            "title": title,
            "price_gbp": price,
            "stock": stock,
            "rating": rating
        })
    return books

def main():
    all_books = []
    for page_num in range(1, 51):
        url = BASE_URL.format(page_num)
        print(f"Scraping {url}...")
        soup = scrape_page(url)
        books = extract_books(soup)
        all_books.extend(books)
        time.sleep(1)

    with open("books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price_gbp", "stock", "rating"])
        writer.writeheader()
        writer.writerows(all_books)

    print(f"Done. {len(all_books)} books scraped.")

if __name__ == "__main__":
    main()
