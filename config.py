import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'i am ur father'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    DEFAULT_ADMIN_PASSWORD = '12345'
    SUPER_ADMIN_PHONE_NUM = '19188884186'
    DEFAULT_WASH_FEE = 1000

    WX_APPID = '88888888'
    WX_SECRET = '88888888'

    # 微信支付开发相关参数。
    WXPAY_APPID = '88888888'
    WXPAY_MCH_ID = '88888888'
    WXPAY_API_KEY = '88888888'
    WXPAY_NOTIFY_ULR = 'http://pay.fm-ai.com/pay/notify'
    WXPAY_NONCE_STR = '88888888'

    ALIYUN_KEY = '88888888'
    ALIYUN_SECRET = '88888888'
    ALIYUN_SMS_SIGN = '费曼AI洗车'
    ALIYUN_SMS_TEMPLATE = 'SMS_149385594'

    # 洗车机运营状态。
    STATE_NORMAL = 1  # 正常运营。
    STATE_STOP = -1  # 暂停服务。
    STATE_WAIT = -2  # 即将开业。
    STATE_HIDE = -3  # 隐藏机器。

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://fmai:fmai@localhost:3306/fmai'
    MACHINE_QRCODE_PATH = basedir + '\\app\\static\\m_qrcode\\'


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://fmai:fmai@localhost:3306/fmai'
    MACHINE_QRCODE_PATH = basedir + '/app/static/m_qrcode/'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# print(DevelopmentConfig.MACHINE_QRCODE_PATH)
