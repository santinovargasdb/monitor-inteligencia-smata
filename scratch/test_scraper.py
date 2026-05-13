
from src.scrapers.rss_scraper import DynamicScraper
import asyncio

def test():
    scraper = DynamicScraper()
    print("Testing scraper for EE. UU...")
    try:
        news = scraper.fetch("EE. UU.", query="Toyota")
        print(f"Success! Found {len(news)} items for EE. UU.")
        for n in news[:2]:
            print(f"- {n.title}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
