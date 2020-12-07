# main.py A python web scraper
# Paul Lockyer (plockyer@googlemail.com)
# 2020-10-21

# TODO: Redo file to use new classes and methods

# ## Imports ##
from ScraperConfig import configuration
from database import DbSqlite3Wrapper
from ScraperFactory import ScraperFactory

# Perform some setup and create the initial objects
database = DbSqlite3Wrapper(configuration['database_name'])
database.connect()
factory = ScraperFactory(database)


def main():
    """

    Runs the application

    :return:
    """
    factory.run()


if __name__ == '__main__':
    # Run the application
    main()

database.close()
