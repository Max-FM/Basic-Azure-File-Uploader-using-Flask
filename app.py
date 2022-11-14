import os
import asyncio
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_file
)
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import ContainerClient
from dotenv import load_dotenv

load_dotenv()

# Configure App
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['AZURE_CONNECTION_STRING'] = os.environ.get(
    'AZURE_CONNECTION_STRING'
)

# Connect to Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=app.config["AZURE_CONNECTION_STRING"]
)


# Create uploads container on Azure
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


asyncio.run(create_azure_uploads_container())


# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('File not in requests!', category="error")
            return redirect(url_for('index'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected!', category="error")
            return redirect(url_for('index'))

        if file:
            blob_client = blob_service_client.get_blob_client(
                container='uploads',
                blob=secure_filename(file.filename)
            )
            blob_client.upload_blob(file)

            flash('File uploaded successfully!', category="success")
            return redirect(url_for('index'))

    else:
        container_client = blob_service_client.get_container_client('uploads')
        blob_list = list(container_client.list_blobs())

        return render_template("index.html", files=blob_list)


@app.route('/delete/<name>')
def delete_file(name):
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=name
    )
    blob_client.delete_blob(delete_snapshots="include")

    flash("File deleted successfully!", category="success")

    return redirect(url_for('index'))


@app.route('/uploads/<name>')
def download_file(name):
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=name
    )

    return send_file(
        blob_client.download_blob(),
        download_name=name,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run()
