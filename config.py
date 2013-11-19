import os

basedir = os.path.abspath(os.path.dirname(__file__))

ADMINS = frozenset(['sgillespie3@gatech.edu'])
SECRET_KEY = os.environ['FLASK_SECRET_KEY']

CSRF_ENABLED = True
CSRF_SESSION_KEY = os.environ['FLASK_SECRET_KEY']