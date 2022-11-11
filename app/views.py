from flask import (
    Blueprint,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_file
)
from werkzeug.utils import secure_filename

views = Blueprint("views", __name__)


@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('File not in requests!', category="error")
            return redirect(url_for('views.index'))

        file = request.files['file']

        if file.filename == '':
            flash('No file selected!', category="error")
            return redirect(url_for('views.index'))

        if file:
            from . import blob_service_client
            blob_client = blob_service_client.get_blob_client(
                container='uploads',
                blob=secure_filename(file.filename)
            )
            blob_client.upload_blob(file)

            flash('File uploaded successfully!', category="success")
            return redirect(url_for('views.index'))

    else:
        from . import blob_service_client
        container_client = blob_service_client.get_container_client('uploads')
        blob_list = list(container_client.list_blobs())

        return render_template("index.html", files=blob_list)


@views.route('/delete/<name>')
def delete_file(name):
    from . import blob_service_client
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=name
    )
    blob_client.delete_blob(delete_snapshots="include")

    flash("File deleted successfully!", category="success")

    return redirect(url_for('views.index'))


@views.route('/uploads/<name>')
def download_file(name):
    from . import blob_service_client
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=name
    )

    return send_file(
        blob_client.download_blob(),
        download_name=name,
        as_attachment=True
    )
