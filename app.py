from flask import Flask
from backend.models import db
from flask_login import LoginManager

app = None

def init_app():
    app = Flask(__name__)
    app.secret_key = 'fsfdgdsgs'
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iescp.db'
    db.init_app(app)
    app.app_context().push()
    login_manager = LoginManager()
    login_manager.login_view = 'controller.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    print("app started....")
    return app

app = init_app()

# Import routes after app initialization
from backend.controller import *

if __name__ == '__main__':
    app.run()
