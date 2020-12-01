""" Database wrapper class

Wrapper class for connecting to a sqlite3 database

This script is intended to be imported from other scripts and not
run on it's own.

"""
import sqlite3
import os.path


# TODO: Move to SQLAlchemy to utilise any number of DBs
# TODO: Update class documentation

class DbSqlite3Wrapper:
    """
    A wrapper class for the sqlite3 module

    Attributes
    ----------
    conn :  Connection
        The connection to the sqlite3 database file or in memory object

    curs : Cursor
        The cursor to run sql statements against the db

    results : list
        Holds the rows from the database returned by a query string

    db_file : str
        Stores the path and name of the database file to open

    Methods
    -----------
    connect(db_file)
        Connects to the database passed into the method

    close()
        Close the opened connection to the database

    create_table(table_sql)
        Create a table within the database

    query(query_sql, query_params)
        Run the supplied query statement against the database, returns a list of the
        data found by the sql

    execute(cmd_sql, query_values)
        Run a sql command against the database and does not return anything

    update(cmd_sql, cmd_values)
        Updates an entry in the database
    """

    def __init__(self, db_file):
        """ Standard class initializer method
        :param db_file: The name and path to the database file
        :returns: Nothing
        """
        self.db_file = db_file
        self.conn = None
        self.curs = None

    def log_task(self, id, start_dt, end_dt, task_name, http_code=None, status_code=None, content=None,
                 duration=None, owner='scraper'):
        """
        Logs a task into the database

        :param id:              The ID of the process logging the task
        :param start_dt:        The start time of the task
        :param end_dt:          The end time of the task
        :param task_name:       The name of the task being performed
        :param http_code:       The http_status code of the task, if any
        :param status_code:     The general status code of the task, if any
        :param content:         Any content relevant to the task like error messages, if any
        :param duration:        How long the task took to run
        :param owner:           The process that owns this message
        :return:
        """

        log_sql = "INSERT INTO scrapers_log(scraper_id, started, ended, task, http_code, status_code, content, " \
                  "duration, owner) " \
                  "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"

        log_values = [(id, start_dt, end_dt, task_name, http_code, status_code, content, duration, owner)]

        self.execute(log_sql, log_values)

    def connect(self):
        """Connects to the requested database
        :returns: nothing
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.curs = self.conn.cursor()
        except sqlite3.Error as err:
            print(err)

    def close(self):
        """Closes the connection to the database
        :returns: Nothing
        """
        if self.conn:
            self.conn.close()

    def create_table(self, table_sql):
        """Create a table within the database

        :param table_sql: The SQL that will be executed to created the table
        :returns: Nothing
        """
        try:
            self.curs.execute(table_sql)
            return True
        except sqlite3.ProgrammingError as prog_err:
            print(prog_err)
            return False

    def query(self, query_sql, query_params=[]):
        """Performs a query against the database

        :param query_sql: The sql you wish to be executed against the database
        :param query_params: Any paramitesed query values needed to be added to the sql
        :returns: An iterable resultset of data
        """
        try:
            if len(query_params) == 0:
                self.curs.execute(query_sql)
                return self.curs.fetchall()
            else:
                self.curs.execute(query_sql, query_params)
                return self.curs.fetchall()
        except sqlite3.OperationalError as op_err:
            print(op_err)
        except sqlite3.ProgrammingError as prog_err:
            print(prog_err)
        except sqlite3.Error as err:
            print(err)

    def execute(self, cmd_sql, query_values=[]):
        """Executes a sql command against the database and returns nothing

        :param cmd_sql: The sql you desire to execute against the database
        :param query_values: A list of tuples contain the data to insert
        :returns: Nothing
        """
        try:
            if len(query_values) == 0:
                self.curs.execute(cmd_sql)
                self.conn.commit()
            else:
                self.curs.executemany(cmd_sql, query_values)
                self.conn.commit()
        except sqlite3.OperationalError as op_err:
            print(op_err)
        except sqlite3.ProgrammingError as prog_err:
            print(prog_err)
        except sqlite3.Error as err:
            print(err)

    def update(self, cmd_sql, cmd_values=[]):
        """
        Update one or more records in the database

        :param cmd_sql:         The update statement to run
        :param cmd_values:      The required params for the sql
        :return:
        """
        try:
            self.curs.executemany(cmd_sql, cmd_values)
            self.conn.commit()
        except sqlite3.Error as err:
            print(err)

    def setup_scrapers_db(self):
        """

        Creates the scarpers database locally

        :return:
        """

        # SQL for creating tables
        scrapers_table_sql = "CREATE TABLE scrapers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NULL, " \
                             "enabled INTEGER DEFAULT 0, " \
                             "last_updated TEXT NULL, status_code INTEGER NULL, customer_id INTEGER NOT NULL, " \
                             "timeout INTEGER NOT NULL DEFAULT 30, " \
                             "created_at TEXT DEFAULT (DATETIME('now','localtime'))" \
                             ", search_terms TEXT NOT NULL, run_frequency INTEGER NOT NULL DEFAULT 1" \
                             ")"

        customers_table_sql = "CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NULL" \
                              ", created_at TEXT DEFAULT (DATETIME('now','localtime')))"

        rules_table_sql = "CREATE TABLE rules(id INTEGER PRIMARY KEY, name TEXT NOT NULL, value TEXT NULL, " \
                          "scraper_id INTEGER NOT NULL, customer_id INTEGER NOT NULL" \
                          ", created_at TEXT DEFAULT (DATETIME('now','localtime')))"

        scrapers_log_sql = "CREATE TABLE scrapers_log(id INTEGER PRIMARY KEY, scraper_id INTEGER NOT NULL, started REAL TEXT," \
                           "ended TEXT NULL, task TEXT NOT NULL, http_code INTEGER NULL, status_code NULL, " \
                           "content TEXT NULL, duration REAL NULL, owner TEXT NOT NULL)"

        raw_data_sql = "CREATE TABLE raw_data(id INTEGER PRIMARY_KEY, scraper_id INTEGER NOT NULL, date_time TEXT NOT NULL, " \
                       "content TEXT NULL, http_code INTEGER NOT NULL)"

        print("Creating database and tables in {}".format(self.db_file))

        if self.conn:
            self.create_table(scrapers_table_sql)
            self.create_table(customers_table_sql)
            self.create_table(rules_table_sql)
            self.create_table(scrapers_log_sql)
            self.create_table(raw_data_sql)

    def scrapers_sample_data(self):
        """

        Adds sample data for testing to the database

        :return:
        """

        # List of tuples containing the data to be inserted into the database
        scrapers = [
            (1, 'argos-xbox', 'Scraper for the argos search page', 1, 1, 'xbox series x', 0.0833),
            (2, 'wickes-bath-taps', 'Scraper for the wickes search page', 1, 2, 'bath taps', 0.0833)
        ]

        customers = [
            (1, 'argos', ''),
            (2, 'wickes', '')
        ]

        argos_rules = [
            ('url', 'https://www.argos.co.uk/search', 1, 1),
            ('searches', 'class/search', 1, 1),
            ('products', 'class/ProductCardstyles__Wrapper-l8f8q8-1', 1, 1),
            ('title', 'class/ProductCardstyles__Title-l8f8q8-12', 1, 1),
            ('price', 'class/ProductCardstyles__PriceText-l8f8q8-14', 1, 1),
            ('stock', '', 1, 1)
        ]

        wickes_rules = [
            ('url', 'https://www.wickes.co.uk/search?text=', 2, 2),
            ('searches', 'class/products-list', 2, 2),
            ('products', 'class/card', 2, 2),
            ('title', 'class/product-card__title', 2, 2),
            ('price', 'class/product-card__price', 2, 2),
            ('stock', '', 2, 2)
        ]

        # SQL to run to actually insert the data
        scrapers_sql = "INSERT INTO scrapers(id,name,description,enabled,customer_id, search_terms, run_frequency) " \
                       "VALUES(?,?, ?, ?, ?, ?, ?)"
        customers_sql = "INSERT INTO customers(id,name,description) VALUES(?,?, ?)"
        rules_sql = "INSERT INTO rules(name,value,scraper_id,customer_id) VALUES(?, ?, ?, ?)"

        # Now insert the data
        self.execute(scrapers_sql, scrapers)
        self.execute(customers_sql, customers)
        self.execute(rules_sql, argos_rules)
        self.execute(rules_sql, wickes_rules)
