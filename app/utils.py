# payments/utils.py
import io
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict=None):
    context_dict = context_dict or {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


# compressing in memory 
# utils.py
import io
import zipfile
from django.core.files.base import ContentFile

def compress_file_to_zip_in_memory(uploaded_file):
    """
    uploaded_file: an UploadedFile / InMemoryUploadedFile / TemporaryUploadedFile
    Returns: (ContentFile(zip_bytes), compressed_size_bytes)
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        uploaded_file.seek(0)
        data = uploaded_file.read()
        zf.writestr(uploaded_file.name, data)
    buf.seek(0)
    zipped_bytes = buf.getvalue()
    zipped_name = f"{uploaded_file.name}.zip"
    return ContentFile(zipped_bytes, name=zipped_name), len(zipped_bytes)


# compressing in disk 
# utils.py (continuation)
import tempfile
import os
from django.core.files import File

def compress_file_to_zip_on_disk(uploaded_file):
    """
    For large files: write upload to a temp file, zip it to a temp zip, return an open file and paths to cleanup.
    Returns: (django File object, temp_input_path, temp_zip_path)
    """
    # save upload to a temp input file
    temp_in = tempfile.NamedTemporaryFile(delete=False)
    try:
        for chunk in uploaded_file.chunks():
            temp_in.write(chunk)
        temp_in.flush()
        temp_in.close()

        temp_zip_path = tempfile.mktemp(suffix='.zip')
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # arcname is the original filename inside the zip
            zf.write(temp_in.name, arcname=uploaded_file.name)

        f = open(temp_zip_path, 'rb')
        return File(f), temp_in.name, temp_zip_path
    except:
        # cleanup on error
        try:
            os.remove(temp_in.name)
        except:
            pass
        raise
