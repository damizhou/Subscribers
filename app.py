from flask import Flask
from login.routes import login_bp
from user_list.routes import user_list_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 用于闪现消息

app.register_blueprint(login_bp)
app.register_blueprint(user_list_bp)

if __name__ == '__main__':
    app.run(debug=True)
