from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered.")


class CommentForm(FlaskForm):
    content = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    genre = StringField("Genre", validators=[DataRequired()])
    year = IntegerField("Year", validators=[DataRequired()])
    thumbnail = FileField("Thumbnail", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    video = FileField("Video", validators=[FileAllowed(["mp4"], "Videos only!")])
    submit = SubmitField("Submit")


class UpdateProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update")


class ChangePasswordForm(FlaskForm):
    """
    Форма для изменения пароля в профиле.
    """
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message="Current password is required.")]
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required."),
            Length(min=6, message="Password must be at least 6 characters long.")
        ]
    )
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Change Password')
