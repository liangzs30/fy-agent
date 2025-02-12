import datetime
import json
import os
import time
from functools import partial
import traceback
from entity.TestVo import Task, CaseLog, Param, WebElement, StopTask
from np.kw.api.http import HttpClient
from np.kw.common.common import Common
from np.kw.db.dboper import MysqlClient
from np.kw.web.web import Browser

from apscheduler.schedulers.blocking import BlockingScheduler

from tools.http_client import HttpUtil
from tools.log_util import calc_time, LogUtil

driver = Browser()
db_class = MysqlClient()
step_class = {'HttpClient': HttpClient(), 'Common': Common(), 'Browser': driver, 'MysqlClient': db_class}
logger = LogUtil().logger
http_util = HttpUtil()
scheduler = BlockingScheduler()


def execute_step(**kwargs):
    test_step = kwargs['test_step']
    test_steps = kwargs['test_steps']
    pass_steps = kwargs['pass_steps']
    loop_steps = kwargs['loop_steps']
    step_index = kwargs['step_index']
    log_text = kwargs['log_text']
    if test_step['enabled']:
        log_dict = {'stepName': test_step['kw']['name'],
                    'stepDesc': test_step['desc'] if test_step.get('desc') else ''}
        try:
            module_name = test_step['kw']['className']
            method_name = test_step['kw']['funcName']
            mould = step_class[module_name]
            method = getattr(mould, method_name)
            kwargs = {}
            if test_step['stepParam']:
                kwargs['params'] = test_step['stepParam']
            if test_step['stepResps'] != '[]':
                kwargs['step_resps'] = test_step['stepResps']
            log_dict['logDetail'], log_dict['cost_time'], log_dict['result'], log_dict[
                'screen_shot'] = method(mould, **kwargs)
            if test_step['kw']['name'] == 'if条件执行':
                wont_run = log_dict['logDetail'][2]['content']['wont_run']
                for s in wont_run:
                    pass_steps.append(step_index + s + 1)
            if test_step['kw']['name'] == 'for循环执行':
                loop_params = json.loads(test_step['stepParam'])
                loop_steps['time'] = int(loop_params['loop_time'])
                l_index = int(loop_params['step_index'])
                loop_steps['steps'] = test_steps[step_index + 1: l_index + 1]
            case_result = log_dict['result']
            log_text.append(log_dict)
            return case_result, log_text, pass_steps, loop_steps
        except Exception as e:
            log_dict['logDetail'] = [{'title': '错误信息', 'time': f'{datetime.datetime.now()}',
                                      'content': traceback.format_exc()}]
            log_dict['result'] = 'error'
            case_result = 'error'
            log_text.append(log_dict)
            logger.error("步骤执行异常: %s", e)
            return case_result, log_text, pass_steps, loop_steps


def run_task(robot_id: int):
    is_running = Task.get_task_status()
    if is_running == 0:
        try:
            tasks = http_util.get_pending_tasks()
            if len(tasks) == 0:
                return
            Param.delete_all()
            WebElement.delete_all()
            test_cases = http_util.query_task_cases(task=tasks[0])
            # print('cases: ', resp.text)
            task = Task(task_id=tasks[0]['id'], name=tasks[0]['name'], env=tasks[0]['runEnv'], test_cases=test_cases,
                        start_time=tasks[0]['startTime'], end_time='', project_id=tasks[0]['projectID'])
            task.save()
            http_util.update_task(task_id=task.task_id, status='running', end_time=0)
            http_util.create_report(task=task)
            Task.update_status(1)
            sys_params = http_util.query_sys_params(tasks[0]['runEnv']['id'])
            Param.save_params(sys_params)
            web_elements = http_util.query_element(pid=tasks[0]['projectID'])
            WebElement.save_web_elements(web_elements)
            stop = 0
            for case in task.test_cases:
                tid = StopTask.get_by_mid(robot_id)
                if tid == task.task_id:
                    task_complete(task)
                    stop = 1
                    logger.info("任务id: %s, 名称: %s终止执行", tid, task.name)
                    break
                case_result = 'pass'
                start_time = time.time()
                log_text = []
                case_log = CaseLog(task_id=task.task_id, case_no=case['caseNo'], case_title=case['caseTitle'],
                                   case_desc=case['desc'] if case.get('desc') else '', log_text='', cost_time='',
                                   exe_sort=case['executeSort'],
                                   result='', project_id=case['projectID'])
                test_steps = case['testSteps']
                try:
                    step_index = 0
                    pass_steps = []
                    loop_steps = {'time': 0, 'steps': []}
                    for testStep in test_steps:
                        break_loop = False
                        if step_index in pass_steps:
                            step_index += 1
                            continue
                        if loop_steps['time'] != 0:
                            for i in range(loop_steps['time'] - 1):
                                if break_loop:
                                    break
                                for step in loop_steps['steps']:
                                    case_result, log_text, pass_steps, loop_steps = execute_step(test_step=step,
                                                                                                 test_steps=test_steps,
                                                                                                 pass_steps=pass_steps,
                                                                                                 loop_steps=loop_steps,
                                                                                                 step_index=step_index,
                                                                                                 log_text=log_text)
                                    if case_result != 'pass':
                                        break_loop = True
                                        break
                            loop_steps = {'time': 0, 'steps': []}
                        if break_loop:
                            break
                        case_result, log_text, pass_steps, loop_steps = execute_step(test_step=testStep,
                                                                                     test_steps=test_steps,
                                                                                     pass_steps=pass_steps,
                                                                                     loop_steps=loop_steps,
                                                                                     step_index=step_index,
                                                                                     log_text=log_text)
                        if case_result != 'pass':
                            break
                        step_index += 1
                except Exception as e:
                    logger.error("用例执行异常: %s", traceback.format_exc())
                    case_result = 'error'
                case_log.logText = json.dumps(log_text)
                case_log.result = case_result
                end_time = time.time()
                execution_time = calc_time(start_time=start_time, end_time=end_time)  # 计算执行时间
                case_log.costTime = execution_time
                case_log.save()
            if stop == 0:
                task_complete(task)
        except Exception as e:
            logger.error("任务执行异常: %s", e)


