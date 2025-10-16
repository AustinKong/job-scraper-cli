from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from chains.dedup.url_dedup import url_dedup
from chains.dedup.fuzzy_dedup import fuzzy_dedup
from chains.scraper import scraper
from chains.listings_formatter import listings_formatter
from chains.misc import filter_none
from chains.db import read_listing_by_url, save_listing

from langchain_core.runnables import RunnableBranch, RunnablePassthrough

import ui

urls = ui.list("Paste or type URLs").ask()
sample_urls = ["https://jobs.smartrecruiters.com/Grab/744000087062923-grit-trainee-software-engineer-trust-engineering?trid=2d92f286-613b-4daf-9dfa-6340ffbecf73",
               "https://careers.shopee.sg/job-detail/J02037008/1?channel=10001",
               "https://jobs.smartrecruiters.com/Grab/744000087062923-grit-trainee-software-engineer-comms-platform?trid=2d92f286-613b-4daf-9dfa-6340ffbecf73"]

# TODO: See how they do it: https://github.com/cwwmbm/linkedinscraper
urls = sample_urls

get_listings_chain = \
  ui.with_spinner_chain(url_dedup.map(), "URL deduping") | \
  ui.with_spinner_chain(RunnableBranch( # Scrape and format only if not found by URL dedup, we do this here because fuzzy dedup is extremely not reliable
    (lambda input: isinstance(input, dict) and input["dedup_conf"] == 0, scraper | listings_formatter),
    RunnablePassthrough()
  ).map(), "Scraping and formatting listings")
  # TODO: Fix fuzzy deduping to use keywords instead of full page body. Then readd this deduping
  # with_spinner(RunnableBranch(
  #   (lambda input: isinstance(input, dict) and input["dedup_conf"] == 0, fuzzy_dedup),
  #   RunnablePassthrough()
  # ).map(), "Fuzzy deduping")
listings = get_listings_chain.invoke(urls)

# At this point, dedup_conf = 0 for new listings, 1.0 for exact URL matches, and (0, 1) for fuzzy matches
# We let the user choose to rescrape or not for fuzzy matches 
print([l["title"] + ", " + l["company"] + "(" + str(l["dedup_conf"]) + ")" for l in listings])

DEDUP_CONF_THRESHOLD = 0.8
choices = [ui.Choice(f"{l['title']}, {l['company']} ({l['dedup_conf']})", value=l, checked=(l["dedup_conf"] < DEDUP_CONF_THRESHOLD)) for l in listings]
to_save = ui.checkbox(f"Found {len([l for l in listings if l['dedup_conf'] < DEDUP_CONF_THRESHOLD])} unique listings out of {len(urls)} URLs. Select to save and generate:", choices=choices).ask()

print(to_save)