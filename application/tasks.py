import pytesseract
from celery import Celery
from database.config import async_session
from database.models import DocumentText
from PIL import Image
from asgiref.sync import async_to_sync
import asyncio


"""Создание фоновой задачи"""

app_celery = Celery("tasks", broker="pyamqp://maxkry:asdf456@rabbit:5672//")

async def analyse_document_async(document_id: int, image_path: str):
    text = pytesseract.image_to_string(Image.open(image_path))

    async with async_session() as session:
        doc_text = DocumentText(id_doc=document_id, text=text)
        session.add(doc_text)
        await session.commit()

    return text

@app_celery.task
def analyse_document(document_id: int, image_path: str):
    result_text = async_to_sync(analyse_document_async)(document_id, image_path)
    return result_text

def asy_to_syn(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)
