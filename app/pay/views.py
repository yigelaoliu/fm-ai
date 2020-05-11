from . import pay
from .. import db
from ..models import Order, User, Machine
from flask import Flask, request, jsonify
from weixin.pay import WeixinPay, WeixinPayError
import time

app = Flask(__name__)
wx_pay = WeixinPay(
    '88888888',  # app_id 公众号APP_ID。
    '88888888',  # mch_id 商户号。
    '88888888',  # mch_key 商户开发秘钥。
    'http://pay.fm-ai.com/pay/notify',  # notify_url 支付成功后回调地址。
)


@pay.route('/hello')
def hello():
    return 'Hello World!'


@pay.route('/jsapi', methods=['POST'])
def pay_jsapi():
    """
    微信JSAPI创建统一订单，并且生成参数给JS调用
    :return: 微信格式XML
    """
    data_dict = wx_pay.to_dict(request.data.decode('utf-8'))
    product_id = data_dict['product_id']
    m = Machine.query.get_or_404(int(product_id))
    fee = m.fee
    timestamp = str(int(time.time()))
    out_trade_no = timestamp + '-' + product_id  # out_trade_no 商户订单号。商户系统内部订单号。时间戳-id。
    try:
        raw = wx_pay.jsapi(
            is_subscribe='Y',
            body='洗车机{n}号'.format(n=product_id),
            out_trade_no=out_trade_no,
            total_fee=fee,
            trade_type='NATIVE',
            product_id=product_id
        )
        xml_dict = {
            'return_code': 'SUCCESS',
            'appid': raw['appId'],
            'mch_id': '1516465131',
            'nonce_str': raw['nonceStr'],
            'is_subscribe': 'Y',  # 用户是否关注公众号，支付大于2元显示。
            'prepay_id': raw['package'].replace('prepay_id=', ''),
            'result_code': 'SUCCESS',
        }
        xml_dict['sign'] = wx_pay.sign(xml_dict)
        return wx_pay.to_xml(xml_dict)
    except WeixinPayError as e:
        print('ERROR: ' + str(e))
        return 'error', 400


@pay.route('/notify', methods=['GET', 'POST'])
def pay_notify():
    data_dict = wx_pay.to_dict(request.data.decode('utf-8'))
    record_order(data_dict)
    return 'OK', 200


@pay.route('/test', methods=['GET'])
def test():
    data = b'<xml><appid><![CDATA[wx3fd49b67c586bbeb]]></appid>\n<bank_type><![CDATA[CFT]]></bank_type>\n<cash_fee><![CDATA[1]]></cash_fee>\n<fee_type><![CDATA[CNY]]></fee_type>\n<is_subscribe><![CDATA[Y]]></is_subscribe>\n<mch_id><![CDATA[1510022291]]></mch_id>\n<nonce_str><![CDATA[sbvDwM9Q3eJpjJZGiBbqHEleTQhNR3iW]]></nonce_str>\n<openid><![CDATA[o9Khr1R7N8dmz1sC5YegSVZGBBBo]]></openid>\n<out_trade_no><![CDATA[2018080912345678-1]]></out_trade_no>\n<result_code><![CDATA[SUCCESS]]></result_code>\n<return_code><![CDATA[SUCCESS]]></return_code>\n<sign><![CDATA[AD40D7D7B215C1942BB23FB9A151EF8D]]></sign>\n<time_end><![CDATA[20180722123535]]></time_end>\n<total_fee>1</total_fee>\n<trade_type><![CDATA[NATIVE]]></trade_type>\n<transaction_id><![CDATA[4200000123201807228171678037]]></transaction_id>\n</xml>'
    data_dict = wx_pay.to_dict(data.decode('utf-8'))
    record_order(data_dict)
    from pprint import pprint
    pprint(data_dict)
    return 'ok'


def record_order(data_dict):
    transaction_id = data_dict['transaction_id']
    if Order.query.filter_by(transaction_id=transaction_id).first() is not None:
        return
    openid = data_dict['openid']
    m_id = data_dict['out_trade_no'].split('-')[1]
    m = Machine.query.get_or_404(m_id)
    u = User.query.filter_by(openid=openid).first()
    if u is None:
        # 若不存在用户openid，则创建用户。
        u = User(openid=openid)
        db.session.add(u)
        db.session.commit()
    status = 0
    if data_dict['result_code'] == 'SUCCESS':
        status = 1
    o = Order(
        fee=int(data_dict['total_fee']),
        user_id=u.id,
        machine_id=m_id,
        admin_id=m.admin_id,
        status=status,
        transaction_id=transaction_id  # 微信支付订单。
    )
    db.session.add(o)
    db.session.commit()
