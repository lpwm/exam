"""Flask主程序

Returns:
    [type] -- [description]
"""
from flask import Flask, request, session, redirect, url_for, jsonify, render_template
from flask_cors import CORS
from db import Db
from Tiku import Tiku
from calc import Calc
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
# 修改jinja模板标签加入空格,解决和VUE模板语法的冲突
app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'
# 设置session用到的密钥
app.secret_key = b'4lgNukRBXhn-5oRPBZxpsw'
CORS(app)


@app.route('/', methods=['GET'])
def index():
    """首页跳转至登录页面
    """
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """校验登录
    """
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        data = request.form    # dict类型,调用需要使用['key']的方式
        uname = data['username']
        upwd = data['password']
        if dbo.check_user(uname, upwd) == 1:
            # 普通用户登录成功
            session['username'] = uname  # 保存session会话
            return redirect('/')

        elif dbo.check_user(uname, upwd) == 2:
            # 管理员登录成功
            dashboard_data = dbo.dashboard()
            return render_template('/admin/admin.html', dash=dashboard_data['top_data'], chart_data=dashboard_data['chart_data'])
        else:
            return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """注销登录
    """
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/home', methods=['GET'])
def home():
    """首页导航
    """
    if 'username' in session:
        if 'action' in request.args:    # 带参数的访问
            action = request.values['action']
            if action == 'simulate':
                ques = dbo.random_questions()  # 获取随机题库
                return render_template('moni.html', questions=ques, username=session['username'])
            if action == 'single':
                ques = dbo.random_questions()  # 获取随机题库
                return render_template('zhuanxiang.html', questions=ques, username=session['username'])

            return render_template('home.html')

        else:
            render_template('home.html')    # 不带参数直接返回导航页面

    else:
        return redirect('/')


@app.route('/get', methods=['GET'])
def get():
    """异步获取首页题目数据
    """
    ques = dbo.random_questions()
    return jsonify(ques)


@app.route('/check', methods=['POST'])
def check():
    """校验答题结果
    """
    data = request.json
    cal = Calc()
    result = cal.calc_score(data)
    return jsonify(result)


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
    if data['type'] == 'db_manage':
        return render_template('/admin/db_manage.html')


@app.route('/op', methods=['POST'])
def op():
    """题库操作,需要传入json数据
    """
    tk = Tiku()
    result = ''
    data = request.json
    op_type = data['type']

    if op_type == 'update':
        args = data['args']
        result = tk.update(args['id'], args['title'], args['answer'])
        new_tk = tk.get_all()  # 重新获取最新的题库数据
        return jsonify({'tiku': new_tk})
    if op_type == 'add':
        args = data['args']
        result = tk.add(args['title'], args['answer'])
        new_tk = tk.get_all()  # 重新获取最新的题库数据
        return jsonify({'tiku': new_tk})
    if op_type == 'remove':
        args = data['args']
        result = tk.remove(args['id'])
        new_tk = tk.get_all()  # 重新获取最新的题库数据
        return jsonify({'tiku': new_tk})
    if op_type == 'query':
        args = data['args']
        keyword = args['keyword']

        result = tk.query(args['keyword'])
        return jsonify({'result': result})
    if op_type == 'all':
        all_tk = tk.get_all()
        return jsonify({'tiku': all_tk})


@app.route('/ztlx', methods=['POST'])
def ztlx():
    """专题练习
    """
    data = request.values
    timu_type = data['timu_type']
    timu_num = int(data['timu_num'])
    result = dbo.get_questions(timu_type, timu_num)
    return jsonify({'timu': result})


@app.route('/test', methods=['GET', 'POST'])
def test():
    """测试用函数
    """
    data = request.json
    cal = Calc()
    result = cal.calc_score(data)
    print(result)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
