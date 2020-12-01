# main.py A python web scraper
# Paul Lockyer (plockyer@googlemail.com)
# 2020-10-21

## Imports ##
import requests
import os, os.path
from bs4 import BeautifulSoup as BS
from datetime import datetime as dt
import time

# List basic rules for sites to scrape
ruleset = {}

ruleset["WICKES"] = {
    'url': 'https://www.wickes.co.uk/search?text=',
    'searches_rule': 'class/products-list',
    'products_rule': 'class/card',
    'product_title': 'class/product-card__title',
    'product_price': 'class/product-card__price',
    'product_stock': None,
    'last_checked': None
}
app_title = "WebScraping Test"

print("=" * (len(app_title) + 10))
print("     {}     ".format(app_title))
print("=" * (len(app_title) + 10))

# Only gather results if we do not already have a cache of data locally
cache_file = "cache.dat"
cache_data = ''

class prod:

    def __init__(self, name, price):
        self.name = name
        self.price = price

items = []

print("Running at {} ".format(dt.now()))

def writeToCache(cache_file, content):
    pass

def readFromCache(cache_file):
    pass

def isCacheFresh(cache_file, freshness):
    pass

def cacheFileExists(cache_file):
    pass

if os.path.isfile(cache_file):
    print("Cache file exists. Loading data")
    with open(cache_file) as file:
        cache_data = file.read()

else:
    print("Cache file does not exist already. Generating new cache file")
    # perform the initial search for the data we would like to scrape
    response = requests.get("{}{}".format(ruleset["WICKES"]["url"],'bath+taps'))

    # check to see the status code of our request
    print("Status code = {}".format(response.status_code))

    # Save the data to the local cache but only if status code is good
    if response.status_code == 200:
        with open(cache_file, 'w') as file:
            file.write(response.text)
            # Store the data retrieved in memory as well
            cache_data = response.text
            print("Cache data saved to disk and memory")

# Now check the data is not empty before we carry on
if len(cache_data) > 0:
    print("cache data OK")
    data = BS(cache_data, 'html.parser')
    print("Filtering per rulesets")
    products = data.find('div', attrs={'class': 'products-list'}).find_all('div', attrs={'class': 'product-card'})
    print("{} matches found".format(len(products)))
    print("Extracting relevant data")

    for product in products:
        title = product.find('a', attrs={'class': 'product-card__title'})
        price = product.find('div', attrs={'class': 'product-card__price-value'})

        # Add the product to the list of items found
        items.append(prod(title.text, str(price.text).strip()))


    for item in items:
        print("{} {}".format(item.name, item.price))


else:
    print("There is an issue with the cache data")
