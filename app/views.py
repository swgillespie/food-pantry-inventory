from flask import Blueprint, render_template, g, redirect, request
from app.decorators import requires_login
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