from flask import Blueprint, render_template, g, redirect, request, url_for
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
    