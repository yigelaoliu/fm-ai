from . import super_admin
from .forms import EditAdminForm, EditMachineForm
from .. import db
from ..decorators import super_required
from ..models import User, Admin, Machine, Order, MachineStatus
from flask import render_template, redirect, url_for, flash, abort, request, current_app, jsonify
# from flask_login import login_required, current_user


@super_admin.route('/', methods=['GET'])
@super_required
def index():
    return redirect(url_for('main.index'))


# 机器相关管理操作。
@super_admin.route('/machines', methods=['GET'])
@super_required
def machines():
    m_list = Machine.query.all()
    return render_template('machines.html', m_list=m_list)


# 通过提交的表单编辑机器数据。
def edit_m_with_form(m, form):
    m.fee = form.fee.data
    m.longitude = form.longitude.data
    m.latitude = form.latitude.data
    m.name = form.name.data
    m.info = form.info.data
    m.state = form.state.data
    m.admin_id = form.admin_id.data
    db.session.add(m)
    db.session.commit()
    flash('机器设置已更新')


# 新建机器。
@super_admin.route('/machine/new', methods=['GET', 'POST'])
@super_required
def new_machine():
    form = EditMachineForm()
    m = Machine()
    if form.validate_on_submit():
        edit_m_with_form(m=m, form=form)
        return redirect(url_for('super.edit_machine', m_id=m.id))
    return render_template('super/machine_edit.html', m=m, form=form)


# 编辑机器。
@super_admin.route('/machine/<int:m_id>/edit', methods=['GET', 'POST'])
@super_required
def edit_machine(m_id):
    form = EditMachineForm()
    m = Machine.query.get(m_id)
    if form.validate_on_submit():
        edit_m_with_form(m=m, form=form)
    return render_template('super/machine_edit.html', m=m, form=form)


# 隐藏机器。
@super_admin.route('/machine/<int:m_id>/hide', methods=['GET'])
@super_required
def hide_machine(m_id):
    m = Machine.query.get_or_404(m_id)
    m.state = -3  # -3)隐藏机器。
    db.session.add(m)
    db.session.commit()
    flash('洗车机已隐藏')
    return redirect(url_for('super.edit_machine', m_id=m.id))


# 显示机器。
@super_admin.route('/machine/<int:m_id>/show', methods=['GET'])
@super_required
def show_machine(m_id):
    m = Machine.query.get_or_404(m_id)
    m.state = 1  # 默认正常运营。需手动修改其他状态。
    db.session.add(m)
    db.session.commit()
    flash('洗车机已展示 请编辑洗车机运营状态')
    return redirect(url_for('super.edit_machine', m_id=m.id))


# 商家相关管理操作。
@super_admin.route('/admins', methods=['GET'])
@super_required
def admins():
    a_list = Admin.query.all()
    return render_template('super/admins.html', a_list=a_list)


# 通过提交的表单编辑商家数据。
def edit_a_with_from(a, form):
    a.name = form.name.data
    a.phone_num = form.phone_num.data
    a.info = form.info.data
    db.session.add(a)
    db.session.commit()
    flash('商家资料已更新')


# 新建商家。
@super_admin.route('/admin/new', methods=['GET', 'POST'])
@super_required
def new_admin():
    form = EditAdminForm()
    a = Admin()
    if form.validate_on_submit():
        edit_a_with_from(a=a, form=form)
        return redirect(url_for('super.admin', a_id=a.id))
    return render_template('super/admin.html', a=a, form=form)


# 商家页面。
@super_admin.route('/admin/<int:a_id>', methods=['GET', 'POST'])
@super_required
def admin(a_id):
    form = EditAdminForm()
    a = Admin.query.get_or_404(a_id)
    if form.validate_on_submit():
        edit_a_with_from(a=a, form=form)
    return render_template('super/admin.html', a=a, form=form)


# 商家拥有机器列表。
@super_admin.route('/admin/<int:a_id>/machines', methods=['GET'])
@super_required
def admin_machines(a_id):
    a = Admin.query.get_or_404(a_id)
    m_list = a.machines
    return render_template('machines.html', a=a, m_list=m_list)


# 商家机器订单列表。
@super_admin.route('/admin/<int:a_id>/orders', methods=['GET'])
@super_required
def admin_orders(a_id):
    a = Admin.query.get_or_404(a_id)
    o_list = a.orders
    return render_template('orders.html', a=a, o_list=o_list)


# 重置商家密码。
@super_admin.route('/reset-admin-pw/<int:a_id>', methods=['GET'])
@super_required
def reset_admin_pw(a_id):
    a = Admin.query.get_or_404(a_id)
    a.password = current_app.config['DEFAULT_ADMIN_PASSWORD']
    db.session.add(a)
    db.session.commit()
    return '成功重置管理员{a_id}号密码12345。'.format(a_id=a_id)


# 列出全部订单。
@super_admin.route('/orders', methods=['GET'])
@super_required
def orders():
    if request.args.get('transaction_id'):
        transaction_id = request.args.get('transaction_id')
        o_list = Order.query.filter_by(transaction_id=transaction_id)
    else:
        o_list = Order.query.all()
    return render_template('orders.html', o_list=o_list)


# 洗车用户的资料。待添加：车型、手机号、洗车时段等信息。
@super_admin.route('/user/<int:u_id>', methods=['GET'])
@super_required
def user(u_id):
    u = User.query.get_or_404(u_id)
    return u


# 洗车用户消费的订单。
@super_admin.route('/user/<int:u_id>/orders', methods=['GET'])
@super_required
def user_orders(u_id):
    u = User.query.get_or_404(u_id)
    o_list = u.orders
    return render_template('orders.html', u=u, o_list=o_list)
