from flask import Blueprint, render_template, request, redirect, url_for, flash

login_bp = Blueprint('login', __name__, template_folder='templates')

@login_bp.route('/')
def home():
    return redirect(url_for('login.login'))

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'www.163.com':
            flash('登录成功')
            return redirect(url_for('user_list.user_list'))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login.login'))
    return render_template('login.html')
