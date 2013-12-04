import threading
import sqlite3
from functools import wraps
import hashlib
import os

SCHEMA_FILE = os.path.join(os.path.abspath('app'), 'schema.sql')

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
        data = self._row_to_dict(result)
        return data[0] if len(data) > 0 else None
    
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
        self._sqlconn.commit()

    @requires_lock
    def do_drop_off(self, deliveries):
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
                'INSERT INTO dropoff_transaction (date, qty, source_name, product_name) ',
                'VALUE (date(\'now\'), ?, ?, ?)'
            ]), (delivery['qty'], delivery['source'], delivery['product']))
        self._sqlconn.commit()
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
        result = self._sqlconn.execute(''.join([
            'INSERT INTO clients (gender, dob, start_date, street, city, state, zip, ',
            'apartment, firstname, lastname, phone, bag_name, pickup_day)',
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        ]), (
            client_dictionary['gender'],
            client_dictionary['dob'],
            client_dictionary['start'],
            client_dictionary['date'],
            client_dictionary['street'],
            client_dictionary['city'],
            client_dictionary['state'],
            client_dictionary['zip'],
            client_dictionary['apartment'],
            client_dictionary['firstname'],
            client_dictionary['lastname'],
            client_dictionary['phone'],
            client_dictionary['bag'],
            client_dictionary['name'],
            client_dictionary['pickup_day']
        ))
        self._sqlconn.commit()
        print "Client addition complete"        

    @requires_lock
    def do_add_family(self, family_dictionary):
        '''
        Given a dictionary witih a family's information, insert
        into families table.
        '''
        result = self._sqlconn.execute(''.join([
            'INSERT INTO family_members (firstname, lastname, dob, gender, client_id) ',
            'VALUES (?, ? ?, ?, ?)'
        ]), (
            family_dictionary['firstname'],
            family_dictionary['lastname'],
            family_dictionary['dob'],
            family_dictionary['gender'],
            family_dictionary['client_id']
        ))
        self._sqlconn.commit()
        print "Family addition complete"

    @requires_lock
    def do_view_bag(self, bag_name):
        '''
        Performs a query that returns the contents of a bag named bag_name.
        '''
        result = self._sqlconn.execute(''.join([
            'SELECT * FROM bag_holds LEFT OUTER JOIN products ',
            'ON bag_holds.product_name = products.name ',
            'WHERE bag_holds.bag_name = ? ',
            'ORDER BY products.name'
        ]), (bag_name,))
        return self._row_to_dict(result)

    @requires_lock
    def do_add_product(self, bag_name, product_name, qty, last_qty):
        '''
        Adds qty number of product_name to the bag bag_name
        '''
        result = self._sqlconn.execute(''.join([
            'SELECT * FROM bag_holds LEFT OUTER JOIN products ',
            'ON bag_holds.product_name = products.name ',
            'WHERE bag_holds.bag_name = ? AND products.name = ?'
        ]), (bag_name, product_name))
        if len([x for x in result]) != 0:
            print "product {} is already in bag {}".format(product_name, bag_name)
        else:
            result = self._sqlconn.execute(''.join([
                'INSERT INTO bag_holds (current_qty, last_month_qty, bag_name, product_name) ',
                'VALUES (?, ?, ?, ?)'
            ]), (qty, last_qty, bag_name, product_name))
            self._sqlconn.commit()
        print "product {} added to bag {}".format(product_name, bag_name)

    @requires_lock
    def do_remove_product(self, bag_name, product_name):
        '''
        Removes product_name from a bag called bag_name
        '''
        result = self._sqlconn.execute(''.join([
            'DELETE FROM bag_holds ',
            'WHERE bag_holds.product_name = ? AND bag_name = ?'
        ]), (product_name, bag_name))
        self._sqlconn.commit()
        print "product {} removed from bag {}".format(product_name, bag_name)

    @requires_lock
    def do_edit_product_qty(self, bag_name, product_name, qty):
        '''
        Changes the quantity of the product product_name in bag_name to qty.
        '''
        result = self._sqlconn.execute(''.join([
            'UPDATE bag_holds ',
            'SET current_qty=? ',
            'WHERE bag_holds.bag_name = ? AND bag_holds.product_name = ?'
        ]), (bag_name, product_name))
        self._sqlconn.commit()
        print "product {} updated to qty {}".format(product_name, qty)

    @requires_lock
    def do_list_products(self):
        '''
        Returns a list of all products currently in the food pantry.
        '''
        result = self._sqlconn.execute(''.join([
            'SELECT * FROM products ',
            'ORDER BY name'
        ]))
        return self._row_to_dict(result)

    @requires_lock
    def do_add_new_product(self, product_dictionary):
        '''
        Given a dictionary with a product's information, insert into
        products table.
        '''
        result = self._sqlconn.execute(''.join([
            'INSERT INTO products (name, cost, source_name) ',
            'VALUES (?, ?, ?)'
        ]), (
            product_dictionary['name'],
            product_dictionary['cost'],
            product_dictionary['source_name']
        ))
        self._sqlconn.commit()

    @requires_lock
    def do_monthly_service_report(self):
        '''
        Generates a monthly service report.
        '''
        result_list = []
        client_ids = self._sqlconn.execute(''.join([
            'SELECT id FROM clients'
        ]))
        for row in client_ids:
            client_id = row['id']
            result = self._sqlconn.execute(''.join([
                "SELECT * FROM ",
                "(SELECT COUNT(*) AS under18 FROM family_members ",
                "WHERE client_id = ? AND strftime('%Y', 'now') - strftime('%Y', dob) < 18)  ",
                "(SELECT COUNT(*) AS 19to64 FROM family_members ",
                "WHERE client_id = ? AND strftime('%Y', 'now') - strftime('%Y', dob) BETWEEN 19 AND 65) ",
                "(SELECT COUNT(*) AS 65plus FROM family_members ",
                "WHERE client_id = ? AND strftime('%Y', 'now') - strftime('%Y', dob) > 65)"
            ]), (client_id, client_id, client_id))
            result_dict = self._row_to_dict(result)
            result_list.append(result_dict)
        out_dict = {}
        out_dict['num_clients'] = len(result_dict)
        out_dict['num_people'] = sum([x['under18'] + x['19to64'] + x['65plus'] for x in result_list]) + out_dict['num_clients']
        result = self._sqlconn.execute(''.join([
            'SELECT SUM(cost) AS total_cost ', 
            '(SELECT product_name FROM ',
            '(SELECT id, bag_name FROM clients WHERE pickup_day IN week) AS temp ',
            'LEFT OUTER JOIN bag_holds ON temp.bag_name = bag_holds.bag_name) AS temp2 ',
            'LEFT OUTER JOIN products ON products.name = temp2.product_name'
        ]))
        out_dict['total_cost'] = result['total_cost']
        return out_dict
        

    @requires_lock
    def do_grocery_list_report(self):
        '''
        Generates a grocery list report.
        '''
        result = self._sqlconn.execute(''.join([
            'SELECT h.product_name AS name, SUM(h.current_qty) AS current_qty, SUM(h.last_month_qty) AS last_month_qty ',
            'FROM bag_holds AS h, clients AS c ',
            'WHERE c.bag_name = h.bag_name ',
            'GROUP BY h.product_name'
        ]))
        return self._row_to_dict(result)