from dotenv import load_dotenv
load_dotenv()

from chains.dedup.url_dedup import url_dedup
from chains.dedup.fuzzy_dedup import fuzzy_dedup
from chains.scraper import scraper
from chains.listings_formatter import listings_formatter
from chains.misc import filter_none
from chains.db import save_listing

import questionary
from input.list import list_prompt
from input.spinner import with_spinner

urls = list_prompt("Paste or type URLs")

get_listings_chain = \
  with_spinner(url_dedup.map() | filter_none, "Simple deduping") | \
  with_spinner(scraper.map(), "Scraping pages") | \
  with_spinner(fuzzy_dedup.map(), "Fuzzy deduping") | \
  with_spinner(listings_formatter.map(), "Formatting listings")
listings = get_listings_chain.invoke(urls)

choices = [questionary.Choice(f"{l['title']}, {l['company']}", value=l, checked=True) for l in listings] + \
          [questionary.Choice("Save all", value="__all__", checked=True)]
questionary.checkbox(f"Found {len(listings)} unique listings out of {len(urls)} URLs. Select to save:", 
                      choices=[f"{l["title"]}, {l["company"]}" for l in listings]).ask()

# See how they do it: https://github.com/cwwmbm/linkedinscraper
# Take url inputs from user
# URLS = ["https://jobs.smartrecruiters.com/Grab/744000087062923-grit-trainee-software-engineer-trust-engineering?trid=2d92f286-613b-4daf-9dfa-6340ffbecf73"]

# # IMPORTANT: Fuzzy dedup is susceptible to false positives
# chain = url_dedup.map() | filter_none | scraper.map() | fuzzy_dedup.map() | filter_none | listings_formatter.map() | save_listing.map()
# res = chain.invoke(URLS)
# print(res)

# URLS = ["https://jobs.smartrecruiters.com/Grab/744000087062923-grit-trainee-software-engineer-comms-platform?trid=2d92f286-613b-4daf-9dfa-6340ffbecf73"]
# res = chain.invoke(URLS)
# print(res)

# URLS = ["https://careers.shopee.sg/job-detail/J02037008/1?channel=10001"]
# res = chain.invoke(URLS)
# print(res)
