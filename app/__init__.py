from flask import Flask, render_template, flash

app = Flask("Food Pantry Webapp - CS 4400")
app.config.from_object('config')

@app.errorhandler(404)
def not_found(e):
    return "OH GOD WHY", 404

@app.route('/')
def hello():
    flash("Hello world!")
    return render_template('index.html')