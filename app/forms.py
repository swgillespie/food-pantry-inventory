from wtforms import Form, TextField, PasswordField, BooleanField, IntegerField, SelectField, validators

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
        validators.Length(min=4, max=20),
        validators.Required(),
        validators.EqualTo('confirm_pass', message='Passwords must match')
    ])
    confirm_pass = PasswordField("Password Again")
    is_director = BooleanField("Are you a director?")

class DropoffForm(Form):
    product = TextField("Product", [
        validators.Length(min=2, max=24),
        validators.InputRequired(message="This field is required.")
    ])
    source = TextField("Source", [
        validators.Length(min=3, max=24),
        validators.InputRequired(message="This field is required.")
    ])
    qty = IntegerField("Qty", [
        validators.NumberRange(min=1, message="Must drop off at least one of this product."),
        validators.InputRequired(message="This field is required.")
    ])

class NewProductForm(Form):
    product = TextField("Product", [
        validators.Length(min=2, max=24),
        validators.InputRequired(message="This field is required.")
    ])
    source = TextField("Source", [
        validators.Length(min=3, max=24),
        validators.InputRequired(message="This field is required.")
    ])
    cost = IntegerField("Cost Per Unit", [
        validators.NumberRange(min=1, message="Cost must be at least 1."),
        validators.InputRequired(message="This field is required.")
    ])

class ClientForm(Form):
    pick_up_day = IntegerField("Pick-up Day", [
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
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ])
    birthdate = TextField("Birth-date: (YYYY-mm-dd)", [
        validators.Length(min=10, max=10),
        validators.InputRequired(message="This field is required.")
    ])
    street = TextField("Street Name", [
        validators.Length(min=2, max=40),
        validators.InputRequired(message="This field is required.")
    ])
    apartment_num = IntegerField("Apartment #", [
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
        validators.InputRequired(message="This field is required.")
    ])
    phone = TextField("Phone Number: ", [
        validators.Length(min=10, max=10),
        validators.InputRequired(message="This field is required.")
    ])
    start_date = TextField("Start Date: (YYYY-mm-dd)", [
        validators.Length(min=10, max=10),
        validators.InputRequired(message="This field is required.")
    ])
    aid = SelectField('Aid Source')
    bag = SelectField('Bag')
    delivery = BooleanField("Are you picking up the bag?")

class FamilyForm(Form):
    firstname = TextField("First Name", [
        validators.Length(min=2, max=40),
        validators.InputRequired(message="This field is required.")
    ])
    lastname = TextField("Last Name", [
        validators.Length(min=2, max=40),
        validators.InputRequired(message="This field is required.")
    ])
    gender = TextField("Gender", [
        validators.Length(min=1, max=40),
        validators.InputRequired(message="This field is required.")
    ])
    dob = TextField("Birth-date: (YYYY-mm-dd)", [
        validators.Length(min=10, max=10),
        validators.InputRequired(message="This field is required.")
    ])
