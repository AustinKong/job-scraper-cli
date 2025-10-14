import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from langchain_core.runnables import RunnableLambda

# Unused because it is kinda flaky
def scrape_with_requests(url: str) -> str:
  res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
  return res.text

def scrape_with_browser(url: str) -> str:
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle")
    html = page.content()
    browser.close()
    return html

def clean_html(html: str) -> str:
  soup = BeautifulSoup(html, "html.parser")
  for tag in soup(["script", "style", "noscript"]):
    tag.decompose()
  return " ".join(soup.stripped_strings)[:10000]
  
def scrape_one(input):
  url = input["url"]
  return input | { "content": clean_html(scrape_with_browser(url)) }

scraper = RunnableLambda(scrape_one)
