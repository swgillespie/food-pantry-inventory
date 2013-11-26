import threading
import sqlite3
from functools import wraps

class DBInterface(object):

    def __init__(self, dbname):
        '''
        Initializes a new DB connection to the database named
        dbname.
        '''
        self._sqlconn = sqlite3.connect(dbname)
        self._sqlconn.row_factory = sqlite3.Row
        # lock is necessary since sqlite is not thread-safe
        self._lock = threading.Lock()

    def requires_lock(func):
        '''
        Function decorator that acquires a mutex lock before
        interacting with the database.
        '''
        @wraps(func)
        def _lock(self, *args, **kwargs):
            self._lock.acquire()
            retval = func(self, *args, **kwargs)
            self._lock.release()
            return retval
        return _lock

    @requires_lock
    def execute_script(self, script):
        self._sqlconn.executescript(script)
        self._sqlconn.commit()

    @requires_lock
    def close(self):
        self._sqlconn.close()
        
    @requires_lock
    def do_login(self, username, password):
        '''
        Logs in a user. Takes the username and the SHA1 hash of the
        password and uses it to query the database. If the response
        from the DB is non-empty, it returns true, indicating a successful
        login - otherwise, it returns false.
        '''
        pass

    @requires_lock
    def do_pickup_query(self, day_of_month):
        '''
        Performs a query to find the clients that will be picking up their
        bag that day and returns the results of the query.
        '''
        pass

    @requires_lock
    def do_family_bag_pickup(self, client_id):
        '''
        Indicates to the database that a family with given client_id
        has picked up their bag.
        '''
        pass

    @requires_lock
    def do_drop_off(self, *deliveries):
        '''
        Given some number of delivery DICTIONARIES with attributes
        expected in the pseudocode, performs a drop off in the database.
        '''
        for delivery in deliveries:
            pass

    @requires_lock
    def do_search_client(self, lastname, phone):
        '''
        Search for a client using either lastname or phone.
        '''
        pass

    @requires_lock
    def do_new_client(self, client_dictionary):
        '''
        Given a dictionary with the Client's information, insert
        into the clients table.
        '''
        pass

    @requires_lock
    def do_add_family(self, family_dictionary):
        '''
        Given a dictionary witih a family's information, insert
        into families table.
        '''
        pass

    @requires_lock
    def do_view_bag(self, bag_name):
        '''
        Performs a query that returns the contents of a bag named bag_name.
        '''
        pass

    @requires_lock
    def do_add_product(self, bag_name, product_name, qty):
        '''
        Adds qty number of product_name to the bag bag_name
        '''
        pass

    @requires_lock
    def do_remove_product(self, bag_name, product_name):
        '''
        Removes product_name from a bag called bag_name
        '''
        pass

    @requires_lock
    def do_list_products(self):
        '''
        Returns a list of all products currently in the food pantry.
        '''
        pass

    @requires_lock
    def do_add_new_product(self, product_dictionary):
        '''
        Given a dictionary with a product's information, insert into
        products table.
        '''
        pass

    @requires_lock
    def do_monthly_service_report(self):
        '''
        Generates a monthly service report.
        '''
        pass

    @requires_lock
    def do_grocery_list_report(self):
        '''
        Generates a grocery list report.
        '''
        pass