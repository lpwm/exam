"""题库操作类
"""
from db import Db


class Tiku:
    def __init__(self):
        self.dbo = Db()

    def get_all(self):
        """获取全部问题
        """
        sql = 'select * from questions'
        conn, cursor = self.dbo.connect()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result

    def add(self, title: str, answer: str):
        """添加问题
        """
        sql = 'insert into questions(title,answer) values("%s", "%s")'
        conn, cursor = self.dbo.connect()
        result = cursor.execute(sql % (title, answer))
        if result:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def update(self, id: int, title: str, answer: str):
        """更新单个问题

        Arguments:
            id {int} -- 编号
            title {str} -- 题目
            question {str} -- 答案

        Returns:
            [type] -- True:修改成功 False:修改失败
        """
        sql = 'update questions set title="%s", answer="%s" where id="%s"'
        conn, cursor = self.dbo.connect()
        result = cursor.execute(sql % (title, answer, id))
        if result:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def remove(self, id: int):
        """删除单个问题
        """
        sql = 'delete from questions where id="%s"'
        conn, cursor = self.dbo.connect()
        result = cursor.execute(sql % id)
        if result:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def query(self, keyword: str):
        """根据题目关键字查询
        """
        sql = 'select * from questions where title like %s'
        conn, cursor = self.dbo.connect()
        cursor.execute(sql, ('%' + keyword + '%'))
        result = cursor.fetchall()
        conn.close()
        return result
