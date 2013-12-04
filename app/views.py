from flask import Blueprint, render_template, g, redirect, request, url_for, flash
# suppress pyflakes warning
# from app.decorators import requires_login
from app.forms import LoginForm, RegistrationForm, DropoffForm, NewProductForm
import base64


mod = Blueprint('tools', __name__, url_prefix='/')

@mod.route('/', methods=['GET', 'POST'])
def login():
    if hasattr(g, 'user'):
        redirect(url_for('home'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        ## TODO INTEGRATE WITH DB
        print "Login: username: {} password: {}".format(
            form.username.data, form.password.data
        )
        return render_template('index.html')
    return render_template('login.html', form=form)

@mod.route('register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        ## TODO INTEGRATE WITH DB
        print "New user: username: {} password: {}".format(
            form.username.data, form.password.data
        )
        return redirect('/')
    return render_template('register.html', form=form)

@mod.route('pickup/', methods=['GET', 'POST'])
def pickup():
    if request.method == 'GET':
        return render_template('pickup.html')
    elif request.method == 'POST':
        if 'pickup' in request.form:
            pickup_day = request.form['pickup']
            ## DO DB QUERY HERE 
            rows = [{
                'client_id': 42,
                'lastname': 'gillespie',
                'firstname': 'sean',
                'family_size': 8,
                'street': '123 Easy Street',
                'city': 'Compton',
                'state': 'CA',
                'zip': 12345,
                'apartment': 9999,
                'phone': '123-456-7890',
                'pickup_day': 9
            },
            {
                'client_id': 42,
                'lastname': 'gillespie',
                'firstname': 'sean',
                'family_size': 8,
                'street': '123 Easy Street',
                'city': 'Compton',
                'state': 'CA',
                'zip': 12345,
                'apartment': 9999,
                'phone': '123-456-7890',
                'pickup_day': 9
            }

            ]
            ## END DB TRANSACTION
            return render_template('pickup.html', rows=rows)
    # other methods are not supported
    return render_template('pickup.html')

@mod.route('pickup/<int:client_id>/', methods=['GET', 'POST'])
def family_pickup(client_id):
    if request.method == 'GET':
        ## BEGIN DB TRANSACTION
        client = {
            'firstname': 'sean',
            'lastname': 'gillespie',
            'id': 42
        }
        products = [
            { 'product_name': 'milk', 'current_qty': 42 },
            { 'product_name': 'cookies', 'current_qty': 11 },
            { 'product_name': 'pretzels', 'current_qty': 39 },
            { 'product_name': 'crackers', 'current_qty': 55 }
        ]
        ## END DB TRANSACTION
        return render_template('family_pickup.html', client=client, rows=products)
    elif request.method == 'POST':
        ## BEGIN DB TRANSACTION
        print "Client {} just picked up their bag".format(client_id)
        ## END DB TRANSACTION
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
    bags = [{
                'bagname': 'Family Bag 1',
                'numitems': 5,
                'numclients': 37,
                'cost': 15.64,
            },
            {
                'bagname': 'Family Bag 2',
                'numitems': 7,
                'numclients': 21,
                'cost': 23.78,
            }]
    for bag in bags:
        bag['bagnameEnc'] = base64.b16encode(bag['bagname'])
    return render_template('bag_list.html', bags=bags)

@mod.route('viewEditBag/<string:bagnameEnc>/', methods=['GET', 'POST'])
def view_edit_bag(bagnameEnc):
    bagname = base64.b16decode(bagnameEnc)
    if request.method=='GET':
    ## BEGIN DB TRANSACTION
        bag = [
            { 'product_name': 'milk', 'qty': 2 },
            { 'product_name': 'cookies', 'qty': 1 },
            { 'product_name': 'pretzels', 'qty': 2 },
            { 'product_name': 'crackers', 'qty': 5 }
        ]
    elif request.method=='POST':
        product_name=request.form['product_name']
        qty=request.form['qty']
        bag = [
            { 'product_name': 'milk', 'qty': request.form['qty'] },
            { 'product_name': 'cookies', 'qty': 1 },
            { 'product_name': 'pretzels', 'qty': 2 },
            { 'product_name': 'crackers', 'qty': 5 }
        ]
        print ">>>PRODUCT UPDATE: The qty of product {} has been updated to {}.".format(product_name, qty)
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

