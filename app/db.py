import threading
import sqlite3
from functools import wraps
import logging
import hashlib

SCHEMA_FILE = 'schema.sql'

class DBInterface(object):
    
    def __init__(self, dbname):
        '''
        Initializes a new DB connection to the database named
        dbname.
        '''
        print 'DBInterface __init__'
        self._sqlconn = sqlite3.connect(dbname)
        self._sqlconn.row_factory = sqlite3.Row
        # lock is necessary since sqlite is not thread-safe
        self._lock = threading.Lock()
        self._init()
        
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

    def _init(self):
        response = self._sqlconn.execute('SELECT * FROM sqlite_master;')
        if len([x for x in response]) == 0:
            print "Database needs to be initialized" 
            self.execute_script(open(SCHEMA_FILE, 'r').read())
        print "Database initialization complete"

    def _row_to_dict(self, row_in):
        list_out = []
        for row in row_in:
            temp = {}
            for key in row.keys():
                temp[key] = row[key]
            list_out.append(temp)
        return list_out
        
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
        print 'login from user {} with password {}'.format(username, password)
        sha1pass = hashlib.sha1(password).hexdigest()
        result = self._sqlconn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                                       (username, sha1pass))
        return len([x for x in result]) != 0

    @requires_lock
    def do_register(self, username, last, first, email, passwd, is_director):
        print 'registration from user {} with name {} {}'.format(username, last, first)
        sha1pass = hashlib.sha1(passwd).hexdigest()
        result = self._sqlconn.execute(''.join([
            'INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);'
        ]), (username, sha1pass, first, last, email, is_director))
        print 'table insertion successful'
        self._sqlconn.commit()

    @requires_lock
    def client_lookup_by_id(self, client_id):
        result = self._sqlconn.execute(''.join([
            'SELECT * FROM clients WHERE id = ?'
        ]), (client_id,))
        return self._row_to_dict(result)[0]
    
    @requires_lock
    def do_pickup_query(self, day_of_month):
        '''
        Queries the database to find the users picking up on a certain day.
        '''
        print "pickup query for day {}".format(day_of_month)
        result = self._sqlconn.execute(''.join([
            'SELECT lastname, firstname, family_size, street, city, state, zip, apartment, phone, pickup_day ',
            'FROM clients_with_family_size ',
            'WHERE pickup_day = ?'
        ]), (day_of_month,))
        return self._row_to_dict(result)

    @requires_lock
    def do_family_bag_show(self, client_id):
        '''
        Returns the contents of a family's bag.
        '''
        print "family bag show for {}".format(client_id)
        self._lock.release()
        client = self.client_lookup_by_id(client_id)
        self._lock.acquire()
        if client['bag_name'] is None:
            return []
        result = self._sqlconn.execute(''.join([
            'SELECT p.name, h.current_qty ',
            'FROM bag_holds AS h, products AS p ',
            'WHERE h.product_name = p.name AND h.bag_name = ?'
        ]), (client['bag_name'],))
        return self._row_to_dict(result)
        
    @requires_lock
    def do_family_bag_pickup(self, client_id):
        '''
        Indicates to the database that a family with given client_id
        has picked up their bag on the given day.
        '''
        print "family bag pickup for {}".format(client_id)
        self._lock.release()
        client = self.client_lookup_by_id(client_id)
        self._lock.acquire()
        result = self._sqlconn.execute(''.join([
            'INSERT INTO pickup_transaction (pickup_date, client_id, bag_name) ',
            'VALUES (?, ?, ?)'
        ]), (client['pickup_day'], client['id'], client['bag_name']))
        print "pickup complete"

    @requires_lock
    def do_drop_off(self, *deliveries, date):
        '''
        Given some number of delivery DICTIONARIES with attributes
        expected in the pseudocode, performs a drop off in the database.
        '''
        print "start do drop off"
        for delivery in deliveries:
            result = self._sqlconn.execute(''.join([
                'SELECT * FROM sources ',
                'WHERE sources.name = ?'
            ]), (delivery['source'],))
            if len([x for x in result]) == 0:
                print "source {} not in database".format(delivery['source'])
                result = self._sqlconn.execute(''.join([
                    'INSERT INTO sources(name) ',
                    'VALUES (?)'
                ]), (delivery['source'],))
            result = self._sqlconn.execute(''.join([
                'SELECT * FROM products ',
                'WHERE products.name = ?'
            ]), (delivery['product'],))
            if len([x for x in result]) == 0:
                print "product {} not in database".format(delivery['product'])
                result = self._sqlconn.execute(''.join([
                    'INSERT INTO products(name, source_name) ',
                    'VALUES (?, ?)'
                ]), (delivery['product'], delivery['source']))
            result = self._sqlconn.execute(''.join([
                'INSERT INTO dropoff_transaction (date, qty, source_name, product_name)',
                'VALUE (?, ?, ?, ?)'
            ]), (date, delivery['qty'], delivery['source'], delivery['product']))
        print "Dropoff complete"

    @requires_lock
    def do_search_client(self, lastname=None, phone=None):
        '''
        Search for a client using either lastname or phone.
        '''
        if lastname is None and phone is None:
            return []
        else:
            if not lastname is None and phone is None:
                result = self._sqlconn.execute(''.join([
                    'SELECT * FROM clients_with_family_size ',
                    'WHERE lastname = ?'
                ]), (lastname,))
            elif lastname is None and not phone is None:
                result = self._sqlconn.execute(''.join([
                    'SELECT * FROM clients_with_family_size ',
                    'WHERE phone = ?'
                ]), (phone,))
            else:
                result = self._sqlconn.execute(''.join([
                    'SELECT * FROM clients_with_family_size ',
                    'WHERE lastname = ? OR phone = ?'
                ]), (lastname,))
        return self._row_to_dict(result)

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