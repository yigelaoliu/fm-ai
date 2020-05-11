import uuid
import datetime
import hmac
import base64
import requests
from urllib.parse import quote
from flask import current_app


class AliyunSMS(object):
    def __init__(self):

        self.format = "JSON"
        self.version = "2017-05-25"
        self.key = current_app.config['ALIYUN_KEY']
        self.secret = current_app.config['ALIYUN_SECRET']
        self.signature = ""
        self.signature_method = "HMAC-SHA1"
        self.signature_version = "1.0"
        self.signature_nonce = str(uuid.uuid4())
        self.timestamp = datetime.datetime.utcnow().isoformat("T")
        self.region_id = 'cn-hangzhou'

        self.gateway = "http://dysmsapi.aliyuncs.com"
        self.action = "SendSms"
        self.sign = ""
        self.template = ""
        self.params = {}
        self.phones = ""

    def send_single(self, phone, sign, template, params):
        self.action = "SendSms"
        self.phones = phone
        self.sign = sign
        self.params = params
        self.template = template

        query_string = self.build_query_string()

        resp = requests.get(self.gateway + "?" + query_string).json()
        model = resp.get("Model")
        if model is not None:
            return True
        # print(model)
        # print("send sms to %s , reason: %s" % (self.phones, resp.get("Message")))
        # print(resp)
        return False

    def build_query_string(self):
        query = list()
        query.append(("Format", self.format))
        query.append(("Version", self.version))
        query.append(("AccessKeyId", self.key))
        query.append(("SignatureMethod", self.signature_method))
        query.append(("SignatureVersion", self.signature_version))
        query.append(("SignatureNonce", self.signature_nonce))
        query.append(("Timestamp", self.timestamp))
        query.append(("RegionId", self.region_id))
        query.append(("Action", self.action))
        query.append(("SignName", self.sign))
        query.append(("TemplateCode", self.template))
        query.append(("PhoneNumbers", self.phones))
        params = "{"
        for param in self.params:
            params += "\"" + param + "\"" + ":" + "\"" + str(self.params[param]) + "\"" + ","
        params = params[:-1] + "}"
        # print(params)
        query.append(("TemplateParam", params))
        query = sorted(query, key=lambda key: key[0])
        query_string = ""
        i = 0
        for item in query:
            query_string += quote(item[0], safe="~") + "=" + quote(item[1], safe="~") + "&"
            i += 1
            # print(query_string)
        # print(i)
        query_string = query_string[:-1]
        # print(query_string)
        tosign = "GET&%2F&" + quote(query_string, safe="~")
        secret = self.secret + "&"
        hmb = hmac.new(secret.encode("utf-8"), tosign.encode("utf-8"), "sha1").digest()
        self.signature = quote(base64.standard_b64encode(hmb).decode("ascii"), safe="~")
        query_string += "&" + "Signature=" + self.signature
        # print('query_string', query_string)
        return query_string
