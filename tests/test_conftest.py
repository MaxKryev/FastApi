from sqlalchemy import select
import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from httpx import AsyncClient, ASGITransport
from database.models import Base, Document, DocumentText
from database.config import async_engine, async_session
from application.endpoints import upload_dir
from application.main import app
import asyncio
import os
import shutil
from uuid import uuid4

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def temp_documents_dir():
    original_documents_dir = upload_dir

    temp_dir = f"/tmp/test_documents_{uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    app.dependency_overrides[upload_dir] = lambda: temp_dir

    yield temp_dir

    app.dependency_overrides[upload_dir] = lambda: original_documents_dir
    shutil.rmtree(temp_dir)

@pytest_asyncio.fixture(scope='module')
async def test_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_session
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

"""Тест на удаление"""
@pytest.mark.asyncio
async def test_doc_delete(test_db):
    async with async_session() as session:
        test_document = Document(path='test_document.txt')
        session.add(test_document)
        await session.flush()
        doc_id = test_document.id

        test_document_text = DocumentText(text='Тестовый текст', id_doc=doc_id)
        session.add(test_document_text)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as client:
        response = await client.delete(f'/documents/delete/{doc_id}')
    assert response.status_code == 200

"""Тест на существование строки в таблице"""
@pytest.mark.asyncio
async def test_doc_get(test_db):
    async with async_session() as session:
        test_document = Document(path='test_document.txt')
        session.add(test_document)
        await session.commit()
        doc_id = test_document.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as client:
        response = await client.get(f'/documents/read/{doc_id}')
    assert response.status_code == 200

"""Тест на существование баз данных"""
@pytest.mark.asyncio
async def test_tables_exist(test_db):
    async with test_db() as session:
        for model in [Document, DocumentText]:
            try:
                await session.execute(select(model).limit(1))
            except SQLAlchemyError:
                pytest.fail(f"Таблица для модели {model.__tablename__} не существует")


@pytest.mark.asyncio
async def test_upload_document_unsupported_file_type(temp_documents_dir):
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        with open(os.path.join(temp_documents_dir, "test_file.txt"), "w") as f:
            f.write("unsupported data")

        with open(os.path.join(temp_documents_dir, "test_file.txt"), "rb") as f:
            response = await client.post(
                "/documents/upload_doc",
                files={"file": ("test_file.txt", f, "text/plain")}
            )

        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect file format"}

"""Тест на существование текста"""
@pytest.mark.asyncio
async def test_get_text(test_db):
    async with async_session() as session:

        document = Document(path="/path/to/document")
        session.add(document)
        await session.commit()

        test_text = DocumentText(id_doc=document.id, text="Some text")
        session.add(test_text)
        await session.commit()

        document_id = test_text.id_doc
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        response = await client.get(f'/documents/read_doc_text/{document_id}')

    assert response.status_code == 200
    assert response.json() == {"document_id": document_id, "text": "Some text"}

