from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid # Import the uuid module

# from . import models, schemas, database
import models
import schemas
import database

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="계층 구조 레코드 복사 API",
    description="FastAPI와 MySQL을 이용한 RESTful API 서버"
)

# --- Hello World 엔드포인트 ---
@app.get("/hello", summary="Hello World")
async def read_hello():
    return {"message": "world"}

# --- 기본 CRUD 엔드포인트 (테스트용) ---

@app.post("/categories/", response_model=schemas.Category, summary="새 카테고리 생성")
def create_category(category: schemas.CategoryCreate, db: Session = Depends(database.get_db)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[schemas.Category], summary="모든 카테고리 조회")
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=schemas.Category, summary="특정 카테고리 조회")
def read_category(category_id: int, db: Session = Depends(database.get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


# --- ⭐️ 레코드 복사 엔드포인트 ---

@app.post("/categories/{source_category_id}/copy", response_model=schemas.Category, summary="카테고리 레코드 복사")
def copy_category(source_category_id: int, db: Session = Depends(database.get_db)):
    """
    지정된 ID의 카테고리 레코드를 복사하여 새로운 레코드를 생성합니다.
    - **source_category_id**: 복사할 원본 카테고리의 ID
    - 복사된 카테고리는 원본과 동일한 `parent_id`를 가집니다.
    - 이름은 "Copy of [원본 이름]" 형식으로 생성됩니다.
    """
    # 1. 원본 레코드 조회
    original_category = db.query(models.Category).filter(models.Category.id == source_category_id).first()
    
    if not original_category:
        raise HTTPException(status_code=404, detail="Source category not found")

    # 2. 복사할 새로운 데이터 생성
    new_category_data = {
        "name": f"Copy of {original_category.name}",
        "description": original_category.description,
        "parent_id": original_category.parent_id  # 원본과 동일한 부모를 가짐
    }

    # 3. 새로운 레코드 객체 생성 및 DB에 추가
    copied_category = models.Category(**new_category_data)
    db.add(copied_category)
    db.commit()
    db.refresh(copied_category) # DB에 저장된 후의 ID, 생성일자 등 최신 정보 반영

    return copied_category


# =============================================
#  교재 및 모든 하위 데이터 복사 API
# =============================================
@app.post("/books/{source_book_id}/copy", response_model=schemas.Book, summary="교재 및 모든 하위 데이터 복사")
def copy_book_and_dependents(source_book_id: int, db: Session = Depends(database.get_db)):
    """
    지정한 교재(Book)와 그에 속한 모든 하위 데이터(챕터, 유닛, 단어 등)를 
    새로운 레코드로 복사합니다.
    - **source_book_id**: 복사할 원본 교재의 ID
    """
    try:
        # 1. 원본 교재 조회
        original_book = db.query(models.Book).filter(models.Book.idx == source_book_id).first()
        if not original_book:
            raise HTTPException(status_code=404, detail="Original book not found")

        # 2. 교재(Book) 레코드 복사
        new_book = models.Book(
            book_title=f"{original_book.book_title} (개정)",
            book_isbn=original_book.book_isbn,
            book_imagelink=original_book.book_imagelink,
            cate_lvl1_idx=original_book.cate_lvl1_idx,
            cate_lvl2_idx=original_book.cate_lvl2_idx,
            created_by=original_book.created_by  # 필요시 현재 사용자 ID로 변경
        )
        db.add(new_book)
        db.flush()  # DB에 임시 저장하여 새 book의 idx를 할당받음
        print("new_book created")

        # --- 매핑용 딕셔너리 ---
        old_to_new_chapter_map = {}
        old_to_new_unit_map = {}
        old_to_new_voca_map = {}
        old_to_new_meaning_map = {}

        # 3. 챕터(Chapters) 복사
        for ch in original_book.chapters:
            new_chapter = models.Chapter(ch_title=ch.ch_title, ch_order=ch.ch_order, book_idx=new_book.idx, created_by=ch.created_by)
            db.add(new_chapter)
            db.flush()
            old_to_new_chapter_map[ch.idx] = new_chapter.idx
        print("chapters copied")
        # 4. 유닛(Units) 복사
        for un in original_book.units:
            new_unit = models.Unit(un_title=un.un_title, un_order=un.un_order, book_idx=new_book.idx, created_by=un.created_by)
            db.add(new_unit)
            db.flush()
            old_to_new_unit_map[un.idx] = new_unit.idx
        print("units")
        # 5. 챕터-유닛 매핑(Chapter-Unit Mappings) 복사
        original_chapters_ids = old_to_new_chapter_map.keys()
        if original_chapters_ids:
            mappings = db.query(models.ChapterUnitMapping).filter(models.ChapterUnitMapping.ch_idx.in_(original_chapters_ids)).all()
            for m in mappings:
                new_ch_idx = old_to_new_chapter_map.get(m.ch_idx)
                new_un_idx = old_to_new_unit_map.get(m.un_idx)
                if new_ch_idx and new_un_idx:
                    db.add(models.ChapterUnitMapping(ch_idx=new_ch_idx, un_idx=new_un_idx, created_by=m.created_by))

        print("mappings")
        # 6. 단어(Voca) 및 하위 데이터 복사
        for i, voca in enumerate(original_book.vocas):
            print(f"voca {i+1}") # 일련번호 추가
            new_un_idx = old_to_new_unit_map.get(voca.un_idx)
            if not new_un_idx: continue # 매핑되는 유닛이 없으면 건너뜀

            new_voca = models.Voca(
                vc_word=voca.vc_word, vt_idx=voca.vt_idx, vc_type=voca.vc_type, vc_root=voca.vc_root,
                vc_unikey=voca.vc_unikey,
                un_idx=new_un_idx, book_idx=new_book.idx, vc_order=voca.vc_order,
                created_by=voca.created_by
            )
            db.add(new_voca)
            db.flush()
            old_to_new_voca_map[voca.idx] = new_voca.idx

            # 6-1. 파생어(Derivatives) 복사
            for dr in voca.derivatives:
                db.add(models.VocaDr(dr_word=dr.dr_word, dr_meaning=dr.dr_meaning, voca_idx=new_voca.idx, created_by=dr.created_by))
            
            # 6-2. 단어 뜻(Meanings) 및 하위 데이터 복사
            for meaning in voca.meanings:
                print("meaning")
                new_meaning = models.VocaMeaning(
                    mi_meaning=meaning.mi_meaning, mi_engmeaning=meaning.mi_engmeaning,
                    mi_order=meaning.mi_order, voca_idx=new_voca.idx, created_by=meaning.created_by
                )
                db.add(new_meaning)
                db.flush()
                old_to_new_meaning_map[meaning.idx] = new_meaning.idx

                # 6-2-1. 예문(Examples) 복사
                for ex in meaning.examples:
                    db.add(models.MeaningExample(
                        ex_sentence=ex.ex_sentence, ex_translation=ex.ex_translation,
                        meaning_idx=new_meaning.idx, voca_idx=new_voca.idx, created_by=ex.created_by
                    ))

                # 6-2-2. 유의어/반의어(Synonyms/Antonyms) 복사
                for sa in meaning.snyants:
                    db.add(models.MeaningSnyant(
                        snyant_type=sa.snyant_type, snyant_word=sa.snyant_word, snyant_meaning=sa.snyant_meaning,
                        meaning_idx=new_meaning.idx, voca_idx=new_voca.idx, created_by=sa.created_by
                    ))
        
        # 7. 모든 변경사항을 DB에 최종 커밋
        db.commit()
        
        # 8. 생성된 새 교재 정보를 반환
        db.refresh(new_book)
        return new_book

    except Exception as e:
        # 오류 발생 시 모든 작업을 롤백하여 데이터 일관성 유지
        db.rollback()
        # 서버 로그에 에러 기록 (디버깅용)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")