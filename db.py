"""
数据库操作常用功能
"""
import json
import time
import pymysql


class Db:
    """数据库操作类
    """

    def connect(self):
        """设置连接属性cursorclass返回查询结果为dict类型序列

        Returns:
            [type] -- 返回连接对象和指针
        """
        conn = pymysql.connect('10.41.56.123', 'root', 'lpwm86', 'wenming',
                               charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        return conn, cursor

    def query(self, sql: str):
        """根据传入的SQL语句执行查询

        Arguments:
            sql {str} -- 要执行的SQL语句

        Returns:
            str -- 返回json格式数据字符串
        """
        conn, cursor = self.connect()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return json.dumps(result, ensure_ascii=False)

    def check_user(self, username: str, password: str):
        """校验用户登录

        Arguments:
            username {str} -- 用户名
            password {str} -- 密码

        Returns:
            int -- 0:登陆失败 1:普通用户登陆成功 2:管理员登录成功
        """
        conn, cursor = self.connect()
        sql = 'select username,password from users where username=%s and password=%s'
        cursor.execute(sql, (username, password))
        data = cursor.fetchall()
        conn.close()
        if len(data):
            if username == data[0]['username'] and password == data[0]['password']:
                if username == 'admin':
                    return 2
                else:
                    return 1
            else:
                return 0
        else:
            return 0

    def random_questions(self):
        """随机抽取指定数量考题
        """
        num_tiankong = 5
        num_danxuan = 25
        num_duoxuan = 5
        num_panduan = 5
        conn, cursor = self.connect()
        # 填空题
        sql = 'select * from tiankong order by rand() limit %s'
        cursor.execute(sql, num_tiankong)
        tiankong = cursor.fetchall()
        # 单选题
        sql = 'select * from danxuan order by rand() limit %s'
        cursor.execute(sql, num_danxuan)
        danxuan = cursor.fetchall()
        # 拆分单选选项
        for i in range(0, len(danxuan)):
            danxuan[i]['options'] = danxuan[i]['options'].split(' ')
        # 多选题
        sql = 'select * from duoxuan order by rand() limit %s'
        cursor.execute(sql, num_duoxuan)
        duoxuan = cursor.fetchall()
        for i in range(0, len(duoxuan)):
            duoxuan[i]['options'] = duoxuan[i]['options'].split(' ')
        # 判断题
        sql = 'select * from panduan order by rand() limit %s'
        cursor.execute(sql, num_panduan)
        panduan = cursor.fetchall()
        conn.close()
        # 整合数据
        result = {'tiankong': tiankong, 'danxuan': danxuan,
                  'duoxuan': duoxuan, 'panduan': panduan}
        return result

    def check_answer(self, answer: dict):
        """校验填空题答案是否正确
           answer格式{'id' : 1, 'answer': '回答内容'}
        """
        conn, cursor = self.connect()
        sql = 'select answer from tiankong where id=%s'
        # 查询返回结果格式:{'answer': 'D'}
        cursor.execute(sql, answer['id'])
        correct_answer = cursor.fetchone()['answer']
        conn.close()
        correct_answers = correct_answer.split(' ')
        if len(correct_answers) > 1:
            # 多个答案情况
            answers = answer['answer'].split(' ')
            if len(answers) != len(correct_answers):
                # 答案数量不一致
                return False
            else:
                result = True
                for i in range(0, len(answers)):
                    if answers[i] != correct_answers[i]:
                        result = False

                return result
        else:
            # 单个答案情况
            if answer['answer'] == correct_answer:
                return True
            else:
                return False

    def history(self, username: str):
        """查询个人历史成绩
        """
        conn, cursor = self.connect()
        sql = 'select test_time,score from logs where username=%s order by test_time desc'
        cursor.execute(sql, username)
        result = cursor.fetchall()
        conn.close()
        return(result)

    def log(self, username: str, score: str = 0):
        """记录测试

        Arguments:
            username {str} -- 用户名            
            score {int} -- 测试分数
        """
        conn, cursor = self.connect()
        sql = 'insert into logs(username,test_time,score) values (%s, %s, %s)'
        test_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        result = cursor.execute(sql, (username, test_time, score))
        if result > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def dashboard(self):
        """后台首页数据
        """
        conn, cursor = self.connect()
        sql = "select count(username) as count from users"
        cursor.execute(sql)
        total_people = cursor.fetchone()['count']  # 总考生人数

        sql = "select count(username) as count from logs where test_time BETWEEN %s and %s;"
        start_time = time.strftime(
            '%Y-%m-%d', time.localtime(time.time())) + ' 00:00:00'
        end_time = time.strftime(
            '%Y-%m-%d', time.localtime(time.time())) + ' 23:00:00'
        cursor.execute(sql, (start_time, end_time))
        today_people = cursor.fetchone()['count']  # 今日进行测验次数

        sql = "select username,test_time from logs order by test_time desc limit 1"
        cursor.execute(sql)
        data = cursor.fetchone()
        recent_people = {
            'username': data['username'], 'test_time': data['test_time']}  # 最近测试

        sql = "select username,score from logs order by score desc limit 1"
        cursor.execute(sql)
        data = cursor.fetchone()
        best_people = {'username': data['username'], 'score': data['score']}

        sql = "select * from (select username,score from logs order by test_time desc)as tmp group by username order by score desc"
        cursor.execute(sql)
        chart_data = cursor.fetchall()  # 图表数据

        conn.close()
        return {
            'top_data': {
                'total_people': total_people,
                'today_people': today_people,
                'recent_people': recent_people,
                'best_people': best_people},
            'chart_data': chart_data
        }
