import json
import os
import re
import sqlite3

import jsonpath

from np.funcs import SystemFunc
from tools.log_util import LogUtil

logger = LogUtil().logger


def create_conn():
    conn = sqlite3.connect(f'{os.getcwd()}/test.db')
    cursor = conn.cursor()
    return conn, cursor


class Task:
    def __init__(self, task_id, name, env, test_cases, start_time, end_time, project_id):
        self.task_id = task_id
        self.name = name
        self.env = json.dumps(env)
        self.test_cases = test_cases
        self.start_time = start_time
        self.end_time = end_time
        self.project_id = project_id

    def save(self):
        sql = 'INSERT INTO `task` (task_id, name, env, test_cases, start_time, end_time, project_id) values (?,?,?,?,?,?,?)'
        conn, cursor = create_conn()
        cursor.execute(sql, [self.task_id, self.name, self.env, '', self.start_time, self.end_time, self.project_id])
        conn.commit()
        cursor.close()
        conn.close()

    def delete(self):
        conn, cursor = create_conn()
        sql = 'DELETE FROM `task` WHERE `task_id`=?'
        cursor.execute(sql, [self.task_id])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_task():
        conn, cursor = create_conn()
        cursor.execute('SELECT * FROM `task` LIMIT 1;')
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return Task(task_id=row[1], name=row[2], env=row[3], test_cases=row[4], start_time=row[5], end_time=row[6],
                    project_id=row[7])

    @staticmethod
    def get_task_status():
        conn, cursor = create_conn()
        '''设置当前是否在执行任务'''
        cursor.execute('SELECT status FROM `task_status` LIMIT 1;')
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0]

    @staticmethod
    def update_status(status):
        conn, cursor = create_conn()
        '''更新任务状态'''
        cursor.execute('UPDATE `task_status` SET status=?;', [status])
        conn.commit()
        cursor.close()
        conn.close()


class CaseLog:
    def __init__(self, task_id, case_no, case_title, case_desc, log_text, cost_time, exe_sort, result, project_id):
        self.task_id = task_id
        self.case_no = case_no
        self.case_title = case_title
        self.case_desc = case_desc
        self.logText = log_text
        self.costTime = cost_time
        self.exeSort = exe_sort
        self.result = result
        self.project_id = project_id

    def save(self):
        conn, cursor = create_conn()
        sql = 'INSERT INTO `caseLog` (task_id, case_no, case_title, case_desc, log_text, cost_time, exe_sort, result, project_id) values (?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, [self.task_id, self.case_no, self.case_title, self.case_desc, self.logText, self.costTime,
                             self.exeSort, self.result, self.project_id])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_case_logs():
        logs = []
        tid = None
        conn, cursor = create_conn()
        cursor.execute("SELECT task_id from caseLog ORDER BY id desc limit 1;")
        _row = cursor.fetchone()
        if _row:
            tid = _row[0]
            cursor.execute('SELECT * FROM `caseLog` where task_id=? order by id', [tid])
            rows = cursor.fetchall()
            for row in rows:
                logs.append(
                    {'id': row[0], 'executeSort': row[0], 'runTaskId': row[1], 'caseNo': row[2], 'caseTitle': row[3],
                     'caseDesc': row[4],
                     'result': row[8], 'stepLog': row[6], 'costTime': row[7], 'projectID': row[9]})
        cursor.close()
        conn.close()
        return tid, logs

    @staticmethod
    def delete_case_logs(cid: int):
        conn, cursor = create_conn()
        sql = 'DELETE FROM `caseLog` WHERE id=?'
        cursor.execute(sql, [cid])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def clear_case_logs():
        conn, cursor = create_conn()
        sql1 = 'DELETE FROM `caseLog`'
        cursor.execute(sql1)
        conn.commit()
        sql2 = 'DELETE FROM sqlite_sequence WHERE name=?;'
        cursor.execute(sql2, ['caseLog'])
        conn.commit()
        cursor.close()
        conn.close()


class PlatformApi:
    @staticmethod
    def get_apis():
        conn, cursor = create_conn()
        '''获取API集合'''
        apis = {}
        cursor.execute("SELECT * FROM `platform_api`;")
        rows = cursor.fetchall()
        for row in rows:
            apis[row[0]] = row[1]
        cursor.close()
        conn.close()
        return apis


class WebElement:
    @staticmethod
    def save_web_elements(elements):
        conn, cursor = create_conn()
        for element in elements:
            cursor.execute('INSERT INTO `web_element` (eid, find_type, expression, pid) values (?,?,?,?);',
                           [element['id'], element['findType'], element['expression'], element['projectID']])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete_all():
        conn, cursor = create_conn()
        cursor.execute('DELETE FROM `web_element`;')
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_eid(id: int):
        conn, cursor = create_conn()
        cursor.execute('SELECT * FROM `web_element` WHERE eid=?;', [id])
        row = cursor.fetchone()
        if row:
            return {'findType': row[2], 'expression': row[3]}
        cursor.close()
        conn.close()


