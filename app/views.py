from flask import Blueprint, render_template, g, redirect, request, url_for, flash, abort, session
from app.decorators import requires_login
from app.forms import LoginForm, RegistrationForm, DropoffForm, NewProductForm
import base64
from app.db import DBInterface
from app import app

mod = Blueprint('tools', __name__, url_prefix='/')

def connect_db():
    conn = DBInterface(app.config['DATABASE'])
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.execute_script(f.read())

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@mod.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return render_template('index.html')
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        success = db.do_login(form.username.data, form.password.data)
        if success:
            session['logged_in'] = True
            session['user'] = form.username.data
            flash("You are logged in!")
            return render_template('index.html')
        else:
            print "Login failed"
            flash("Login information incorrect.")
    return render_template('login.html', form=form)

@mod.route('logout', methods=['GET'])
def logout():
    del session['logged_in']
    del session['user']
    return redirect('/')
    
@mod.route('register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        db.do_register(form.username.data, form.lastname.data,
                       form.firstname.data, form.email.data,
                       form.password.data, form.is_director.data)
        flash("Thanks for registering!")
        return redirect('/')
    return render_template('register.html', form=form)

@mod.route('pickup/', methods=['GET', 'POST'])
def pickup():
    if request.method == 'GET':
        return render_template('pickup.html')
    elif request.method == 'POST':
        if 'pickup' in request.form:
            pickup_day = request.form['pickup']
            db = get_db()
            result = db.do_pickup_query(pickup_day)
            if len(result) == 0:
                flash("No pickups found on this day.")
            print result
            return render_template('pickup.html', rows=result)
    # other methods are not supported
    return render_template('pickup.html')

@mod.route('pickup/<int:client_id>/', methods=['GET', 'POST'])
def family_pickup(client_id):
    if request.method == 'GET':
        ## BEGIN DB TRANSACTION
        db = get_db()
        client = db.client_lookup_by_id(client_id)
        if client is None:
            abort(404) # not found
        family_bag = db.do_family_bag_show(client_id)
        return render_template('family_pickup.html', client=client,
                               rows=family_bag)
    elif request.method == 'POST':
        ## BEGIN DB TRANSACTION
        db = get_db()
        db.do_family_bag_pickup(client_id)
        flash("Client {} has successfully picked up their bag.".format(client_id))
        return render_template('pickup.html')
    # other methods not supported
    return redirect('/pickup/')

@mod.route('clients/', methods=['GET'])
def clients():
    # nothing to do here but render the template response
    return render_template('clients.html')

@mod.route('clients/list/', methods=['GET', 'POST'])
def client_list():
    # TODO
    return render_template('client_list.html')

@mod.route('clients/new/', methods=['GET', 'POST'])
def new_client():
    # TODO
    return render_template('new_client.html')

@mod.route('bag_list/', methods=['GET'])
def bag_list():
    db = get_db()
    bags = db.do_bag_list()
    for bag in bags:
        bag['bagnameEnc'] = base64.b16encode(bag['bag_name'])
    return render_template('bag_list.html', bags=bags)

@mod.route('viewEditBag/<string:bagnameEnc>/', methods=['GET', 'POST'])
def view_edit_bag(bagnameEnc):
    bagname = base64.b16decode(bagnameEnc)
    if request.method=='GET':
    ## BEGIN DB TRANSACTION
        db = get_db()
        bag = db.do_view_bag(bagname)
    elif request.method=='POST':
        db = get_db()
        product_name=request.form['product_name']
        qty = request.form['qty']
        if qty == '0':
            print "removing a product"
            db.do_remove_product(bagname, product_name)
        else:
            db.do_edit_product_qty(bagname, product_name, qty)
        flash("Bag updated!")
        return redirect('viewEditBag/{}'.format(bagnameEnc))
    ## END DB TRANSACTION
    return render_template('viewEditBag.html', bag=bag, bagname=bagname, bagnameEnc=bagnameEnc)

@mod.route('dropoff/', methods=['GET', 'POST'])
def dropoff():
    form = DropoffForm(request.form)
    if request.method == 'GET':
        return render_template('dropoff.html', form=form)
    elif request.method == 'POST' and form.validate():
    ## BEGIN DB TRANSACTION
        print ">>>NEW DROPOFF: product: {}, source: {}, qty: {}".format(
            form.product.data, form.source.data, form.qty.data
        )
    ## END DB TRANSACTION
        
    return render_template('dropoff.html', form=form)



@mod.route('products/', methods=['GET'])
def products():
    return render_template('products.html')

@mod.route('products/list/', methods=['GET', 'POST'])
def product_list():
    if request.method=='GET':
        ## BEGIN DB TRANSACTION
        products = [
            { 'product': 'milk', 'source':'Kroger', 'cost': 2.23 },
            { 'product': 'cookies', 'source': 'Kroger','cost': 1.54 },
            { 'product': 'pretzels', 'source': 'Trader Joe''s','cost': 0.59 },
            { 'product': 'crackers', 'source': 'Trader Joe''s', 'cost': 4.32 }
        ]
        ## END DB TRANSACTION
        return render_template('product_list.html', products=products)
    elif request.method=='POST':
        product_name=request.form['product_name']
        ## BEGIN DB TRANSACTION
        products = [
            { 'product': 'milk', 'source':'Kroger', 'cost': 2.23 },
        ]
        print ">>>USER PRODUCT SEARCH: The user searched for product {}.".format(product_name)
        ## END DB TRANSACTION
        return render_template('product_list.html', products=products)
    return render_template('product_list.html')

@mod.route('products/new/', methods=['GET', 'POST'])
def new_product():
    form = NewProductForm(request.form)
    if request.method == 'GET':
        return render_template('new_product.html', form=form)
    elif request.method == 'POST' and form.validate():
    ## BEGIN DB TRANSACTION
        print ">>>NEW PRODUCT: product: {}, source: {}, cost-per-unit: {}".format(
            form.product.data, form.source.data, form.cost.data
        )
    ## END DB TRANSACTION
        return redirect('/products/new/')
    return render_template('new_product.html', form=form)

