"""Flask主程序

Returns:
    [type] -- [description]
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db import Db
# import logging

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

# HOST = '0.0.0.0'
DEBUG = False
TEMPLATES_AUTO_RELOAD = True
JSON_AS_ASCII = False

dbo = Db()

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    """首页跳转至登录页面
    """
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """校验登录
    """
    data = request.form    # dict类型,调用需要使用['key']的方式
    uname = data['username']
    upwd = data['password']
    if dbo.check_user(uname, upwd) == 1:
        # 普通用户登录成功
        ques = dbo.random_questions(40)  # 设置抽取题目数量
        return render_template('index.html', questions=ques, username=uname)
    elif dbo.check_user(uname, upwd) == 2:
        # 管理员登录成功
        dashboard_data = dbo.dashboard()
        return render_template('/admin/admin.html', dash=dashboard_data['top_data'], chart_data=dashboard_data['chart_data'])
    else:
        return render_template('login.html')


@app.route('/check', methods=['POST'])
def check():
    """校验答题结果
    """
    data = request.form
    result = []
    for k, v in data.items():
        answer = {'id': k, 'answer': v}
        is_right = dbo.check_answer(answer)
        cur_result = {'id': k, 'is_right': is_right}
        result.append(cur_result)
        # print('Key: ' + k + ' Value: ' + v + ' Result: ' + str(result))
    return jsonify({'result': result})


@app.route('/log', methods=['POST'])
def log():
    """记录测试结果
    """
    data = request.form  # 接收表单数据使用.form
    print(data['username'] + data['score'])
    result = dbo.log(data['username'], data['score'])
    return jsonify({'result': result})


@app.route('/history', methods=['POST'])
def history():
    """查询个人历史记录
    """
    data = request.values   # 接收字典数据使用.values
    result = dbo.history(data['username'])
    return jsonify({'history': result})


@app.route('/admin', methods=['GET'])
def admin():
    """后台管理获取局部渲染HTML数据
    """
    data = request.values
    if data['type'] == 'dashboard':
        dashboard_data = dbo.dashboard()
        return render_template('/admin/dashboard.html', dash=dashboard_data['top_data'], chart_data=dashboard_data['chart_data'])
    if data['type'] == 'detail':
        return render_template('/admin/detail.html')


@app.route('/test', methods=['GET'])
def test():
    """测试用函数
    """
    return jsonify(dbo.dashboard())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
