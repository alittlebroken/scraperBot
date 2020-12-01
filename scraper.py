""" Scraper class

    Connects to a specified URL, performs a search for specified search terms and then stores the data locally and
    extracts relevant data from a set of rules.

"""

# TODO: Document class
# TODO: Remove output of processed data from screen

# Imports
import requests
from datetime import datetime as dt
from time import perf_counter
from bs4 import BeautifulSoup as BS


class ScraperBot:
    """

    scraperBot class for searching different sites for specific items

    :param scraper_id: The unique ID of the scraper in the database
    :param dbo: The object that allows us to run commands against the database
    :returns:
    """

    def __init__(self, scraper_id=None, dbo=None):

        self.id = scraper_id
        self.db = dbo
        self.rules = {}
        self.last_run_at = dt.now()  # When was the scraper bot last run
        self.current_run_at = dt.now()  # Set the initial run at value for the loop
        self.run_frequency = 1  # How many hours between runs, default to once every hour
        self.running = False
        self.state = 0  # The current state of the scraper, 1 for running, 0 for not running
        self.last_state = 0  # The very last state of the scraper, compare with current state
        # for restricting runs and too many messages
        self.enabled = True  # Enable the scraper at the start so it can run right away
        self.status_code = 0

        # Load config
        self._loadConfiguration()

    def _logLastRun(self, scraper_id):
        """

        Log the time that a scraper was last used to retrieve data from a url

        :param scraper_id:  The id of the scraper we wish to update
        :return:
        """
        print("Scraper #{}: Updating last run time.".format(self.id))
        update_sql = "UPDATE scrapers SET last_updated = ?, status_code = ? WHERE id = ?"
        update_params = [(dt.now(), self.status_code, scraper_id)]
        self.db.update(update_sql, update_params)

    def _loadConfiguration(self):
        """
        Retrieve the scrapers rules and other config information from the database

        :return:
        """
        print("Scraper #{}: Loading configuration.".format(self.id))
        config_sql = "SELECT search_terms, timeout, last_updated, run_frequency FROM scrapers WHERE id = ?"
        id_param = [(self.id)]
        config_results = self.db.query(config_sql, id_param)

        for conf in config_results:
            self.terms = conf[0]
            self.timeout = conf[1]
            self.last_updated = conf[2]
            self.run_frequency = conf[3]

        # Rules
        print("Scraper #{}: Loading processing rules.".format(self.id))
        rules_sql = "SELECT name, value FROM rules WHERE scraper_id = ?"
        rules_results = self.db.query(rules_sql, id_param)

        # Format the rules into a dictionary of {'rule_name': 'rule_value'}
        for rule in rules_results:
            self.rules[rule[0]] = rule[1]

    def _save_search_results(self):
        """
        Save the raw search results into the database
        :return:
        """

        task_start = perf_counter()
        task_start_dt = dt.now()

        print("Scraper #{}: Saving search results.".format(self.id))

        # Save the data
        save_raw_data_sql = "INSERT INTO raw_data(scraper_id, date_time, content, http_code) values(?, ?, ?, ?)"
        save_raw_data = [(self.id, task_start_dt, self.response.text, self.response.status_code)]
        self.db.execute(save_raw_data_sql, save_raw_data)

        task_end = perf_counter()
        task_end_dt = dt.now()
        task_duration = task_end - task_start

        # Save the task stats to the database
        self.db.log_task(self.id, task_start_dt, task_end_dt, 'save-raw-data', self.response.status_code,
                         '', '', task_duration, 'scraper')

    def _get_search_results(self):
        """
        Extract the search results from the target url

        :returns:
        """

        # TODO: Handle pagination

        print("Scraper #{}: Retrieving data from target URL.".format(self.id))
        # Get the specified url and parameters and store ready to be processed later
        try:
            task_start = perf_counter()
            task_start_dt = dt.now()

            self.response = requests.get("{}/{}".format(self.rules['url'], self.terms), timeout=self.timeout)

            task_end = perf_counter()
            task_end_dt = dt.now()
            task_duration = task_end - task_start

            self.status_code = self.response.status_code

            # Record the task details to the log
            self.db.log_task(self.id, task_start_dt, task_end_dt, 'extract-data', self.status_code,
                             'GOOD', '', task_duration, 'scraper')

            return True
        except requests.Timeout as err_timeout:
            print("Request to {} timed out using search terms: {}".format(self.rules['url'], self.terms))
            self.response = None
            return False
        except requests.ConnectionError as err_connect:
            print("Unable to connect to {}".format(self.rules['url']))
            self.response = None
            return False
        except requests.HTTPError as err_http:
            print("We have received HTTP error code {}".format(self.status_code))
            self.response = None
            return False
        except requests.RequestException as err_req:
            print("We have encountered an error in the requests library")
            self.response = None
            return False

    def update(self):

        self.current_run_at = dt.now()

        duration = (self.current_run_at - self.last_run_at).total_seconds()
        time_to_elapse = self.run_frequency * 3600

        if duration >= time_to_elapse:
            self.enabled = True
            self.last_run_at = self.current_run_at
        else:
            self.enabled = False

    def _process_data(self):
        """

        Processes the data returned by the requests library and applies the custom rules to
        extract the relevant data from it.

        :return:
        """

        task_start = perf_counter()
        task_start_dt = dt.now()

        print("Scraper #{}: Processing retrieved data.".format(self.id))

        # Search data returned OK, lets parse the hell out of it
        if self.status_code == 200:

            self.soup = BS(self.response.text, 'html.parser')

            # Extract the rules to be uses
            if self.rules['searches']:
                searchesRule = self.rules['searches'].split("/")

            if self.rules['products']:
                productsRule = self.rules['products'].split("/")

            if self.rules['title']:
                productTitleRule = self.rules['title'].split("/")

            if self.rules['price']:
                productPriceRule = self.rules['price'].split("/")

            if self.rules['stock']:
                productStockRule = self.rules['stock'].split("/")

            # Get the main body of search results
            resultset = self.soup.find_all(attrs={searchesRule[0]: searchesRule[1]})

            # Now find all the individual items

            item_count = 0

            for result in resultset:
                items = result.find_all(attrs={productsRule[0]: productsRule[1]})

                # Now for each individual item, extract the relevant data
                for item in items:

                    item_count += 1

                    # Check we have data
                    if item.find(attrs={productTitleRule[0]: productTitleRule[1]}):
                        title = item.find(attrs={productTitleRule[0]: productTitleRule[1]}).text

                    if item.find(attrs={productPriceRule[0]: productPriceRule[1]}):
                        price = item.find(attrs={productPriceRule[0]: productPriceRule[1]}).text.strip(' ')

                    # Only print if the title matches all search terms we want
                    if title == self.terms and not allResults:
                        print("{} [ {} ]".format(title, str(price).strip()))
                    else:
                        print("{} [ {} ]".format(title, str(price).strip()))

            return item_count

        task_end = perf_counter()
        task_end_dt = dt.now()
        task_duration = task_end - task_start

        # Record the task details to the log
        self.db.log_task(self.id, task_start_dt, task_end_dt, 'process-data', self.status_code,
                         'GOOD', '', task_duration, 'scraper')

    def run(self, allResults=True):
        """

        Performs the main function of the scraper, extracting and then processing the data

        :param allResults:      Controls if we wish to see all results or only the first entry returned
        :return:
        """

        task_start = perf_counter()
        task_start_dt = dt.now()

        self.running = True
        self.last_state = self.state
        self.state = 1

        current_run_at = dt.now()

        print("Scraper #{}: Starting main execution.".format(self.id))

        items_found = 0

        # Perform the search against the website
        if self._get_search_results():
            # Save the the raw data
            self._save_search_results()
            self._logLastRun(self.id)
            items_found = self._process_data()

        self.running = False
        self.state = 0
        self.enabled = False  # Disable the scraper for the allocated duration
        self.last_run_at = current_run_at

        task_end = perf_counter()
        task_end_dt = dt.now()
        task_duration = task_end - task_start

        # Record the task details to the log
        self.db.log_task(self.id, task_start_dt, task_end_dt, 'scraper-run', self.status_code,
                         'GOOD', '', task_duration, 'scraper')

        print("Scraper #{}: Finished main execution.".format(self.id))

        return items_found
