import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
DB_PATH = os.path.join(basedir, 'database.db')
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkeydonttellanyone'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    from .models import File  # noqa: F401

    create_database(app)

    return app


def create_database(app):
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
        print('Database created!')


app = create_app()
