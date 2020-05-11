from flask import Blueprint

# 因super与内建函数重名。故用super_admin作为蓝图对象名字。
# app/init.py注册蓝图时使用super_blueprint，故url_map中endpoint为'super.index'。
# 不过app/super/views.py导入的是super_admin，所以修饰器为@super_admin.route('/')。
super_admin = Blueprint('super', __name__)

from . import views
