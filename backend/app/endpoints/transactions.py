from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.transactions import ImportResult, StoreListResponse
from app.services.parsers import parse_cnab
from app.services.transactions import save_transactions, get_stores_with_balance

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/upload", response_model=ImportResult)
async def upload_cnab(
    file: UploadFile = File(..., description="Arquivo CNAB (.txt)"),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=422,
            detail="Apenas arquivos .txt são aceitos",
        )

    content_bytes = await file.read()

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    parsed_lines, errors = parse_cnab(content)

    if not parsed_lines and errors:
        raise HTTPException(
            status_code=422,
            detail=f"Nenhuma linha válida encontrada. Erros: {[str(e) for e in errors[:5]]}",
        )

    user_id = int(payload["sub"])
    saved = await save_transactions(db, parsed_lines, user_id)

    return ImportResult(
        imported=saved,
        errors=len(errors),
        message=f"{saved} transações importadas com sucesso."
        + (f" {len(errors)} linha(s) ignorada(s) por erro." if errors else ""),
    )


@router.get("/stores", response_model=StoreListResponse)
async def list_stores(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = int(payload["sub"])
    stores = await get_stores_with_balance(db, user_id)
    return StoreListResponse(stores=stores, total_stores=len(stores))
