from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    passengers = StringField('Number of passengers', default=1)
    date_from = DateTimeField(
        label='First departure date (YYYY-MM-DD)',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
    date_to = DateTimeField(
        label='Last departure date (YYYY-MM-DD)',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
