from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class SearchForm(FlaskForm):
    city = StringField('Città', validators=[DataRequired(message='Inserisci il nome di una città')])
    submit = SubmitField('Cerca')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Accedi')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma password', validators=[
        DataRequired(),
        EqualTo('password', message='Le password non corrispondono'),
    ])
    submit = SubmitField('Registrati')
