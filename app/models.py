from . import db
from . import login_manager
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# 管理员/商家模型。拥有洗车机的人。可登陆后台的账号。
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String(16), unique=True, index=True)  # 登录用的电话。
    pw_hash = db.Column(db.String(128))  # 登录密码。以密文存储。
    name = db.Column(db.String(8))
    info = db.Column(db.Text())  # 管理员的个人信息。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    a_orders = db.relationship('Order', backref='admin', lazy='dynamic')
    machines = db.relationship('Machine', backref='admin', lazy='dynamic')
    notification = db.relationship('Notification', backref='admin', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)
        self.password = current_app.config['DEFAULT_ADMIN_PASSWORD']  # 初始化密码12345。

    @property
    def password(self):
        raise AttributeError('密码不是可读属性')

    @password.setter
    def password(self, password):
        self.pw_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def is_super(self):
        return self.phone_num == current_app.config['SUPER_ADMIN_PHONE_NUM']

    # 管理员拥有全部洗车机的全部订单的列表。
    @property
    def orders(self):
        all_orders = []
        machines = self.machines
        for m in machines:
            orders = m.orders
            for o in orders:
                all_orders.append(o)
        return sorted(all_orders, key=lambda x: x.id)

    # 最近15天的订单数量的数组。
    @property
    def latest_orders_count_list(self):
        days = 15
        count_list = []
        for day in range(0, days):
            that_day = date.today() - timedelta(days=day-1)  # 那一天。
            last_day = date.today() - timedelta(days=day)  # 那一天的上一天。
            count = Order.query.filter_by(admin=self).\
                filter(Order.timestamp >= last_day).\
                filter(Order.timestamp <= that_day).count()
            count_list.append(count)
        count_list.reverse()
        return count_list

    # 管理员的全部收入。
    @property
    def income(self):
        income = 0
        machines = self.machines
        for m in machines:
            orders = m.orders
            for o in orders:
                income += o.fee
        return income

    def __repr__(self):
        return '<Admin %r>' % self.id


# 机器模型。
class Machine(db.Model):
    __tablename__ = 'machines'
    id = db.Column(db.Integer, primary_key=True)
    fee = db.Column(db.Integer)  # 洗一次车的定价。单位是分。用于生成支付金额。
    longitude = db.Column(db.String(16))  # 经度 114.522648。
    latitude = db.Column(db.String(16))  # 纬度 38.042903。
    state = db.Column(db.Integer)  # 洗车机的*运营*状态：1)正常运营；-1)暂停服务；-2)即将开业；-3)隐藏机器。非status*运行*状态。
    name = db.Column(db.String(32))  # 洗车机的名字。
    info = db.Column(db.Text())  # 机器的相关信息。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    orders = db.relationship('Order', backref='machine', lazy='dynamic')  # 洗车机洗过的订单。
    statuses = db.relationship('MachineStatus', backref='machine', lazy='dynamic')  # 关联MachineStatus模型。

    def __init__(self, **kwargs):
        super(Machine, self).__init__(**kwargs)
        self.fee = current_app.config['DEFAULT_WASH_FEE']  # 初始化洗车费用为默认。

    # 洗车机的全部收入。
    @property
    def income(self):
        orders = self.orders
        income = 0
        for o in orders:
            income += o.fee
        return income

    def has_qrcode(self):
        file_path = current_app.config['MACHINE_QRCODE_PATH'] + 'mid_' + str(self.id) + '.png'
        return os.path.exists(file_path)

    def __repr__(self):
        return '<Machine %r>' % self.id


# 用户模型。洗车的人。
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True, index=True)  # 微信交易用户openid。为APP对应用户的唯一id。
    phone_num = db.Column(db.String(16), index=True)  # 可为空。检查是否绑定了手机号。
    sms_code = db.Column(db.String(8))  # 绑定手机是发送的验证码。每发送一次短信，更新一次sms_code。
    phone_verified = db.Column(db.Boolean, default=False)  # 手机号是否经过验证。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    orders = db.relationship('Order', backref='user', lazy='dynamic')  # 用户洗车消费的订单。

    # 用户拥有的车。
    @property
    def cars(self):
        orders = self.orders
        car_list = []
        for o in orders:
            car = o.car
            if car and (car not in car_list):
                car_list.append(car)
        return car_list

    def __repr__(self):
        return '<User %r>' % self.id


# 车型模型。
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)  # 车名。
    firm = db.Column(db.String(32))  # 厂家。
    date = db.Column(db.String(16))  # 上市时间。
    engine = db.Column(db.String(16))  # 发动机。

    orders = db.relationship('Order', backref='car', lazy='dynamic')  # 此款车型的全部订单。

    def __repr__(self):
        return '<Car %r>' % self.id


# 订单模型。
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(32), unique=True, index=True)  # 微信支付成功后返回的微信订单号。
    fee = db.Column(db.Integer)  # 洗车的金额。已订单为准。与机器洗车定价无关。用于纪录账单。
    status = db.Column(db.Integer)  # 订单的交易状态。支付成功、失败。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))

    def __repr__(self):
        return '<Order %r>' % self.id


# 机器状态模型。记录机器反馈的状态。
class MachineStatus(db.Model):
    __tablename__ = 'machine_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32))  # 机器返回的状态。格式未定。停水、缺清洗剂。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'))

    def __repr__(self):
        return '<MachineStatus %r>' % self.id


# 站内通知模型。
class Notification(db.Model):
    __tablename__ = 'notifictions'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)  # 状态。已读、未读。
    timestamp = db.Column(db.DateTime, default=datetime.now)

    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))  # 收信人。

    def __repr__(self):
        return '<Notification %r>' % self.id
