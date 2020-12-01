"""
Setup the database for the app and add some scrapers, rules and customer information
"""

# Imports
from database import DbSqlite3Wrapper
from ScraperConfig import configuration

database_name = configuration["database_name"]

# Customers
customers = [
    (1, 'argos', 'Argos UK'),
    (2, 'wickes', 'Wickes DIY Store')
]

# Scrapers
scrapers = [
    (1, 'argos-xbox-series-x', 'Argos scraper for xbox series x', 1, 1 , 'xbox series x', 0.5),
    (2, 'wickes-bath-taps', 'Wickes scraper for bath taps', 1, 2, 'bath taps', 1)
]

# Rules
argos_xbox_rules = [
            ('url', 'https://www.argos.co.uk/search', 1, 1),
            ('searches', 'class/search', 1, 1),
            ('products', 'class/ProductCardstyles__Wrapper-l8f8q8-1', 1, 1),
            ('title', 'class/ProductCardstyles__Title-l8f8q8-12', 1, 1),
            ('price', 'class/ProductCardstyles__PriceText-l8f8q8-14', 1, 1),
            ('stock', '', 1, 1)
    ]

wickes_bath_tap_rules = [
            ('url', 'https://www.wickes.co.uk/search?text=', 2, 2),
            ('searches', 'class/products-list', 2, 2),
            ('products', 'class/card', 2, 2),
            ('title', 'class/product-card__title', 2, 2),
            ('price', 'class/product-card__price', 2, 2),
            ('stock', '', 2, 2)
        ]

# SQL
scrapers_sql = "INSERT INTO scrapers(id,name,description,enabled,customer_id, search_terms, run_frequency) " \
               "VALUES(?, ?, ?, ?, ?, ?, ?)"
customers_sql = "INSERT INTO customers(id,name,description) VALUES(?, ?, ?)"
rules_sql = "INSERT INTO rules(name,value,scraper_id,customer_id) VALUES(?, ?, ?, ?)"

if __name__ == '__main__':

    dbc = DbSqlite3Wrapper(database_name)
    dbc.connect()

    # Create the database
    #dbc.setup_scrapers_db()

    # Scrapers and customers inserts
    dbc.execute(customers_sql, customers)
    dbc.execute(scrapers_sql, scrapers)

    # Scraper rule Inserts
    dbc.execute(rules_sql, argos_xbox_rules)
    dbc.execute(rules_sql, wickes_bath_tap_rules)

    dbc.close()