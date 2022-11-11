from . import db
from .models import File
import uuid
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
            filename = secure_filename(file.filename)

            from . import blob_service_client
            blod_id = str(uuid.uuid4())
            blob_client = blob_service_client.get_blob_client(
                container='uploads',
                blob=blod_id
            )
            blob_client.upload_blob(file)

            db.session.add(
                File(
                    filename=filename,
                    blob_id=blod_id
                )
            )
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

    from . import blob_service_client
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=file_to_delete.blob_id
    )
    blob_client.delete_blob(delete_snapshots="include")

    db.session.delete(file_to_delete)
    db.session.commit()
    flash("File deleted successfully!", category="success")

    return redirect(url_for('views.index'))


@views.route('/uploads/<int:id>')
def download_file(id):
    file_to_download = File.query.get_or_404(id)

    from . import blob_service_client
    blob_client = blob_service_client.get_blob_client(
        container='uploads',
        blob=file_to_download.blob_id
    )

    return send_file(
        blob_client.download_blob(),
        download_name=file_to_download.filename,
        as_attachment=True
    )
