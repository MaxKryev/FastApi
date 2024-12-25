import pytesseract
from celery import Celery
from database.config import session
from database.models import DocumentText
from PIL import Image


"""Создание фоновой задачи"""

app_celery = Celery("tasks", broker="pyamqp://maxkry:asdf456@rabbit:5672//")

def analyse_document_async(doc_id: int, image_path: str):
    text = pytesseract.image_to_string(Image.open(image_path))

    with session() as sess:
        doc_text = DocumentText(id_doc=doc_id, text=text)
        sess.add(doc_text)
        sess.commit()

    return text

@app_celery.task
def analyse_document(doc_id: int, image_path: str):
    result_text = analyse_document_async(doc_id, image_path)
    return result_text
