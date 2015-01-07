__author__ = 'lolo'


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import basedir


app = Flask(__name__)
app.config.from_object('Viewer.config.ProdConfiguration')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from Viewer import views, models