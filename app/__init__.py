import os
import asyncio
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import ContainerClient
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
DB_PATH = os.path.join(basedir, 'database.db')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING')
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.Config")
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


async def create_azure_uploads_container():
    try:
        container_name = "uploads"
        container_client = ContainerClient.from_connection_string(
            conn_str=app.config["AZURE_CONNECTION_STRING"],
            container_name=container_name
        )

        await container_client.create_container()

    except Exception as ex:
        print('Exception:')
        print(ex)


app = create_app()
blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=app.config["AZURE_CONNECTION_STRING"]
)

asyncio.run(create_azure_uploads_container())
