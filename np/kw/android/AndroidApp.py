import os
import uuid

import uiautomator2 as u2

from entity.TestVo import BrowserImage
from tools.config import keyword


class AndroidApp:
    def __init__(self):
        self.driver = None
        self.session = None

    @keyword(name='连接安卓设备', param_conf={'connect_type': '连接类型,wifi或usb', 'connect_dest': 'ip或序列号'})
    def connect_to_device(self, *args, **kwargs):
        connect_type = kwargs['params']['connect_type']
        connect_dest = kwargs['params']['connect_dest']
        if connect_type == 'wifi':
            self.driver = u2.connect(connect_dest)
        elif connect_type == 'usb':
            self.driver = u2.connect_usb(connect_dest)
        self.driver.screen_on()
        return None, 'pass'

    @keyword(name='打开App', param_conf={'package_name': '包名'})
    def launch_app(self, *args, **kwargs):
        package_name = kwargs['params']['package_name']
        self.session = self.driver.session(package_name)
        return None, 'pass'

    @keyword(name='关闭App', param_conf={})
    def stop_app(self, *args, **kwargs):
        self.session.close()
        return None, 'pass'

    @keyword(name='重启App', param_conf={})
    def stop_restart(self, *args, **kwargs):
        self.session.restart()
        return None, 'pass'

    @keyword(name='截图', param_conf={})
    def save_screenshot(self, *args, **kwargs):
        return self.capture_screenshot(), 'pass'

    def destroy_client(self):
        if self.session:
            self.session.close()
            self.session = None
        if self.driver:
            self.driver = None

    def capture_screenshot(self):
        file_name = f'{str(uuid.uuid4())}.png'
        self.driver.screenshot(filename=os.getcwd() + '/data/image/' + file_name, format='opencv')
        return BrowserImage(file_name)
