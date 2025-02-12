import json

from tools.config import keyword
import pymysql


class MysqlClient:
    def __init__(self):
        self.conn = None
        self.cursor = None

    @keyword(name='创建mysql连接',
             param_conf={'host': '主机地址', 'port': '数据库端口', 'user': '用户名', 'password': '密码',
                         'database': '数据库'})
    def create_conn(self, *args, **kwargs):
        params = kwargs['params']
        self.conn = pymysql.connect(
            host=params['host'],
            port=int(params['port']),
            user=params['user'],
            password=params['password'],
            database=params['database'],
            charset='utf8'
        )
        self.cursor = self.conn.cursor()
        return None, 'pass'

    @keyword(name='执行mysql查询', param_conf={'sql': 'sql语句'})
    def execute_query(self, *args, **kwargs):
        params = kwargs['params']
        self.cursor.execute(params['sql'])
        results = self.cursor.fetchall()
        # 将结果转换为字典列表（假设第一行是列名）或直接转换为JSON字符串。这里使用字典列表形式。
        column_names = [desc[0] for desc in
                        self.cursor.description]
        resp = [dict(zip(column_names, row)) for row in results]
        return resp, 'pass'

    @keyword(name='mysql非查询操作', param_conf={'sql': 'sql语句'})
    def execute_sql(self, *args, **kwargs):
        params = kwargs['params']
        self.cursor.execute(params['sql'])
        self.conn.commit()
        return None, 'pass'

    @keyword(name='关闭mysql连接', param_conf={})
    def close_conn(self, *args, **kwargs):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return None, 'pass'
