import os
import aiofiles
from typing import Annotated, List, LiteralString
from fastapi import Query, HTTPException, UploadFile, File, APIRouter
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from sqlalchemy.future import select
from application.schemas import DocumentPydantic
from database.models import Document, DocumentText
from application.tasks import analyse_document
from database.sessions import SessionDep

"""Создание директории для хранения файла"""

upload_dir = "./documents"
os.makedirs(upload_dir, exist_ok=True)


"""Создание пути для endpoints"""
router = APIRouter(prefix="/documents")


"""Endpoint стартовой страницы"""

@router.get("/", tags=["Start"])
def start_page() -> str:
    greeting_message: Annotated[str, Query()] = "Welcome to app: fastapi_practice"
    return greeting_message


"""Endpoint на чтение документа"""

async def get_one_doc(session: SessionDep, doc_id: int) -> DocumentPydantic:
    """Запрос на получение документа из БД по ID"""
    response = await session.execute(select(Document).where(Document.id == doc_id))
    doc = response.scalar_one_or_none()
    return doc

@router.get("/read/{doc_id}", tags=["Read data"], response_model=DocumentPydantic)
async def get_docs_items(doc_id: int, session: SessionDep) -> DocumentPydantic:
    some_doc = await get_one_doc(session, doc_id)
    if some_doc is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return DocumentPydantic(id=some_doc.id, path=some_doc.path, date=some_doc.date)


"""Endpoint на чтение всех документов"""

async def get_all_docs(session: SessionDep) -> List[DocumentPydantic]:
    """Получение всех документов из БД"""
    all_docs = await session.execute(select(Document))
    docs = all_docs.scalars().all()
    return docs

@router.get("/all_docs/read", tags=["Read data"], response_model=List[DocumentPydantic])
async def get_docs_items(session: SessionDep) -> List[DocumentPydantic]:
    all_docs = await get_all_docs(session)
    return all_docs


"""Endpoint на удаление документа"""

async def get_doc_for_delete(doc_id: int, session: SessionDep) -> tuple:
    """Нахождение документа подлежащего удалению"""
    result_doc = await session.execute(select(Document).filter(Document.id == doc_id))
    result_doc_text = await session.execute(select(DocumentText).filter(DocumentText.id_doc == doc_id))
    doc = result_doc.scalar_one_or_none()
    doc_text = result_doc_text.scalar_one_or_none()
    return doc, doc_text

def delete_doc_not_found(doc_delete_for_del):
    """Проверка наличия документа для удаления"""
    if doc_delete_for_del is None:
        raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/delete/{doc_id}", tags=["Delete data"])
async def delete_doc(doc_id: int, session: SessionDep) -> JSONResponse:
    doc_delete, doc_text_delete = await get_doc_for_delete(doc_id, session)
    delete_doc_not_found(doc_delete)
    if doc_text_delete:
        await session.delete(doc_text_delete)
    await session.delete(doc_delete)
    await session.commit()

    return JSONResponse(content={"Message": "Document deleted"}, status_code=200)


"""Endpoint записи картинки в БД и сохранении в директории documents"""

def validate_file(file: UploadFile):
    """Валидация формата файла"""
    correct_formats = ["image/png", "image/jpeg", "image/gif"]
    if file.content_type not in correct_formats:
        raise HTTPException(status_code=400, detail="Incorrect file format")

def get_unique_filename(file: UploadFile) -> str:
    """Присвоение файлу уникального имени"""
    file_format = file.filename.split(".")[-1]
    return f"{uuid4()}.{file_format}"

async def save_document_to_db(session: AsyncSession, file_name: str) -> int:
    """Сохранение файла в БД"""
    new_doc = Document(path=file_name)
    session.add(new_doc)
    await session.commit()
    return new_doc.id

async def save_document_to_disk(file: UploadFile, file_path: str):
    """Сохранение файла на диск"""
    try:
        async with aiofiles.open(file_path, "wb") as buf:
            await buf.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save to disk not completed {str(e)}")

@router.post("/upload_doc", tags=["Upload document"])
async def upload_doc(session: SessionDep, file: UploadFile=File(...)) -> JSONResponse:
    validate_file(file)
    file_name = get_unique_filename(file)
    file_path = os.path.join(upload_dir, file_name)
    document_id = await save_document_to_db(session, file_name)
    await save_document_to_disk(file, file_path)
    return JSONResponse({"id": document_id,"name": file_name,"message": "Document uploaded successfully"})


"""Endpoint анализа загружаемого документа"""

async def get_document(session: AsyncSession, doc_id: int):
    """Получение документа из БД document"""
    res_search_db_doc = await session.execute(select(Document).where(Document.id == doc_id))
    return res_search_db_doc.scalar_one_or_none()

def check_file_in_disk(file_path: LiteralString | str | bytes):
    """Проверка наличия файла"""
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Document not found")

@router.post("/doc_analyse/{doc_id}", tags=["Analyse document"])
async def doc_analyse(doc_id: int, session: SessionDep) -> JSONResponse:
    document = await get_document(session, doc_id)
    image_path = os.path.join(upload_dir, document.path) #Ожидает получить другие форматы строки
    check_file_in_disk(image_path)
    task = analyse_document.delay(doc_id, image_path)
    return JSONResponse({"task_id": task.id, "status": "Processing"})


"""Endpoint на получение текста по id документа"""

async def get_document_text(session: AsyncSession, document_id: int):
    """Получение документа из БД document_text"""
    res_search_db_doc_text = await session.execute(select(DocumentText).where(DocumentText.id_doc == document_id))
    return res_search_db_doc_text.scalars().first()

def text_not_found(document_text):
    """Обработка исключения при пустом результате ответа"""
    if document_text is None:
        raise HTTPException(status_code=404, detail="Text not found for id")

@router.get("/read_doc_text/{document_id}", tags=["Read data"])
async def get_text(document_id: int, session: SessionDep) -> JSONResponse:
    document_text = await get_document_text(session, document_id)
    text_not_found(document_text)
    return JSONResponse({"document_id": document_id, "text": document_text.text})
