# Product Scraper

A simple scraper app that can retrieve text from a specified url according to a set of rules.

Outputs extracted data to screen and stores raw data within the database

## Usage

### Initial setup
* To add your own information edit the add_scrapers.py file
* To add customers modify the tuple list customers
    
    ```python
    customers = [
        (1, 'techstore.com', 'The premier PC part specialist')
    ]
    ```
    NOTE: To add more customers just add another tuple to the list
    
* To add a scraper modify the tuple list called scrapers

    ```python
    scrapers = [
        (1, 'techstore-motherboards', 'All motherboards on techstore.com', 1, 1, 'motherboards', 6)
    ]
    ```
    NOTE: To add more scrapers just add another tuple to the list
    
* To add some rules add a <my_search>_rules tuple list to the file
    
    ```python
    techstore_mb_rules = [
            ('url', 'https://www.techstore.com/search', 1, 1),
            ('searches', 'class/search', 1, 1),
            ('products', 'class/ProductCardstyles__Wrapper-l8f8q8-1', 1, 1),
            ('title', 'class/ProductCardstyles__Title-l8f8q8-12', 1, 1),
            ('price', 'class/ProductCardstyles__PriceText-l8f8q8-14', 1, 1),
            ('stock', '', 1, 1)
    ]
    ```
    NOTE: There should be only one set of rules per scraper
    
    NOTE: It has assumed that for the rules you have already investigated the results page for any
          search to gather the relevant data
    
* Now modify the Scarper rule Inserts section to only include your rules
  
  ```python
  dbc.execute(rules.sql, techstore_mb_rules)
  ```

* Remove or comment out any entries you do not need
* Save and close the file
* Run the following to create the database and create your scrapers, rules and customers

  ```
  python setup.py
  ```
  
  NOTE: Remove this file once run and you have verified the data inside has been created
  properly
  

### Startup
   
    ```
    python main.py
    ```
    NOTE: CTRL + C to end the program