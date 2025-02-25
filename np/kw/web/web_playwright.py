import os
import uuid

from playwright.sync_api import sync_playwright
from selenium.common import TimeoutException

from entity.TestVo import BrowserImage
from tools.config import keyword


class Playwright:
    def __init__(self):
        self.p = None
        self.page = None

    @keyword(name='初始化浏览器', param_conf={'headless': '无头模式', 'conf': '参数', 'no_viewport': 'no_viewport'})
    def init_browser(self, *args, **kwargs):
        headless = kwargs['params']['headless']
        no_viewport = kwargs['params']['no_viewport']
        headless = True if headless == 'true' else False
        no_viewport = True if no_viewport == 'true' else False
        conf = kwargs['params']['conf']
        args_list = conf.split(';')
        p = sync_playwright().start()
        self.p = p
        self.page = p.chromium.launch(headless=headless, args=args_list).new_context(no_viewport=no_viewport).new_page()
        return None, 'pass'

    @keyword(name='打开网页', param_conf={'url': '网址'})
    def go_to_page(self, *args, **kwargs):
        url = kwargs['params']['url']
        self.page.goto(url)
        return None, 'pass'

    @keyword(name='截图', param_conf={})
    def page_screenshot(self, *args, **kwargs):
        return self.capture_screenshot(), 'pass'

    @keyword(name='停止playwright', param_conf={})
    def quit_playwright(self):
        if self.page:
            self.page.close()
            self.page = None
        if self.p:
            self.p.stop()
            self.p = None
        return None, 'pass'

    @keyword(name='单击元素', param_conf={'element': '元素'})
    def elem_click(self, *args, **kwargs):
        elem = kwargs['params']['element']['expression']
        self.page.click(elem)
        return None, 'pass'

    @keyword(name='输入文本', param_conf={'element': '元素', 'text': '文本'})
    def input_text(self, *args, **kwargs):
        elem = kwargs['params']['element']['expression']
        self.page.fill(elem, kwargs['params']['text'])
        return None, 'pass'

    @keyword(name='获取元素文本', param_conf={'element': '元素'})
    def input_value(self, *args, **kwargs):
        elem = kwargs['params']['element']['expression']
        text = self.page.input_value(elem)
        return text, 'pass'

    @keyword(name='获取元素属性', param_conf={'element': '元素', 'attr': '属性名称'})
    def elem_attr(self, *args, **kwargs):
        elem = kwargs['params']['element']['expression']
        attr = kwargs['params']['attr']
        text = self.page.get_attribute(selector=elem, name=attr)
        return text, 'pass'

    @keyword(name='等待元素出现', param_conf={'element': '元素', 'timeout': '超时时间'})
    def wait_for_selector(self, *args, **kwargs):
        elem = kwargs['params']['element']['expression']
        timeout = kwargs['params']['timeout']
        try:
            self.page.wait_for_selector(selector=elem, timeout=int(timeout))
            return None, 'pass'
        except TimeoutException:
            return '等待超时', 'fail'

    @keyword(name='切换iframe', param_conf={'iframe': 'iframe'})
    def switch_to_frame(self, *args, **kwargs):
        iframe = kwargs['params']['iframe']
        self.page = self.page.frame_locator(iframe)
        return None, 'pass'

    @keyword(name='切换默认iframe', param_conf={})
    def switch_to_mainframe(self, *args, **kwargs):
        self.page = self.page.mainFrame()
        return None, 'pass'

    def capture_screenshot(self):
        file_name = f'{str(uuid.uuid4())}.png'
        self.page.screenshot(path=os.getcwd() + '/data/image/' + file_name)
        return BrowserImage(file_name)

