import configparser
import datetime
import json
import os
import time
import traceback

from requests import Response

from entity.TestVo import Param, BrowserImage, WebElement, AssertResult
from tools.log_util import calc_time

# 获取ini文件对象
config = configparser.ConfigParser()
# 读取ini的文件名称
config.read(os.path.abspath(os.path.dirname(__file__)) + '/../config.ini', encoding="utf8")


def get_config(section: str, option: str):
    # print('path', os.path.abspath(os.path.dirname(__file__)))
    return config.get(section, option)


def keyword(name: str, param_conf: dict):
    def run(func):
        def wrapper(*args, **kwargs):
            result = 'pass'
            screen_shot = None
            log_detail = [{'title': '步骤名称', 'time': f'{datetime.datetime.now()}',
                           'content': f'开始执行 {name}'}]
            if kwargs.get('params'):
                real_param = Param.replace_param(kwargs['params'])
                if real_param == 'error':
                    result = 'error'
                    log_detail.append({'title': '错误信息', 'time': f'{datetime.datetime.now()}',
                           'content': '变量获取失败或函数执行异常'})
                    return log_detail, '100ms', result, screen_shot
                else:
                    kwargs['params'] = json.loads(real_param)
                content = ''
                for key in param_conf:
                    if 'element' in key:
                        element = WebElement.get_by_eid(kwargs['params'][key])
                        kwargs['params'][key] = element
                    content = f"{content}{param_conf[key]}:\n{kwargs['params'][key]}\n"
                if content != '':
                    log_detail.append({'title': '步骤参数', 'time': f'{datetime.datetime.now()}',
                                       'content': content})
            start_time = time.time()
            try:
                response, res = func(*args, **kwargs)
                if response is not None:
                    res_content = ''
                    if isinstance(response, Response):
                        res_content = f'{res_content}响应码:\n{response.status_code}\n响应头:\n{response.headers}\n响应体:\n{response.text}\n'
                    elif isinstance(response, BrowserImage):
                        screen_shot = f'/{time.strftime("%Y%m%d", time.localtime())}/{response.file_name}'
                    elif isinstance(response, AssertResult):
                        res_content = f'{res_content}断言结果:\n{response.result}\n'
                    else:
                        res_content = response
                    if res_content != '':
                        log_detail.append({'title': '响应信息', 'time': f'{datetime.datetime.now()}',
                                           'content': res_content})
                    if kwargs.get('step_resps'):
                        step_resps = json.loads(Param.replace_param(kwargs['step_resps']))
                        kwargs['step_resps'] = step_resps
                        svalues = Param.set_resp_var(response=response, step_resps=step_resps)
                        # print(svalues)
                        s_content = ''
                        j = 0
                        for step_resp in step_resps:
                            get_res = svalues[j] if svalues[j] else '提取异常......'
                            if get_res == '提取异常......':
                                s_content = '%s %s %s' % (
                                    s_content, f'变量 {step_resp["varName"]} 提取结果：{get_res}', '\n')
                                res = 'fail'
                                break
                            s_content = '%s %s %s' % (
                                s_content, f'变量 {step_resp["varName"]} 提取结果：{get_res}', '\n')
                        log_detail.append({'title': '提取变量', 'time': f'{datetime.datetime.now()}',
                                           'content': s_content})
                if res:
                    result = res
            except Exception as e:
                result = 'error'
                log_detail.append(
                    {'title': '错误信息', 'time': f'{datetime.datetime.now()}', 'content': traceback.format_exc()})
                if 'Browser' in str(func):
                    im = args[0].capture_screenshot()
                    screen_shot = f'/{time.strftime("%Y%m%d", time.localtime())}/{im.file_name}'
            end_time = time.time()
            cost_time = calc_time(start_time=start_time, end_time=end_time)
            log_detail.append(
                {'title': '步骤结束', 'time': f'{datetime.datetime.now()}', 'content': f'{name} 执行结束'})
            return log_detail, cost_time, result, screen_shot

        return wrapper

    return run
