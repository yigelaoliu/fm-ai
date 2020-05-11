from . import main
from ..models import User, Admin, Machine, Order, MachineStatus
from flask import render_template, redirect, url_for, flash, abort, request, current_app, jsonify
from flask_login import login_required, current_user
import os


# 未登录转向登录界面。已登录主页为管理员个人页面的概览。
@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    else:
        a = current_user
        return render_template('index.html', a=a)


# 管理员所拥有的全部机器。
@main.route('/machines', methods=['GET'])
@login_required
def machines():
    m_list = current_user.machines
    return render_template('machines.html', m_list=m_list)


# 单个机器页面。
@main.route('/machine/<int:m_id>', methods=['GET'])
@login_required
def machine(m_id):
    m = Machine.query.get_or_404(m_id)
    if m.admin_id == current_user.id or current_user.is_super():
        return render_template('machine.html', m=m)
    else:
        abort(403)


# 机器的二维码。
@main.route('/machine/<int:m_id>/qrcode', methods=['GET', 'POST'])
@login_required
def machine_qrcode(m_id):
    m = Machine.query.get_or_404(m_id)
    if m.admin_id == current_user.id or current_user.is_super():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('未选择图片。')
                return redirect(request.url)
            file = request.files['file']
            if file:
                file_path = os.path.join(current_app.config['MACHINE_QRCODE_PATH'] + 'mid_' + str(m.id) + '.png')
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                file.save(file_path)
                flash('二维码上传成功。如果图片没有更换，是浏览器缓存问题。')
        qrcode_s = gen_qrcode_string(m)
        return render_template('machine_qrcode.html', m=m, qrcode_s=qrcode_s)
    else:
        abort(403)


# 单个机器订单。
@main.route('/machine/<int:m_id>/orders', methods=['GET'])
@login_required
def machine_orders(m_id):
    m = Machine.query.get_or_404(m_id)
    if m.admin_id == current_user.id or current_user.is_super():
        o_list = m.orders
        return render_template('orders.html', m=m, o_list=o_list)
    else:
        abort(403)


# 当前商家的订单。
@main.route('/orders', methods=['GET'])
@login_required
def orders():
    a = current_user
    return render_template('orders.html', o_list=a.orders)


def gen_qrcode_string(m):
    import time
    from hashlib import md5

    api_key = current_app.config['WXPAY_API_KEY']
    qrcode_dict = {
        'appid': current_app.config['WXPAY_APPID'],
        'mch_id': current_app.config['WXPAY_MCH_ID'],
        'nonce_str': current_app.config['WXPAY_NONCE_STR'],
        'product_id': str(m.id),
        'time_stamp': str(int(time.time())),
    }
    sorted_s = ''
    for k in sorted(qrcode_dict.keys()):
        sorted_s += '{k}={v}&'.format(k=k, v=qrcode_dict[k])
    sign = md5((sorted_s + 'key=' + api_key).encode(encoding='utf-8')).hexdigest().upper()
    qrcode_s = 'weixin://wxpay/bizpayurl?sign={sign}&{sorted_s}'.format(sign=sign, sorted_s=sorted_s)

    return qrcode_s