def task_complete(task):
    driver.close_browser()
    db_class.close_conn()
    StopTask.delete_all()
    Task.delete(task)
    Task.update_status(0)


def send_logs_images(robot_id: int):
    is_running = Task.get_task_status()
    tid = StopTask.get_by_mid(robot_id)
    if is_running == 1 and tid is None:
        r = http_util.query_stop_task(robot_id)
        if r.text and r.status_code == 200:
            StopTask.save_task(robot_id, int(r.text))
    t_id, data = CaseLog.get_case_logs()
    if len(data) > 0:
        http_util.upload_logs(tid=t_id, data=data)
    upload_files = []
    rm_files = []
    for root, dirs, files in os.walk(f'{os.getcwd()}/data/image'):
        for file in files:
            upload_files.append(('files', (file, open(os.path.join(root, file), 'rb').read(), 'image/png')))
            rm_files.append(os.path.join(root, file))
    if len(upload_files) > 0:
        http_util.upload_images(upload_files=upload_files)
        for file in rm_files:
            os.remove(file)


def main():
    Task.update_status(0)
    CaseLog.clear_case_logs()
    local_ip = http_util.get_local_ip()
    machine_info = http_util.get_machine_info()
    if machine_info['status'] == 400:
        raise "执行机不存在，请检查uniqueCode"
    elif machine_info.get('terminalSerial') and machine_info['status'] == 1 and machine_info[
        'terminalSerial'] != http_util.terminal_serial:
        raise "执行机正被使用，不能启动两个相同的执行机"
    robot_id = machine_info['id']
    http_util.send_heart_beat(ip_addr=local_ip)
    print(f"""
    *************************************
    执行机: {machine_info['name']} 启动成功
    版本: 1.1.0
    本机ip: {local_ip}     
    平台domain: {http_util.domain}                     
    *************************************
     _      __    __                     __         ___       __          __ 
    | | /| / /__ / /______  __ _  ___   / /____    / _/_ __  / /____ ___ / /_
    | |/ |/ / -_) / __/ _ \/  ' \/ -_) / __/ _ \  / _/ // / / __/ -_|_-</ __/
    |__/|__/\__/_/\__/\___/_/_/_/\__/  \__/\___/ /_/ \_, /  \__/\__/___/\__/ 
                                                    /___/                                           
    """)
    # 创建调度器

    partial_job_send_heart_beat = partial(http_util.send_heart_beat, ip_addr=local_ip)
    partial_job_send_logs_images = partial(send_logs_images, robot_id=robot_id)
    partial_job_run_task = partial(run_task, robot_id=robot_id)
    # 添加任务，每150秒执行一次上报心跳
    scheduler.add_job(partial_job_send_heart_beat, 'interval', seconds=60)
    # 执行任务
    scheduler.add_job(partial_job_run_task, 'interval', seconds=5, max_instances=10)
    # 上报日志、图片
    scheduler.add_job(partial_job_send_logs_images, 'interval', seconds=10)
    # 启动定时任务
    scheduler.start()
