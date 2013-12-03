from flask import Flask, render_template
import logging

app = Flask("Food Pantry Webapp - CS 4400")
app.config.from_object('config')

@app.errorhandler(404)
def not_found(e):
    return "OH GOD WHY", 404

from app.views import mod as views
app.register_blueprint(views)
