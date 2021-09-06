
Product Searcher
================

This repository contains the code for an automated product searcher.

Overview
--------

A single bot performs the following steps:

1. Connects to the target sites search page
2. Performs a search with specified keywords
3. Returns the first HTML page of the results and extracts the relevant data and displays it within the console
4. Stores the RAW HTML in a database for later processing

You can have multiple bots running at the same time performing searches against different sites.


Dependencies
------------

- All code written in python 3
- Python libraries used:
 - Beautiful Soup
 - Requests

Installation
------------

Perform the following steps to install

- In a target directory clone the repo

```bash
git clone https://github.com/alittlebroken/scraperBot
```

- Create a python virtual environment

```bash
python -m venv venv
```

- Activate the virtual environment

  unix
```
source venv/Scripts/activate
```

- Install the required packages

```bash
pip install bs4 requests
```

Configuration
-------------

Open the setup.py file in your favourite text/code editor

### Add a customer

Each customer is stored inside the customers list as a single tuple. To add more just add another tuple

**Format:**
```Python
  (
    id,           # Unique identifier for the customer
    name,         # Customers name
    description   # Description of the customer
  )
```
**Example:**
```Python
  customers = [
    (
      1,
      'techstore.com',
      'The premier PC part specialist'
    ),
  ]
```

### Add a scraper
A scraper is added to the scrapers list as a singular tuple. If you wish to add another scraper just add another tuple to the list

**Format:**
```Python
  (
    id,             # Unique id for the scraper
    name,           # Name for this scraper
    description,    # Description of the scraper
    enabled,        # 1 to enable and 0 to disable
    customerID,     # The id of the customer this scraper belongs to
    searchTerms,    # The terms to search on
    runFrequency,   # Run the scraper once every X hours
  )
```

**Example:**
```Python
  scrapers = [
      (
        1,
        'techstore-motherboards',
        'All motherboards on techstore.com',
        1,
        1,
        'motherboards',
        6
      ),
  ]
```

### Add new rules

Each customer should have there own list of rules with each rule being it's own tuple

The rules we support currently are:
- *url* - The url to the customers search packages
- *searches* - The CSS class that identifies the search results on a page
- *products* - The CSS classes that identify a single product in the search results
- *title* - The CSS class that contains the name of an individual product in the results
- *price* - The CSS class which contains the price of an item in the search results

**Format:**
```Python
customer_scraper_rules = [
  (
    ruleName,         # One of the rule names above
    ruleValue,        # Value for this rule
    scraperID,        # The ID of the scraper associated with this rule
    customerID        # The ID of the customer associated with this rule
  ),
]
```

**Example:**
```Python
techstore_mb_rules = [
        ('url', 'https://www.techstore.com/search', 1, 1),
        ('searches', 'class/search', 1, 1),
        ('products', 'class/ProductCardstyles__Wrapper-l8f8q8-1', 1, 1),
        ('title', 'class/ProductCardstyles__Title-l8f8q8-12', 1, 1),
        ('price', 'class/ProductCardstyles__PriceText-l8f8q8-14', 1, 1),
        ('stock', '', 1, 1)
]
```

### Ensure the customer specific rules get added to the database

You need to add one line per set of customer rules in the **# Scraper rule inserts** section

Don't forget to change the second variable of the below function to the actual name you gave your customer rule list

```Python
dbc.execute(rules_sql, techstore_mb_rules)
````

### Final Steps
- Save and close the file
- Run the following command to create the customers, scrapers and rules

  ```bash
  python setup.py
  ```

Startup
-------
Run the following command to start the bot(s)

```bash
python main.py
```

Press CTRL + C to end the program

Cleanup
-------

Once you are happy that the bits are working as intended then you can delete the setup.py file

TODO
--------------------
- Web Interface with Flask
- Add docker files for web, DB and scrapers
- Come up with a better name for the project
- Output startup info to console
- Use a scheduler library for the scrapers
