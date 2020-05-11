from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 注册main蓝图。管理拥有机器的蓝图
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册pay蓝图。用于处理微信支付的蓝图。
    from .pay import pay as pay_blueprint
    app.register_blueprint(pay_blueprint, url_prefix='/pay')

    # 注册auth蓝图。用于注册登录登出的蓝图。
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册super蓝图。用于处超级管理的蓝图。
    from .super import super_admin as super_blueprint
    app.register_blueprint(super_blueprint, url_prefix='/super')

    # 注册weixin蓝图。此为公众号H5页面的蓝图。
    from .weixin import weixin as weixin_blueprint
    app.register_blueprint(weixin_blueprint, url_prefix='/weixin')

    return app
