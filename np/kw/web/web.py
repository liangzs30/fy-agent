import os
import sys
import uuid
import warnings

import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains

from entity.TestVo import BrowserImage
from tools.config import keyword

warnings.filterwarnings("ignore")


class Browser:
    def __init__(self):
        self.driver = None

    @keyword(name='配置webdriver', param_conf={'browser_type': '浏览器类型', 'driver_path': '驱动器路径'})
    def set_driver(self, *args, **kwargs):
        browser_type = kwargs['params']['browser_type']
        driver_path = os.getcwd() + '/browser/'
        if kwargs['params'].get('driver_path'):
            driver_path = kwargs['params']['driver_path']
        if browser_type == 'fireFox':
            self.driver = webdriver.firefox
        elif browser_type == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver_name = 'chromedriver.exe' if sys.platform == 'win32' else 'chromedriver'
            self.driver = webdriver.Chrome(executable_path=f'{driver_path}{driver_name}',
                                           chrome_options=chrome_options)
        elif browser_type == 'Microsoft Edge':
            self.driver = webdriver.ChromiumEdge(executable_path=f'{driver_path}msedgedriver.exe')
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        return None, 'pass'

    @keyword(name='浏览器最大化', param_conf={})
    def window_maximize(self, *args, **kwargs):
        self.driver.maximize_window()
        return None, 'pass'

    @keyword(name='进入新窗口', param_conf={})
    def switch_new_win(self, *args, **kwargs):
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        return None, 'pass'

    @keyword(name='返回上一个窗口', param_conf={})
    def switch_pre_win(self, *args, **kwargs):
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[0])
        return None, 'pass'

    @keyword(name='隐式等待', param_conf={'wait': '等待时间'})
    def implicitly_wait(self, *args, **kwargs):
        self.driver.implicitly_wait(int(kwargs['params']['wait']))
        return None, 'pass'

    @keyword(name='浏览器全屏', param_conf={})
    def window_full_screen(self, *args, **kwargs):
        self.driver.fullscreen_window()
        return None, 'pass'

    @keyword(name='截屏', param_conf={})
    def browser_screenshot(self, *args, **kwargs):
        return self.capture_screenshot(), 'pass'

    @keyword(name='打开网页', param_conf={'url': '网址'})
    def open_url(self, *args, **kwargs):
        url = kwargs['params']['url']
        self.driver.get(url)
        return None, 'pass'

    @keyword(name='关闭浏览器', param_conf={})
    def close_browser(self, *args, **kwargs):
        if self.driver:
            self.driver.quit()
            self.driver = None
        return None, 'pass'

    @keyword(name='关闭当前窗口', param_conf={})
    def close_current_window(self, *args, **kwargs):
        if self.driver:
            self.driver.close()
        return None, 'pass'

    @keyword(name='跳转到iframe', param_conf={'element': 'iframe'})
    def switch_to_iframe(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        iframe = self.driver.find_element(by=by, value=exp)
        self.driver.switch_to.frame(iframe)
        return None, 'pass'

    @keyword(name='切回默认iframe', param_conf={})
    def switch_to_default_content(self, *args, **kwargs):
        self.driver.switch_to.default_content()
        return None, 'pass'

    @keyword(name='单击元素', param_conf={'element': '元素'})
    def click_element(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        self.driver.find_element(by=by, value=exp).click()
        return None, 'pass'

    @keyword(name='输入文本', param_conf={'element': '元素', 'text': '文本'})
    def send_text(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        self.driver.find_element(by=by, value=exp).send_keys(kwargs['params']['text'])
        return None, 'pass'

    @keyword(name='获取元素文本', param_conf={'element': '元素'})
    def get_el_text(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        text = self.driver.find_element(by=by, value=exp).text
        return text, 'pass'

    @keyword(name='元素显示', param_conf={'element': '元素'})
    def el_is_displayed(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        try:
            self.driver.find_element(by=by, value=exp).is_displayed()
            return '元素在页面显示', 'pass'
        except Exception as e:
            return '元素没有显示', 'fail'

    @keyword(name='获取元素属性值', param_conf={'element': '元素', 'attrName': '属性名称'})
    def get_el_attr(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        attr = self.driver.find_element(by=by, value=exp).get_attribute(name=kwargs['params']['attrName'])
        return attr, 'pass'

    @keyword(name='滚动到元素', param_conf={'element': '元素'})
    def scroll_to_el(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        el = self.driver.find_element(by=by, value=exp)
        self.driver.execute_script("arguments[0].scrollIntoView();", el)
        return None, 'pass'

    @keyword(name='鼠标单击元素', param_conf={'element': '元素'})
    def mouse_click_element(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        el = self.driver.find_element(by=by, value=exp)
        actions = ActionChains(self.driver)
        actions.click(el).perform()
        return None, 'pass'

    @keyword(name='鼠标右键点击', param_conf={'element': '元素'})
    def mouse_right_click(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        el = self.driver.find_element(by=by, value=exp)
        actions = ActionChains(self.driver)
        actions.context_click(el).perform()
        return None, 'pass'

    @keyword(name='鼠标双击', param_conf={'element': '元素'})
    def mouse_double_click(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        el = self.driver.find_element(by=by, value=exp)
        actions = ActionChains(self.driver)
        actions.double_click(el).perform()
        return None, 'pass'

    @keyword(name='鼠标悬停', param_conf={'element': '元素'})
    def mouse_hover(self, *args, **kwargs):
        element = kwargs['params']['element']
        by = element['findType']
        exp = element['expression']
        el = self.driver.find_element(by=by, value=exp)
        actions = ActionChains(self.driver)
        actions.move_to_element(el).perform()
        return None, 'pass'

    @keyword(name='鼠标移动到坐标', param_conf={'x': 'x坐标', 'y': 'y坐标'})
    def mouse_mt_location(self, *args, **kwargs):
        x = int(kwargs['params']['x'])
        y = int(kwargs['params']['y'])
        actions = ActionChains(self.driver)
        actions.move_by_offset(xoffset=x, yoffset=y).perform()
        return None, 'pass'

    @keyword(name='物理鼠标拖拽', param_conf={'x': 'x坐标', 'y': 'y坐标'})
    def real_mouse_move(self, *args, **kwargs):
        x = int(kwargs['params']['x'])
        y = int(kwargs['params']['y'])
        pyautogui.dragTo(x=x, y=y, duration=0.1)
        return None, 'pass'

    @keyword(name='鼠标拖放', param_conf={'element_1': '起始元素', 'element_2': '目标元素'})
    def mouse_drag_drop(self, *args, **kwargs):
        element_1 = kwargs['params']['element_1']
        element_2 = kwargs['params']['element_2']
        el1 = self.driver.find_element(by=element_1['findType'], value=element_1['expression'])
        el2 = self.driver.find_element(by=element_2['findType'], value=element_2['expression'])
        actions = ActionChains(self.driver)
        actions.drag_and_drop(el1, el2).perform()
        return None, 'pass'

    def capture_screenshot(self):
        file_name = f'{str(uuid.uuid4())}.png'
        self.driver.save_screenshot(filename=os.getcwd() + '/data/image/' + file_name)
        return BrowserImage(file_name)
