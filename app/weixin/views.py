from . import weixin
from .forms import BindPhoneForm
from .sign import Sign
from .aliyun_sms import AliyunSMS
from .. import db
from ..models import User, Machine, Order
from flask import render_template, redirect, url_for, flash, abort, request, current_app, jsonify
import requests
import json
import urllib.parse
import random


# 公众号H5首页。
@weixin.route('/', methods=['GET'])
def index():
    access_token = get_access_token()
    jsapi_ticket = get_jsapi_ticket(access_token)
    current_url = request.url
    sign = Sign(jsapi_ticket, current_url).sign()
    m_list = Machine.query.filter(Machine.state != current_app.config['STATE_HIDE']).all()
    return render_template('weixin/index.html', m_list=m_list, sign=sign)


# 显示当前微信用户的订单。
@weixin.route('/orders', methods=['GET'])
def orders():
    if request.args.get('code'):
        code = request.args.get('code')
        openid = get_openid(code=code)
        if User.query.filter_by(openid=openid).first():
            u = User.query.filter_by(openid=openid).first()
        else:
            u = User(openid=openid)
            db.session.add(u)
            db.session.commit()
        o_list = Order.query.filter_by(user=u).all()
        return render_template('weixin/orders.html', o_list=o_list)
    # 生成重定向到当前url的微信授权url。
    url = request.url
    authorize_url = wx_authorize_url(url=url, scope='snsapi_base')  # 静默授权。
    return render_template('weixin/orders.html', authorize_url=authorize_url)


# 洗车用户的个人主页。
@weixin.route('/mine', methods=['GET'])
def mine():
    if request.args.get('code'):
        code = request.args.get('code')
        openid = get_openid(code=code)
        if User.query.filter_by(openid=openid).first():  # 是否记录过此openid的用户。
            u = User.query.filter_by(openid=openid).first()
            if u.phone_verified:  # 用户手机号是否经过验证。
                return render_template('weixin/mine.html', u=u)
            else:
                return redirect(url_for('weixin.bind_phone', openid=openid))
        else:
            u = User(openid=openid)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('weixin.bind_phone', openid=openid))
    # 生成重定向到当前url的微信授权url。
    url = request.url
    authorize_url = wx_authorize_url(url=url, scope='snsapi_base')  # 静默授权。
    return render_template('weixin/mine.html', authorize_url=authorize_url)


# 绑定微信用户手机号。
@weixin.route('/bind-phone/<string:openid>', methods=['GET', 'POST'])
def bind_phone(openid):
    form = BindPhoneForm()
    u = User.query.filter_by(openid=openid).first()
    if form.validate_on_submit():
        phone_num = form.phone_num.data
        sms_code = form.sms_code.data
        if (u.phone_num == phone_num) and (u.sms_code == sms_code):
            u.phone_verified = True
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('weixin.mine'))
        else:  # 校验失败情况。应该做一个AJAX校验。省去一次跳转。
            return render_template('weixin/bind_phone.html', openid=openid, form=form)
    return render_template('weixin/bind_phone.html', openid=openid, form=form)


# 发送验证短信。/send-sms?openid=wx_test1&phone_num=17363015217
@weixin.route('/send-sms', methods=['GET'])
def send_sms():
    openid = request.args.get('openid')
    phone_num = request.args.get('phone_num')

    if User.query.filter_by(openid=openid).first():  # 是否记录过此openid的用户。
        u = User.query.filter_by(openid=openid).first()
        u.phone_num = phone_num
    else:
        u = User(openid=openid, phone_num=phone_num)

    db.session.add(u)
    db.session.commit()

    # 发送短信。
    def gen_random_string(range_num):
        s = ''
        for i in range(range_num):
            n = str(random.randint(0, 9))
            s = s + n
        return s

    sms = AliyunSMS()

    params = {"code": gen_random_string(range_num=6)}  # 随机生成6位数
    sign = current_app.config['ALIYUN_SMS_SIGN']
    template = current_app.config['ALIYUN_SMS_TEMPLATE']
    sms.send_single(phone=phone_num, sign=sign, template=template, params=params)

    # 记录短信验证码。
    sms_code = params['code']
    u.sms_code = sms_code
    db.session.add(u)
    db.session.commit()
    return sms_code


# 获取access_token。
def get_access_token():
    appid = current_app.config['WX_APPID']
    secret = current_app.config['WX_SECRET']
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'.format(
        appid=appid, secret=secret
    )
    json_str = requests.get(url).text
    d = json.loads(json_str)
    return d['access_token']


# 获取jsapi_ticket。
def get_jsapi_ticket(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi'.format(
        access_token=access_token
    )
    json_str = requests.get(url).text
    d = json.loads(json_str)
    return d['ticket']


# 生成微信授权链接。
def wx_authorize_url(url, scope):
    # https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect
    appid = current_app.config['WX_APPID']
    redirect_uri = urllib.parse.quote(url)
    authorize_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?' \
                    'appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}' \
                    '#wechat_redirect'.format(
                        appid=appid, redirect_uri=redirect_uri, scope=scope
                    )
    return authorize_url


# 获取微信授权access_token，跟上面的JS-SDK基础支持中的access_token不同。
def get_openid(code):
    # https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
    appid = current_app.config['WX_APPID']
    secret = current_app.config['WX_SECRET']
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' \
          'appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'.format(
              appid=appid, secret=secret, code=code
          )
    json_str = requests.get(url).text
    d = json.loads(json_str)
    return d['openid']
