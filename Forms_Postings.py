from wtforms import *
from wtforms.fields import *


class CreatePostingForm(Form):
    company_name = StringField('Company Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    position = StringField('Position', [validators.Length(min=1, max=150), validators.DataRequired()])
    quantity = IntegerField('Slots Available', [validators.NumberRange(min=1, max=10),validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    pay_rate = FloatField('Pay Rate', [validators.NumberRange(min=0, max=50), validators.DataRequired()])
    date = DateField('Date', [validators.DataRequired()])
    start_time = TimeField('Start Time', [validators.DataRequired()])
    end_time = TimeField('End Time', [validators.DataRequired()])