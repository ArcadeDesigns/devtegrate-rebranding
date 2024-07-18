from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class MessagesForm(FlaskForm):
    name = StringField()
    email = StringField()
    company_name = StringField()
    company_size = StringField()
    industry = StringField()
    other_industry = StringField()
    help_with = StringField()
    other_help = StringField()
    submit = SubmitField()

class OTPForm(FlaskForm):
    otp = StringField()
    submit = SubmitField()
