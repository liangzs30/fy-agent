import json
import os
import platform
import traceback

import requests

from entity.TestVo import PlatformApi, CaseLog
import tools.config as config
from tools.log_util import LogUtil

logger = LogUtil().logger


class HttpUtil:
    def __init__(self):
        self.session = requests.session()
        self.terminal_serial = f"{platform.uname()}{os.getcwd()}"
        self.domain = f"http://{config.get_config('env', 'domain')}"
        self.robot_code = config.get_config('env', 'code')
        self.API = PlatformApi.get_apis()
        self.token = self.login_platform()
        self.headers = {'content-type': 'application/json', 'Authorization': self.token}
        self.headers_2 = {'Authorization': self.token}

    def send_get(self, url: str, params: dict, headers: dict):
        try:
            response = self.session.get(url=url, params=params, headers=headers, timeout=5)
            return response
        except requests.exceptions.HTTPError as errh:
            logger.error("Http Error: %s", errh)  # 捕获HTTPError异常并打印
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting: %s", errc)  # 捕获ConnectionError异常并打印
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error: %s", errt)  # 捕获Timeout异常并打印
        except requests.exceptions.RequestException as err:
            logger.error("Oops: Something Else: %s", err)  # 捕获其他请求异常并打印

    def send_post(self, url, data, headers, files):
        try:
            response = self.session.post(url=url, data=data, headers=headers, files=files, timeout=5)
            return response
        except requests.exceptions.HTTPError as errh:
            logger.error("Http Error: %s", errh)  # 捕获HTTPError异常并打印
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting: %s", errc)  # 捕获ConnectionError异常并打印
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error: %s", errt)  # 捕获Timeout异常并打印
        except requests.exceptions.RequestException as err:
            logger.error("Oops: Something Else: %s", err)  # 捕获其他请求异常并打印

    def login_platform(self):
        uid = 'execMachine'
        headers = {"content-type": "application/json"}
        data = {"username": uid,
                "password": "BkAFDpW+xKVFD8qmqHEDjt0YliWlV6yNles0Vtyg1qQUSgs2LFSHOElDeowaBIMrVw+/SLdYRIaxNvX6/7milA==",
                "code": "64", "uuid": "captcha-code:b6d88562a12b4f129f12e7f4edd4c7a1"}
        url = f'{self.domain}/auth/machine/login'
        try:
            res = self.send_post(url=url, data=json.dumps(data), headers=headers, files=None)
            return res.json()['token']
        except Exception as e:
            logger.error("获取token失败: %s", traceback.format_exc())

    def send_heart_beat(self, ip_addr: str):
        body = {"uniqueCode": f"{self.robot_code}", "ipAddr": ip_addr, "terminalSerial": self.terminal_serial,
                "status": 1}
        try:
            resp = self.send_post(url=f"{self.domain}{self.API['send_heart_beat']}", data=json.dumps(body),
                                  headers=self.headers, files=None)
            if resp.status_code == 200:
                logger.info("发送心跳成功: %s", body)
            else:
                logger.info("发送心跳失败: %s, 即将重新登录获取token", resp.text)
                self.token = self.login_platform()
                self.headers = {'content-type': 'application/json', 'Authorization': self.token}
                self.headers_2 = {'Authorization': self.token}
        except Exception as e:
            logger.error("发送心跳失败: %s，异常原因: %s", body, e)
            self.token = self.login_platform()
            self.headers = {'content-type': 'application/json', 'Authorization': self.token}
            self.headers_2 = {'Authorization': self.token}

    def get_pending_tasks(self):

        resp = self.send_get(url=f"{self.domain}{self.API['queryTaskList']}/{self.robot_code}", headers=self.headers,
                             params={})
        if resp.status_code == 200:
            tasks = resp.json()
            return tasks
        else:
            return []

    def query_task_cases(self, task):
        resp = self.send_get(url=f"{self.domain}{self.API['queryTaskCaseByTaskId']}/{task['id']}", headers=self.headers,
                             params={})
        return resp.json()

    def update_task(self, task_id, status, end_time):
        body = {"taskId": task_id, "status": status, "endTime": end_time}
        self.send_post(url=f"{self.domain}{self.API['updateTask']}", headers=self.headers, data=json.dumps(body),
                       files=None)

    def create_report(self, task):
        body = {"runTask": {"id": task.task_id}, "projectID": task.project_id}
        self.send_post(url=f"{self.domain}{self.API['createReport']}", headers=self.headers, data=json.dumps(body),
                       files=None)

    def query_sys_params(self, env_id):
        resp = self.send_get(url=f"{self.domain}{self.API['queryTaskSysParams']}/{env_id}", headers=self.headers,
                             params={})
        return resp.json()

    def query_element(self, pid):
        resp = self.send_get(url=f"{self.domain}{self.API['queryProjectWebelements']}/{pid}", headers=self.headers,
                             params={})
        return resp.json()

    def query_stop_task(self, mid):
        resp = self.send_get(url=f"{self.domain}{self.API['queryStopTask']}/{mid}", headers=self.headers, params={})
        return resp

    def upload_logs(self, tid, data):
        resp = self.send_post(url=f"{self.domain}{self.API['uploadLogs']}/{tid}", data=json.dumps(data),
                              headers=self.headers, files=None)
        if resp.status_code == 200:
            logger.info("日志上传成功")
        else:
            logger.error("日志上传异常接口响应码: %s, 响应内容: %s", resp.status_code, resp.text)
        for case_log in data:
            CaseLog.delete_case_logs(case_log['id'])

    def upload_images(self, upload_files):
        resp = self.send_post(url=f"{self.domain}{self.API['uploadImages']}", files=upload_files,
                              headers=self.headers_2, data=None)
        if resp.status_code == 200:
            logger.info("图片上传成功")
        else:
            logger.error("图片上传异常接口响应码: %s, 响应内容: %s", resp.status_code, resp.text)

    def get_local_ip(self):
        resp = self.send_get(url=f"{self.domain}{self.API['getLocalIp']}", headers=self.headers, params={})
        return resp.json()['localIp']

    def get_machine_info(self):
        resp = self.send_get(url=f"{self.domain}{self.API['getMachineInfo']}/{self.robot_code}", headers=self.headers,
                             params={})
        return resp.json()
