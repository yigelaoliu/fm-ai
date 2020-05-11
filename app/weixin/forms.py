from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length


class BindPhoneForm(FlaskForm):
    phone_num = StringField('手机号', validators=[DataRequired(), Length(0, 16)])
    sms_code = TextAreaField('验证码', validators=[DataRequired(), Length(0, 128)])
