from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    #remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class EditForm(FlaskForm):
    name = StringField('Название закупки')
    page = StringField('page')
    max_page = StringField('максимальная страница', validators=[DataRequired()])
    interval_minutes = StringField('время проверки', validators=[DataRequired()])
    active = StringField('поднятие включено', validators=[DataRequired()])
    up_time = StringField('время последнего поднятия ')

