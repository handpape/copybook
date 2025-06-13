# schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# =============================================
#  Pydantic Model Configuration
# =============================================
# Pydantic V2 이상에서는 from_attributes=True
# 이전 버전에서는 orm_mode = True
class BaseConfig(BaseModel):
    class Config:
        from_attributes = True


# =============================================
#  pt_category
# =============================================
class CategoryBase(BaseModel):
    cate_name: str
    cate_lvl: int
    cate_pidx: Optional[int] = None
    created_by: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    idx: int
    created_at: Optional[datetime] = None
    
    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_voca_type
# =============================================
class VocaTypeBase(BaseModel):
    vt_title: str
    created_by: Optional[int] = None

class VocaTypeCreate(VocaTypeBase):
    pass

class VocaType(VocaTypeBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_book
# =============================================
class BookBase(BaseModel):
    book_title: str
    book_isbn: Optional[str] = None
    book_imagelink: Optional[str] = None
    cate_lvl1_idx: Optional[int] = None
    cate_lvl2_idx: Optional[int] = None
    created_by: Optional[int] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_chapter
# =============================================
class ChapterBase(BaseModel):
    ch_title: str
    ch_order: int
    book_idx: int
    created_by: Optional[int] = None

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_unit
# =============================================
class UnitBase(BaseModel):
    un_title: str
    un_order: int
    book_idx: int
    created_by: Optional[int] = None

class UnitCreate(UnitBase):
    pass

class Unit(UnitBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_voca
# =============================================
class VocaBase(BaseModel):
    vc_word: str
    vt_idx: int
    vc_type: int
    vc_root: Optional[str] = None
    vc_unikey: Optional[str] = None
    vc_mp3_link: Optional[str] = None
    vc_order: int
    un_idx: int
    book_idx: int
    created_by: Optional[int] = None

class VocaCreate(VocaBase):
    pass

class Voca(VocaBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_voca_dr (Derivative)
# =============================================
class VocaDrBase(BaseModel):
    dr_word: str
    dr_meaning: str
    voca_idx: int
    created_by: Optional[int] = None

class VocaDrCreate(VocaDrBase):
    pass

class VocaDr(VocaDrBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_voca_meaning
# =============================================
class VocaMeaningBase(BaseModel):
    mi_meaning: str
    mi_engmeaning: Optional[str] = None
    mi_order: int
    voca_idx: int
    created_by: Optional[int] = None

class VocaMeaningCreate(VocaMeaningBase):
    pass

class VocaMeaning(VocaMeaningBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_ch_un_mapping (Chapter-Unit Mapping)
# =============================================
class ChapterUnitMappingBase(BaseModel):
    ch_idx: int
    un_idx: int
    created_by: Optional[int] = None

class ChapterUnitMappingCreate(ChapterUnitMappingBase):
    pass

class ChapterUnitMapping(ChapterUnitMappingBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_meaning_example
# =============================================
class MeaningExampleBase(BaseModel):
    ex_sentence: str
    ex_translation: str
    meaning_idx: int
    voca_idx: int
    created_by: Optional[int] = None

class MeaningExampleCreate(MeaningExampleBase):
    pass

class MeaningExample(MeaningExampleBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass

# =============================================
#  pt_meaning_snyant (Synonym/Antonym)
# =============================================
class MeaningSnyantBase(BaseModel):
    snyant_type: int
    snyant_word: str
    meaning_idx: int
    voca_idx: int
    created_by: Optional[int] = None
    snyant_meaning: str

class MeaningSnyantCreate(MeaningSnyantBase):
    pass

class MeaningSnyant(MeaningSnyantBase):
    idx: int
    created_at: Optional[datetime] = None

    class Config(BaseConfig.Config):
        pass
