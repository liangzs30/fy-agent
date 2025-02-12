import json
import warnings

import requests
from tools.config import keyword

warnings.filterwarnings("ignore")


class HttpClient:
    def __init__(self):
        self.client = requests

    @keyword(name='【HTTP】POST请求', param_conf={'url': '请求URL', 'headers': '请求头', 'data': '请求体'})
    def send_post(self, *args, **kwargs):
        params = kwargs['params']
        if params['headers'] != '':
            response = self.client.post(url=params['url'], headers=json.loads(params['headers']), data=params['data'],
                                        timeout=10)
        else:
            response = self.client.post(url=params['url'], data=params['data'], headers={'content-type': 'text/plain'},
                                        timeout=10)
        return response, 'pass'

    @keyword(name='【HTTP】PUT请求', param_conf={'url': '请求URL', 'headers': '请求头', 'data': '请求体'})
    def send_put(self, *args, **kwargs):
        params = kwargs['params']
        if params['headers'] != '':
            response = self.client.put(url=params['url'], headers=json.loads(params['headers']), data=params['data'],
                                       timeout=10)
        else:
            response = self.client.put(url=params['url'], data=params['data'], headers={'content-type': 'text/plain'},
                                       timeout=10)
        return response, 'pass'

    @keyword(name='【HTTP】GET请求', param_conf={'url': '请求URL', 'headers': '请求头', 'params': '请求参数'})
    def send_get(self, *args, **kwargs):
        params = kwargs['params']
        if params['headers'] != '':
            response = self.client.get(url=params['url'], headers=json.loads(params['headers']),
                                       params=params['params'], timeout=10)
        else:
            response = self.client.get(url=params['url'], params=params['params'],
                                       headers={'content-type': 'text/plain'}, timeout=10)
        return response, 'pass'

    @keyword(name='【HTTP】DELETE请求', param_conf={'url': '请求URL', 'headers': '请求头', 'data': '请求体'})
    def send_delete(self, *args, **kwargs):
        params = kwargs['params']
        if params['headers'] != '':
            response = self.client.delete(url=params['url'], headers=json.loads(params['headers'], timeout=10),
                                          data=params['data'])
        else:
            response = self.client.delete(url=params['url'], data=params['data'],
                                          headers={'content-type': 'text/plain'}, timeout=10)
        return response, 'pass'

    @keyword(name='使用session', param_conf={})
    def create_session(self, *args, **kwargs):
        self.client = requests.session()
        return None, 'pass'

    @keyword(name='使用session', param_conf={})
    def cancel_session(self, *args, **kwargs):
        self.client = requests
        return None, 'pass'
