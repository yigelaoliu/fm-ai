#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Admin, Machine, Car, Order, MachineStatus
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db,
                User=User, Admin=Admin, Machine=Machine, Car=Car, Order=Order, MachineStatus=MachineStatus)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# 初始化数据库。
@manager.command
def init_db():
    db.create_all()
    gen_fake_data()


# 删除现有的数据库。
@manager.command
def drop_db():
    db.drop_all()


# 先删除现有的数据库，再初始化数据库。
@manager.command
def drop_init():
    drop_db()
    init_db()


# 生成假数据。
@manager.command
def gen_fake_data():
    # 生成假管理员。
    a1 = Admin(name='刘延', phone_num=app.config['SUPER_ADMIN_PHONE_NUM'])
    a2 = Admin(name='王宁', phone_num='15511127075')
    db.session.add_all([a1, a2])
    db.session.commit()

    # 生成假机器。
    m1 = Machine(
        latitude='38.0348631337',  # QQ地图坐标拾取器。 http://lbs.qq.com/tool/getpoint/
        longitude='114.5281523466',
        admin_id=1,
        state=1,
        info='育才街，金领大厦。'
    )
    m2 = Machine(latitude='38.0481544341', longitude='114.3547850847', admin_id=1, state=-2, info='御园路。')
    m3 = Machine(latitude='38.0342006313', longitude='114.4178228152', admin_id=2, state=-1, info='裕华西路，苑东街。')
    db.session.add_all([m1, m2, m3])
    db.session.commit()

    # 生成假用户。
    u1 = User(openid='wx_test1')
    u2 = User(openid='wx_test2')
    db.session.add_all([u1, u2])
    db.session.commit()

    # 生成假车。
    c1 = Car(name='测试车1')
    c2 = Car(name='测试车2')
    db.session.add_all([c1, c2])
    db.session.commit()

    # 生成假订单。
    o1 = Order(transaction_id='fake_1', status=1, user=u1, machine=m1, admin=m1.admin, car=c1, fee=1000)
    o2 = Order(transaction_id='fake_2', status=1, user=u1, machine=m2, admin=m2.admin, car=c2, fee=1500)
    o3 = Order(transaction_id='fake_3', status=1, user=u2, machine=m3, admin=m3.admin, car=c1, fee=1000)
    o4 = Order(transaction_id='fake_4', status=1, user=u2, machine=m1, admin=m1.admin, car=c1, fee=1001)

    db.session.add_all([o1, o2, o3, o4])
    db.session.commit()


# 列出app的全部路由规则。
@manager.command
def list_url_rules():
    from pprint import pprint
    pprint(list(app.url_map.iter_rules()))


if __name__ == '__main__':
    manager.run()
