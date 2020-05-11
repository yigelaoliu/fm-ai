import time
import random
import string
import hashlib


class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.create_timestamp(),
            'url': url
        }

    @staticmethod
    def create_nonce_str():
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    @staticmethod
    def create_timestamp():
        return int(time.time())

    def sign(self):
        sign_string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        # print(sign_string)
        self.ret['signature'] = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
        return self.ret