class StopTask:
    @staticmethod
    def save_task(mid, stop_id):
        conn, cursor = create_conn()
        sql = 'INSERT INTO `stop_task` (tid, mid) values (?,?);'
        cursor.execute(sql, [stop_id, mid])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete_all():
        conn, cursor = create_conn()
        cursor.execute('DELETE FROM `stop_task`;')
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_mid(mid: int):
        conn, cursor = create_conn()
        cursor.execute('SELECT tid FROM `stop_task` WHERE mid=?;', [mid])
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.close()
        conn.close()


class Param:
    @staticmethod
    def save_params(params):
        conn, cursor = create_conn()
        for param in params:
            cursor.execute('INSERT INTO `sys_params` (name,value) values (?,?);', [param['name'], param['value'], ])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def save(param):
        conn, cursor = create_conn()
        temp_parma = Param.get_by_name(param['name'])
        if temp_parma:
            cursor.execute('UPDATE `sys_params` set value=? where name=?;',
                           [param['value'], param['name']])
        else:
            cursor.execute('INSERT INTO `sys_params` (name,value) values (?,?);', [param['name'], param['value'], ])
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete_all():
        conn, cursor = create_conn()
        cursor.execute('DELETE FROM `sys_params`;')
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_name(name: str):
        conn, cursor = create_conn()
        cursor.execute('SELECT * FROM `sys_params` WHERE name=?;', [name])
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'value': row[2]}
        cursor.close()
        conn.close()
        return False

    @staticmethod
    def replace_param(data: str):
        try:
            pattern_p = r'\$\{([^}]+)\}'
            pattern_f = r'\@\{([^}]+)\}'
            plist = re.findall(pattern_p, data)
            flist = re.findall(pattern_f, data)
            for i in plist:
                re_str = Param.get_by_name(i)
                if re_str['value']:
                    old = "{}{}{}".format('${', i, '}')
                    data = data.replace(old, re_str['value'])
                else:
                    logger.error("替换变量: %s失败，找不到变量", i)
            for j in flist:
                func_name = j.split('(')[0]
                temp = re.findall('\((.*?)\)', j)[0]
                params = eval(temp) if temp != '' else ''
                new_str = getattr(SystemFunc.FuncCollection01, func_name)(*params)
                if new_str:
                    old = "{}{}{}".format('@{', j, '}')
                    data = data.replace(old, str(new_str))
                else:
                    logger.error("函数: %s执行失败", func_name)
            return data
        except Exception as e:
            return 'error'

    @staticmethod
    def get_param(data: str):
        pattern_p = r'\$\{([^}]+)\}'
        p_key = re.findall(pattern_p, data)[0]
        re_str = Param.get_by_name(p_key)['value']
        return re_str

    @staticmethod
    def set_resp_var(response, step_resps):
        values = []
        for step_resp in step_resps:
            if step_resp['respType'] == 'api':
                if step_resp['path'] == 'status_code':
                    value = response.status_code
                    Param.save({'name': step_resp['varName'], 'value': value})
                    values.append(value)
                elif step_resp['path'] == 'headers' and step_resp['findType'] == 'regex':
                    res = re.findall(str(response.headers), step_resp['expression'])
                    value = res[0] if res else None
                    Param.save({'name': step_resp['varName'],
                                'value': value})
                    values.append(value)
                elif step_resp['path'] == 'headers' and step_resp['findType'] == 'jsonpath':
                    res = jsonpath.jsonpath(response.headers, step_resp['expression'])
                    value = res[0] if res else None
                    Param.save({'name': step_resp['varName'],
                                'value': value})
                    values.append(value)
                elif step_resp['path'] == 'body' and step_resp['findType'] == 'regex':
                    res = re.findall(response.text, step_resp['expression'])
                    value = res[0] if res else None
                    Param.save({'name': step_resp['varName'],
                                'value': value})
                    values.append(value)
                elif step_resp['path'] == 'body' and step_resp['findType'] == 'jsonpath':
                    res = jsonpath.jsonpath(response.json(), step_resp['expression'])
                    value = res[0] if res else None
                    Param.save({'name': step_resp['varName'],
                                'value': value})
                    values.append(value)
            elif step_resp['respType'] == 'dict':
                res = jsonpath.jsonpath(response, step_resp['expression'])
                value = res[0] if res else None
                Param.save({'name': step_resp['varName'],
                            'value': value})
                values.append(value)
            elif step_resp['respType'] == 'string':
                res = re.findall(response, step_resp['expression'])
                value = response if len(res) == 0 else res[0] if len(res) > 0 else None
                Param.save({'name': step_resp['varName'],
                            'value': value})
                values.append(value)
            else:
                logger.error("提取失败，提取途径: %s, 提取方式: %s, 表达式: %s", step_resp['path'],
                             step_resp['findType'], step_resp['expression'])
                values.append(False)
            return values


class BrowserImage:
    def __init__(self, file_name):
        self.file_name = file_name


class AssertResult:
    def __init__(self, result):
        self.result = result
