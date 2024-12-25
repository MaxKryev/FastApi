from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


"""Модели базы данных"""

class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    path: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document_text = relationship("DocumentText", uselist=False, back_populates="document")


class DocumentText(Base):
    __tablename__ = "document_text"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_doc: Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)

    document = relationship("Document", back_populates="document_text")


