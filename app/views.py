from flask import Blueprint, render_template
from app.decorators import requires_login

mod = Blueprint('tools', __name__, url_prefix='/')

@mod.route('/')
def home():
    return render_template('login.html')