# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class Category(Base):
    __tablename__ = "pt_category"
    idx = Column(Integer, primary_key=True, index=True)
    cate_name = Column(String(50), nullable=False)
    cate_lvl = Column(Integer, nullable=False)
    cate_pidx = Column(Integer, ForeignKey("pt_category.idx"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    parent = relationship("Category", remote_side=[idx], back_populates="children")
    children = relationship("Category", back_populates="parent")

class VocaType(Base):
    __tablename__ = "pt_voca_type"
    idx = Column(Integer, primary_key=True, index=True)
    vt_title = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)

class Book(Base):
    __tablename__ = "pt_book"
    idx = Column(Integer, primary_key=True, index=True)
    book_title = Column(String(50), nullable=False)
    book_isbn = Column(String(50), nullable=True)
    book_imagelink = Column(String(500), nullable=True)
    cate_lvl1_idx = Column(Integer, ForeignKey("pt_category.idx"), nullable=True)
    cate_lvl2_idx = Column(Integer, ForeignKey("pt_category.idx"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="book", cascade="all, delete-orphan")
    vocas = relationship("Voca", back_populates="book", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "pt_chapter"
    idx = Column(Integer, primary_key=True, index=True)
    ch_title = Column(String(50), nullable=False)
    ch_order = Column(Integer, nullable=False)
    book_idx = Column(Integer, ForeignKey("pt_book.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    book = relationship("Book", back_populates="chapters")
    units_mapping = relationship("ChapterUnitMapping", back_populates="chapter", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = "pt_unit"
    idx = Column(Integer, primary_key=True, index=True)
    un_title = Column(String(50), nullable=False)
    un_order = Column(Integer, nullable=False)
    book_idx = Column(Integer, ForeignKey("pt_book.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)

    book = relationship("Book", back_populates="units")
    chapters_mapping = relationship("ChapterUnitMapping", back_populates="unit", cascade="all, delete-orphan")
    vocas = relationship("Voca", back_populates="unit", cascade="all, delete-orphan")

class ChapterUnitMapping(Base):
    __tablename__ = "pt_ch_un_mapping"
    idx = Column(Integer, primary_key=True, index=True)
    ch_idx = Column(Integer, ForeignKey("pt_chapter.idx"), nullable=False)
    un_idx = Column(Integer, ForeignKey("pt_unit.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)

    chapter = relationship("Chapter", back_populates="units_mapping")
    unit = relationship("Unit", back_populates="chapters_mapping")

class Voca(Base):
    __tablename__ = "pt_voca"
    idx = Column(Integer, primary_key=True, index=True)
    vc_word = Column(String(50), nullable=False)
    vt_idx = Column(Integer, ForeignKey("pt_voca_type.idx"), nullable=False)
    vc_type = Column(Integer, nullable=False)
    vc_root = Column(String(4000), nullable=True)
    vc_unikey = Column(String(4000), nullable=True)
    vc_mp3_link = Column(String(500), nullable=True)
    un_idx = Column(Integer, ForeignKey("pt_unit.idx"), nullable=False)
    book_idx = Column(Integer, ForeignKey("pt_book.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    book = relationship("Book", back_populates="vocas")
    unit = relationship("Unit", back_populates="vocas")
    voca_type = relationship("VocaType")
    derivatives = relationship("VocaDr", back_populates="voca", cascade="all, delete-orphan")
    meanings = relationship("VocaMeaning", back_populates="voca", cascade="all, delete-orphan")

class VocaDr(Base):
    __tablename__ = "pt_voca_dr"
    idx = Column(Integer, primary_key=True, index=True)
    dr_word = Column(String(50), nullable=False)
    dr_meaning = Column(String(50), nullable=False)
    voca_idx = Column(Integer, ForeignKey("pt_voca.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)

    voca = relationship("Voca", back_populates="derivatives")

class VocaMeaning(Base):
    __tablename__ = "pt_voca_meaning"
    idx = Column(Integer, primary_key=True, index=True)
    mi_meaning = Column(String(50), nullable=False)
    mi_engmeaning = Column(String(200), nullable=True)
    mi_order = Column(Integer, nullable=False)
    voca_idx = Column(Integer, ForeignKey("pt_voca.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)

    voca = relationship("Voca", back_populates="meanings")
    examples = relationship("MeaningExample", back_populates="meaning", cascade="all, delete-orphan")
    snyants = relationship("MeaningSnyant", back_populates="meaning", cascade="all, delete-orphan")

class MeaningExample(Base):
    __tablename__ = "pt_meaning_example"
    idx = Column(Integer, primary_key=True, index=True)
    ex_sentence = Column(String(200), nullable=False)
    ex_translation = Column(String(200), nullable=False)
    meaning_idx = Column(Integer, ForeignKey("pt_voca_meaning.idx"), nullable=False)
    voca_idx = Column(Integer, ForeignKey("pt_voca.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    meaning = relationship("VocaMeaning", back_populates="examples")

class MeaningSnyant(Base):
    __tablename__ = "pt_meaning_snyant"
    idx = Column(Integer, primary_key=True, index=True)
    snyant_type = Column(Integer, nullable=False)
    snyant_word = Column(String(50), nullable=False)
    meaning_idx = Column(Integer, ForeignKey("pt_voca_meaning.idx"), nullable=False)
    voca_idx = Column(Integer, ForeignKey("pt_voca.idx"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    
    meaning = relationship("VocaMeaning", back_populates="snyants")
