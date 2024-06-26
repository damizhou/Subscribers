from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
import logging

user_list_bp = Blueprint('user_list', __name__, template_folder='templates')

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='admin',
        database='openbras'
    )
    return connection

def get_users_from_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                subscriberUsername AS username, 
                subscriberPassword AS password, 
                color,
                subscriberCreated AS added_time, 
                subscriberLastMAC AS mac_address, 
                subscriberLastUpdate AS last_login 
            FROM Subscribers
        ''')
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        for user in users:
            user['type'] = map_color_to_type(user['color'])
        return users
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return []

def get_user_from_db(username):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                subscriberUsername AS username, 
                subscriberPassword AS password, 
                color
            FROM Subscribers
            WHERE subscriberUsername = %s
        ''', (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            user['type'] = map_color_to_type(user['color'])
        return user
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return None

def update_user_in_db(username, password, color):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE Subscribers
            SET subscriberPassword = %s, color = %s
            WHERE subscriberUsername = %s
        ''', (password, color, username))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")

def add_user_to_db(username, password, color):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Subscribers (subscriberUsername, subscriberPassword, color, subscriberLastMAC, subscriberLastUpdate, subscriberCreated)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        ''', (username, password, color, 0))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")

def map_color_to_type(color):
    if color == 2:
        return '优质可信用户'
    elif color == 1:
        return '普通可信用户'
    elif color == 0:
        return '普通用户'
    else:
        return '未知类型'

def map_type_to_color(user_type):
    if user_type == '优质可信用户':
        return 2
    elif user_type == '普通可信用户':
        return 1
    elif user_type == '普通用户':
        return 0
    else:
        return 0

@user_list_bp.route('/user_list')
def user_list():
    users = get_users_from_db()
    return render_template('user_list.html', users=users)

@user_list_bp.route('/edit_user/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']
        if password != confirm_password:
            flash('密码和确认密码不一致')
        else:
            color = map_type_to_color(user_type)
            update_user_in_db(username, password, color)
            flash('用户信息更新成功')
            return redirect(url_for('user_list.user_list'))
    user = get_user_from_db(username)
    if user:
        return render_template('edit_user.html', user=user)
    else:
        flash('用户不存在')
        return redirect(url_for('user_list.user_list'))

@user_list_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']
        if password != confirm_password:
            flash('密码和确认密码不一致')
        else:
            color = map_type_to_color(user_type)
            add_user_to_db(username, password, color)
            flash('用户添加成功')
            return redirect(url_for('user_list.user_list'))
    return render_template('add_user.html')
