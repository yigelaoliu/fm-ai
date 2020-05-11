from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length


class EditAdminForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(), Length(0, 8)])
    phone_num = StringField('手机', validators=[DataRequired(), Length(0, 16)])
    info = TextAreaField('资料', validators=[DataRequired(), Length(0, 128)])


class EditMachineForm(FlaskForm):
    fee = StringField('单次计费(单位：分)', validators=[DataRequired(), Length(0, 8)])
    longitude = FloatField('经度', validators=[DataRequired()])
    latitude = FloatField('纬度', validators=[DataRequired()])
    name = StringField('名称', validators=[DataRequired()])
    info = StringField('资料', validators=[DataRequired(), Length(0, 128)])
    state = IntegerField('运营状态', validators=[DataRequired()])
    admin_id = IntegerField('商家ID', validators=[DataRequired()])
