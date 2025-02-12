# 创建logger
import logging
import os
from datetime import datetime


class LogUtil:
    def __init__(self):
        logger = logging.getLogger('engine_logger')
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        # 创建FileHandler，输出到log.txt文件
        current_folder = os.getcwd()
        file_handler = logging.FileHandler(
            filename=current_folder + '/log/' + str(datetime.now().strftime('%Y-%m-%d')) + '.log')
        file_handler.setLevel(logging.DEBUG)

        # 创建formatter并添加到handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        # 将handler添加到logger
        logger.addHandler(file_handler)
        self.logger = logger


def calc_time(start_time, end_time):
    execution_time = end_time - start_time  # 计算执行时间
    if execution_time <= 1:
        cost_time = f"{execution_time * 1000:.2f}ms"
    else:
        cost_time = f"{execution_time:.2f}s"
    return cost_time
