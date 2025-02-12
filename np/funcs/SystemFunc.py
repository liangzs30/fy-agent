import random
import time
import uuid
from datetime import datetime


class FuncCollection01:
    @staticmethod
    def get_curr_time(time_format: str):
        #'%Y-%m-%d %H:%M:%S'
        now = datetime.now()
        # 格式化时间，例如：2023-03-25 10:05:23
        formatted_time = now.strftime(format=time_format)
        return formatted_time

    @staticmethod
    def get_stamp_thirteenth():
        return round(time.time() * 1000)

    @staticmethod
    def get_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def generate_phone_number():
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '147', '150', '151', '152',
                    '153', '155', '156', '157', '158', '159', '165', '170', '171', '172', '173', '175', '176', '177',
                    '178', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189', '198', '199']
        prefix = random.choice(prefixes)
        suffix = f"{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
        return prefix + suffix

