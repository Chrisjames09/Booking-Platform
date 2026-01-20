from wtforms import Form, StringField, SelectField, TextAreaField, PasswordField, validators

class ptForm(Form):
    firstname = StringField('First Name', [validators.DataRequired(), validators.Length(min=2, max=50)])
    lastname = StringField('Last Name', [validators.DataRequired(), validators.Length(min=2, max=50)])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')],default='')
    phone = StringField('Phone Number', [validators.DataRequired(), validators.Length(min=8, max=8)])
    address = TextAreaField('Address', [validators.DataRequired(), validators.Length(min=10, max=200)])
    bank = StringField('Bank Number', [validators.DataRequired(), validators.Length(min=7, max=15 )])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired(), validators.EqualTo('password', message="Passwords must match.")])

class ftForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired(), validators.EqualTo('password', message="Passwords must match.")])

class ptUpdate(Form):
    firstname = StringField('First Name', [validators.DataRequired(), validators.Length(min=2, max=50)])
    lastname = StringField('Last Name', [validators.DataRequired(), validators.Length(min=2, max=50)])
    phone = StringField('Phone Number', [validators.DataRequired(), validators.Length(min=8, max=8)])
    address = TextAreaField('Address', [validators.DataRequired(), validators.Length(min=10, max=200)])
    bank = StringField('Bank Number', [validators.DataRequired(), validators.Length(min=7, max=15 )])

class loginForm(Form):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6, max=50)])
