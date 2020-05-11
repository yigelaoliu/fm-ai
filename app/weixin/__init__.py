from flask import Blueprint

weixin = Blueprint('weixin', __name__)  # 抽离weixin需要三个文件夹：app/weixin; templates/weixin; static/weixin。

from . import views
from . import forms
from . import sign
from . import aliyun_sms
