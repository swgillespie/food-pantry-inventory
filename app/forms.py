from wtforms import Form, TextField, PasswordField, BooleanField, validators

class LoginForm(Form):
    username = TextField("Username", [
        validators.Length(min=4, max=20),
        validators.InputRequired(message="This field is required.")
    ])
    password = PasswordField("Password", [
        validators.Length(min=4, max=20),
        validators.InputRequired(message="This field is required.")
    ])

class RegistrationForm(Form):
    username = TextField("Username", [
        validators.Length(min=4, max=20),
        validators.InputRequired(message="This field is required.")
    ])
    firstname = TextField("First Name", [
        validators.Length(min=2, max=20),
        validators.InputRequired(message="This field is required.")
    ])
    lastname = TextField("Last Name", [
        validators.Length(min=2, max=40),
        validators.InputRequired(message="This field is required.")
    ])
    email = TextField("Email", [
        validators.Length(min=2, max=40),
        validators.Email(message="Please enter a valid email")
    ])
    password = PasswordField("Password", [
        validators.Required(),
        validators.EqualTo('confirm_pass', message='Passwords must match')
    ])
    confirm_pass = PasswordField("Password Again")
    is_director = BooleanField("Are you a director?")