from wtforms import Form, TextField, PasswordField, BooleanField, IntegerField, validators

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

class ClientForm(Form):
    pick_up_day = IntegerField("Pick-up Day", [
	validators.Length(min=1, max=2),
	validators.InputRequired(message="This field is required."),
	validators.NumberRange(min=1, max=28, message="Date must be between 1 and 28.")
    ])
    first_name = TextField("First Name", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    last_name = TextField("Last Name", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    gender = TextField("Gender", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    birthdate = TextField("Birth-date: (mm/dd/YYYY)", [
	validators.Length(min=10, max=10),
	validators.InputRequired(message="This field is required.")
    ])
    street = TextField("Street Name", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    apartment_num = IntegerField("Apartment #", [
	validators.Length(min=1, max=10),
	validators.InputRequired(message="This field is required.")
    ])
    city = TextField("City", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    state = TextField("State", [
	validators.Length(min=2, max=40),
	validators.InputRequired(message="This field is required.")
    ])
    zipcode = IntegerField("Zipcode", [
	validators.Length(min=5, max=5),
	validators.InputRequired(message="This field is required.")
    ])
    phone = IntegerField("Phone Number: XXX-XXXX", [
	validators.Length(min=8, max=8),
	validators.InputRequired(message="This field is required.")
    ])
    start_date = IntegerField("Start Date: (mm/dd/YYYY)", [
	validators.Length(min=10, max=10),
	validators.InputRequired(message="This field is required.")
    ])
    delivery = BooleanField("Are you picking up the bag?")
