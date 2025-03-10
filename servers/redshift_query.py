import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

class RedshiftQuery:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接到Redshift数据库"""
        try:
            self.conn = psycopg2.connect(
                host=os.environ.get('REDSHIFT_HOST'),
                port=os.environ.get('REDSHIFT_PORT'),
                dbname=os.environ.get('REDSHIFT_DBNAME'),
                user=os.environ.get('REDSHIFT_USER'),
                password=os.environ.get('REDSHIFT_PASSWORD')
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"无法连接到Redshift数据库: {e}")

    def disconnect(self):
        """断开与Redshift数据库的连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        if not self.conn or not self.cursor:
            self.connect()

        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"执行查询时出错: {e}")
            return []
        finally:
            self.disconnect()

def query_redshift(sql: str) -> List[Dict[str, Any]]:
    """
    执行Redshift查询的便捷函数
    
    :param sql: 要执行的SQL查询
    :return: 查询结果列表，每个结果是一个字典
    """

    rq = RedshiftQuery()
    return rq.execute_query(sql)

# 使用示例
if __name__ == "__main__":
    test_sql = "SELECT * FROM click_url_infos LIMIT 5"
    results = query_redshift(test_sql)
    for row in results:
        print(row)
