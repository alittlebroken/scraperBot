# main.py A python web scraper
# Paul Lockyer (plockyer@googlemail.com)
# 2020-10-21

## Imports ##
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime as dt

# List basic rules for sites to scrape
ruleset = {}

# Add Argos rules
ruleset["ARGOS"] = {
    'url': 'https://www.argos.co.uk/search/',
    'searches_rule': 'class/search',
    'products_rule': 'class/ProductCardstyles__Wrapper-l8f8q8-1',
    'product_title': 'class/ProductCardstyles__Title-l8f8q8-12',
    'product_price': 'class/ProductCardstyles__PriceText-l8f8q8-14',
    'product_stock': None,
    'last_checked': None
}

ruleset["WICKES"] = {
    'url': 'https://www.wickes.co.uk/search?text=',
    'search_rule': 'class/product-list',
    'product_rule': 'class/card',
    'product_title': 'class/product-card__title',
    'product_price': 'class/product-card__price',
    'product_stock': None,
    'last_checked': None
}

# Class for each product found on the page
class productItem:

    # Standard class initiator
    def __init__(self, title, price, url, out_of_stock = False):
        self.title = title
        self.price = price
        self.url = url
        self.out_of_stock = out_of_stock

# ScraperBot class
class scraperBot:
    # scraperBot class for searching different sites for specific items

    def __init__(self, rules, search_term):
        # Standard class setup method
        self.rules = rules
        self.terms = search_term
        self.results = ''

    def search(self, allResults=True):
        # Perform the search against the website
        self.result = requests.get('{}/{}/'.format(self.rules['url'], self.terms))
        self.rules['last_checked'] = dt.now()
        print("Last checked: {}".format(self.rules['last_checked']))

        # Break out the search terms in a list
        searchTerms = list(self.terms.split(' '))

        # Search data returned OK, lets parse the hell out of it
        if self.result.status_code == 200:

            self.soup = BS(self.result.text, 'html.parser')

            # Extract the rules to be uses
            if self.rules['searches_rule']:
                searchesRule = self.rules['searches_rule'].split("/")

            if self.rules['products_rule']:
                productsRule = self.rules['products_rule'].split("/")

            if self.rules['product_title']:
                productTitleRule = self.rules['product_title'].split("/")

            if self.rules['product_price']:
                productPriceRule = self.rules['product_price'].split("/")

            if self.rules['product_stock']:
                productStockRule = self.rules['product_stock'].split("/")


            # Get the main body of search results
            resultset = self.soup.find_all(attrs={searchesRule[0]: searchesRule[1]})

            # Now find all the individual items
            for result in resultset:
                items = result.find_all(attrs={productsRule[0]: productsRule[1]})

                # Now for each individual item, extract the relevant data
                for item in items:

                    # Check we have data
                    if (item.find(attrs={productTitleRule[0]: productTitleRule[1]})):
                        title = item.find(attrs={productTitleRule[0]: productTitleRule[1]}).text

                    if (item.find(attrs={productPriceRule[0]: productPriceRule[1]})):
                        price = item.find(attrs={productPriceRule[0]: productPriceRule[1]}).text.strip(' ')

                    # Only print if the title matches all search terms we want
                    if title == self.terms:
                        print("{} [ {} ]".format(title, price))




# The main program function
def main():

    # Argos details for searching
    search_company = "ARGOS"
    search_terms = 'Xbox Series X 1TB Console Pre-Order'
    bot = scraperBot(ruleset[search_company], search_terms)
    print("=== {} ===".format(search_company))
    print("search term(s): {}".format(search_terms))
    # perform a search
    bot.search(True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Run the application
    main()
