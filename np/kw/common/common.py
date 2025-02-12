import re
import time

from entity.TestVo import Param, AssertResult
from tools.config import keyword


class Common:

    @keyword(name='暂停（单位：秒）', param_conf={'time': '暂停时长'})
    def sleep(self, *args, **kwargs):
        time.sleep(int(kwargs['params']['time']))
        return None, 'pass'

    @keyword(name='断言', param_conf={'result': '实际结果', 'assert_type': '断言类型', 'expected': '预期结果'})
    def assert_result(self, *args, **kwargs):
        params = kwargs.get('params')
        result = params.get('result')
        result = result if self.find_param(result) else Param.get_param(result)
        assert_type = params.get('assert_type')
        expected = params.get('expected')
        assert_result = 'error'
        if assert_type == 'equal':
            assert_result = result == expected
        elif assert_type == 'notequal':
            assert_result = result != expected
        elif assert_type == 'contain':
            assert_result = expected in result
        elif assert_type == 'not contain':
            assert_result = expected not in result
        elif assert_type == '>':
            assert_result = eval(result) > eval(expected)
        elif assert_type == '>=':
            assert_result = eval(result) >= eval(expected)
        elif assert_type == '<':
            assert_result = eval(result) < eval(expected)
        elif assert_type == '<=':
            assert_result = eval(result) <= eval(expected)
        elif assert_type == 'not none':
            assert_result = result is not None
        elif assert_type == 'none':
            assert_result = result is None
        elif assert_type == 'true':
            assert_result = result if result else False
        elif assert_type == 'false':
            assert_result = True if not result else False
        if assert_result:
            assert_result = 'pass'
        else:
            assert_result = 'fail'
        return AssertResult(assert_result), assert_result

    @keyword(name='if条件执行', param_conf={'condition': '条件表达式', 'step_index': '条件覆盖的步骤'})
    def exec_if(self, *args, **kwargs):
        pass_steps = []
        not_exec_step = int(kwargs['params']['step_index'])
        try:
            expression = eval(kwargs['params']['condition'])
            if not isinstance(expression, bool):
                return {'判断结果': f"表达式{kwargs['params']['condition']}有误", 'wont_run': pass_steps}, 'error'
            if not expression:
                for i in range(not_exec_step):
                    pass_steps.append(i)
            if len(pass_steps) == 0:
                return {'判断结果': f'满足，将执行接下来{not_exec_step}个步骤', 'wont_run': pass_steps}, 'pass'
            return {'判断结果': f'不满足，不执行接下来{not_exec_step}个步骤', 'wont_run': pass_steps}, 'pass'
        except Exception as e:
            return {'判断结果': f"表达式{kwargs['params']['condition']}有误", 'wont_run': pass_steps}, 'error'

    @keyword(name='for循环执行', param_conf={'loop_time': '循环次数', 'step_index': '循环的步骤范围'})
    def exec_for_loop(self, *args, **kwargs):
        return None, 'pass'

    @staticmethod
    def find_param(data: str):
        pattern_p = r'\$\{([^}]+)\}'
        p_key = re.findall(pattern_p, data)
        if len(p_key) > 0:
            return False
        return True
