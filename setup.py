"""
Setup the database for the app and add some scrapers, rules and customer information
"""

# Imports
from database import DbSqlite3Wrapper
from ScraperConfig import configuration

database_name = configuration["database_name"]

# Customers
customers = [
        (1, 'techstore.com', 'The premier PC part specialist')
    ]

# Scrapers
scrapers = [
        (1, 'techstore-motherboards', 'All motherboards on techstore.com', 1, 1, 'motherboards', 6)
    ]

# Rules
techstore_mb_rules = [
            ('url', 'https://www.techstore.com/search', 1, 1),
            ('searches', 'class/search', 1, 1),
            ('products', 'class/ProductCardstyles__Wrapper-l8f8q8-1', 1, 1),
            ('title', 'class/ProductCardstyles__Title-l8f8q8-12', 1, 1),
            ('price', 'class/ProductCardstyles__PriceText-l8f8q8-14', 1, 1),
            ('stock', '', 1, 1)
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
    dbc.setup_scrapers_db()

    # Scrapers and customers inserts
    dbc.execute(customers_sql, customers)
    dbc.execute(scrapers_sql, scrapers)

    # Scraper rule Inserts
    dbc.execute(rules_sql, techstore_mb_rules)

    dbc.close()