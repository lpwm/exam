import json
import itertools
from operator import itemgetter
from db import Db


class Calc:
    """计算成绩类
    """

    def __init__(self):
        self.dbo = Db()

    def calc_single(self, key, group):
        """计算单个题目
        """
        id, type_timu = key.split('-')  # 题目编号, 题目类型
        group = list(group)  # 将itertools._grouper类型转为list

        if type_timu == 'tiankong':
            user_answers = group[0]['value'].split(' ')
            conn, cursor = self.dbo.connect()
            sql = 'select answer from tiankong where id=%s'
            cursor.execute(sql, id)
            correct_answer = cursor.fetchone()['answer']
            correct_answers = correct_answer.split(' ')
            conn.close()

            if len(user_answers) != len(correct_answers):
                # 答案数量不一致
                return {'id': key, 'result': False, 'correct_answer': correct_answer}
            else:
                result = True
                for i in range(0, len(user_answers)):
                    if user_answers[i] != correct_answers[i]:
                        result = False
                return {'id': key, 'result': result, 'correct_answer': correct_answer}

        if type_timu == 'danxuan':
            user_answers = group[0]['value']
            conn, cursor = self.dbo.connect()
            sql = 'select answer from danxuan where id=%s'
            cursor.execute(sql, id)
            correct_answer = cursor.fetchone()['answer']
            conn.close()

            if user_answers != correct_answer:
                return {'id': key, 'result': False, 'correct_answer': correct_answer}
            else:
                return {'id': key, 'result': True, 'correct_answer': correct_answer}

        if type_timu == 'duoxuan':
            user_answers = []
            for item in group:
                user_answers.append(item['value'])  # 拼接用户答案

            conn, cursor = self.dbo.connect()
            sql = 'select answer from duoxuan where id=%s'
            cursor.execute(sql, id)
            # 数据库中多选题答案格式为ABCD中间没有空格,直接使用list将其转换为数组
            correct_answer = cursor.fetchone()['answer']
            correct_answers = list(correct_answer)
            conn.close()

            if len(user_answers) != len(correct_answers):
                # 答案数量不一致
                return {'id': key, 'result': False, 'correct_answer': correct_answer}
            else:
                result = True
                for i in range(0, len(user_answers)):
                    if user_answers[i] != correct_answers[i]:
                        result = False
                return {'id': key, 'result': result, 'correct_answer': correct_answer}

        if type_timu == 'panduan':
            user_answers = group[0]['value']
            conn, cursor = self.dbo.connect()
            sql = 'select answer from panduan where id=%s'
            cursor.execute(sql, id)
            correct_answer = cursor.fetchone()['answer']
            conn.close()

            if user_answers != correct_answer:
                return {'id': key, 'result': False, 'correct_answer': correct_answer}
            else:
                return {'id': key, 'result': True, 'correct_answer': correct_answer}

    def calc_score(self, answers):
        """计算成绩

        Arguments:
            answers {json} -- 前端的form进行serializeArray()后再json.stringfy的数据
        """
        total_score = 0
        detail_result = []
        sorted_data = sorted(answers, key=itemgetter('name'))  # 先进行排序
        for key, group in itertools.groupby(sorted_data, key=lambda x: x['name']):
            single_result = self.calc_single(key, group)
            if single_result['result']:
                total_score += 1
            detail_result.append(single_result)

        return_data = {'total_score': total_score, 'detail': detail_result}
        return return_data
