from flask import Blueprint, render_template, g, redirect, request, url_for, flash
# suppress pyflakes warning
# from app.decorators import requires_login
from app.forms import LoginForm, RegistrationForm


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
