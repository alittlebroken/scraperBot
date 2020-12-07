# Imports
from scraper import ScraperBot
from datetime import datetime as dt


class ScraperFactory:
    """

    Factory method to run individual scraper bots

    :param dbo: Database object for querying and executing commands

    :returns:

    _update_scraper_list(dbo)
        Sets in the DB the last time a scraper ran

    _update_scraper_list()
        This gets a list from the DB of all enabled scrapers. If the scraper is already
        in the internal scraper list then it is removed so it no longer runs

    _load_scrapers()
        Generates a new scraper object and adds it to the internal DB

    _getScrapers()
        Retrueves a list of all enabled scrapers from the DB

    _addScrapers(scraper_id, scraper_obj)
        Adds a scraper to the internal scraper list

    _delScraper(scraper_id)
        Deletes a scraper from the internal scraper list

    run()
        Runs each scraper bot in turn and at specified intervals
    """

    # TODO: Add in logging to local log

    def __init__(self, dbo):
        self.dbo = dbo  # DB Object
        self.scrapers = {}  # List of active scrapers
        self.app_loop = True  # The main application loop

        # Get the list of active scrapers and add them to the list to be run later
        self._load_scrapers()

        self.this_tick = dt.now()  # Records the current time in the main loop
        self.last_tick = dt.now()  # Keeps track of the previous time in the main loop

    def _update_scraper_list(self):
        """

        Updates the internal list of scrapers, removes disabled scrapers and adds new ones if needed

        :return:
        """
        scraper_sql = "SELECT id FROM scrapers"

        # The following sql only extracts the enabled scrapers from the DB
        scrapers_sql = "SELECT id, enabled from scrapers"
        # Execute the query and return the list
        scrapers = self.dbo.query(scrapers_sql)

        # Now for each record returned, check if it is in the list already. If it is and it should
        # disabled now, remove it from the list. Otherwise, add it to the list
        for scraper in scrapers:
            if scraper[0] in self.scrapers and scraper[1] == 0:
                self._delScraper(scraper[0])
            elif scraper[0] not in self.scrapers and scraper[1] == 1:
                self._addScraper(scraper[0], ScraperBot(scraper[0], self.dbo))

    def _load_scrapers(self):
        """

        Retrieves from the DB the current list of active scrapers

        :return:
        """
        active_scrapers = self._getScrapers()

        if active_scrapers is not None:
            for active_scraper in active_scrapers:
                self._addScraper(active_scraper[0], ScraperBot(active_scraper[0], self.dbo))

    def _getScrapers(self):
        """Gets a list of the currently active scrapers from the database

        :return: The resultset of the enabled scrapers from the database
        """
        print("ScraperFactory: Getting list of active scrapers.")
        # The following sql only extracts the enabled scrapers from the DB
        scraper_enabled_sql = "SELECT id from scrapers where enabled = 1"
        # Execute the query and return the list
        return self.dbo.query(scraper_enabled_sql)

    def _addScraper(self, scraper_id, scraper_obj):
        """Adds a scraper to the active scrapers list

        :param scraper_id:   The ID to identify this scraper in the internal list
        :param scraper_obj:  The scraper object to add to the list
        """
        # Only add new scrapers to the list
        print("ScraperFactory: Adding scraper to internal list.")
        if scraper_id not in self.scrapers:
            self.scrapers[scraper_id] = scraper_obj

    def _delScraper(self, scraper_id):
        """Deletes a scraper from the internal scraper list

        :param scraper_id:
        :return: Nothing
        """
        print("ScraperFactory: Deleting scraper from internal list.")
        if scraper_id in self.scrapers:
            del (self.scrapers[scraper_id])

    def run(self):
        """
        Runs each of the scraper bots in turn

        :return: Nothing
        """

        # Print out some information
        print("We have {} scraper(s) to run.".format(len(self.scrapers)))

        while self.app_loop:

            # Update internal list of scrapers
            self._update_scraper_list()

            for idx, scraper in self.scrapers.items():
                # Only run the scraper if the scrapers run frequency has been exceeded

                # Update the timings for the scraper
                scraper.update()

                if scraper.enabled:
                    print("Running scraper bot #{}".format(idx))
                    num_found = scraper.run()
                    print("Scraper scraped {} entries from the specified url".format(num_found))
                    print("Last run: {}".format(scraper.last_run_at))
