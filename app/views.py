from flask import Blueprint, render_template, g, redirect, request
from app.decorators import requires_login
from app.forms import LoginForm, RegistrationForm
from app.db import DBInterface

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
    if not hasattr(g, sqlite_db):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_environment
def close_db(error):
    if hasattr(g, sqlite_db):
        g.sqlite_db.close()

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