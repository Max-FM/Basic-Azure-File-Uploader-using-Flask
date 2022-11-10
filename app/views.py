import os
from . import db
from .models import File
from flask import (
    Blueprint,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_from_directory
)
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

views = Blueprint("views", __name__)


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    from . import app
    return app.config['UPLOAD_FOLDER']


@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('File not in requests!', category="error")
            return redirect(url_for('views.index'))

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == '':
            flash('No file selected!', category="error")
            return redirect(url_for('views.index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            directory = get_upload_folder()
            filepath = os.path.join(directory, filename)
            file.save(filepath)

            from . import blob_service_client
            blob_client = blob_service_client.get_blob_client(
                container='uploads', blob=filename
            )

            with open(filepath, "rb") as data:
                blob_client.upload_blob(data)

            db.session.add(File(name=filename))
            db.session.commit()

            flash('File uploaded successfully!', category="success")
            return redirect(url_for('views.index'))

    else:
        files = File.query.order_by(
            File.date_created
        ).all()

        return render_template("index.html", files=files)


@views.route('/delete/<int:id>')
def delete_file(id):
    file_to_delete = File.query.get_or_404(id)
    os.remove(os.path.join(get_upload_folder(), file_to_delete.name))
    db.session.delete(file_to_delete)
    db.session.commit()
    flash("File deleted successfully!", category="success")
    return redirect(url_for('views.index'))


@views.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(get_upload_folder(), name)
