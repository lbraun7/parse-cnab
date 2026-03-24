import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User

VALID_LINE   = "3201903010000014200096206760174753830274CP154702JOSE COSTA    MERCADO DA AVENIDA "
LINE_STORE_A = "3201903010000014200096206760174753830274CP154702JOSE COSTA    MERCADO DA AVENIDA "
LINE_STORE_B = "1201903010000015200096206760174753830274CP154702MARIA SILVA   LOJA DO O          "
LINE_ENTRADA = "1201903010000010000096206760174753830274CP154702DONO DA LOJA  LOJA TESTE         "
LINE_SAIDA   = "2201903010000005000096206760174753830274CP154702DONO DA LOJA  LOJA TESTE         "


async def create_test_user(db: AsyncSession) -> User:
    user = User(id=1, email="test@example.com", name="Test User")
    db.add(user)
    await db.flush()
    return user


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient):
    resp = await client.post("/api/v1/transactions/upload")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_cnab_success(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
):
    await create_test_user(db_session)

    content = (VALID_LINE + "\n") * 3
    resp = await client.post(
        "/api/v1/transactions/upload",
        files={"file": ("CNAB.txt", content.encode(), "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 3
    assert data["errors"] == 0


@pytest.mark.asyncio
async def test_upload_rejects_non_txt(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
):
    await create_test_user(db_session)

    resp = await client.post(
        "/api/v1/transactions/upload",
        files={"file": ("CNAB.csv", b"bad content", "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_stores_empty(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
):
    await create_test_user(db_session)

    resp = await client.get("/api/v1/transactions/stores", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stores"] == []
    assert data["total_stores"] == 0


@pytest.mark.asyncio
async def test_list_stores_after_upload(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
):
    await create_test_user(db_session)

    content = LINE_STORE_A + "\n" + LINE_STORE_B + "\n"
    await client.post(
        "/api/v1/transactions/upload",
        files={"file": ("CNAB.txt", content.encode(), "text/plain")},
        headers=auth_headers,
    )

    resp = await client.get("/api/v1/transactions/stores", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_stores"] == 2


@pytest.mark.asyncio
async def test_stores_balance_calculation(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
):
    await create_test_user(db_session)

    content = LINE_ENTRADA + "\n" + LINE_SAIDA + "\n"
    await client.post(
        "/api/v1/transactions/upload",
        files={"file": ("CNAB.txt", content.encode(), "text/plain")},
        headers=auth_headers,
    )

    resp = await client.get("/api/v1/transactions/stores", headers=auth_headers)
    stores = resp.json()["stores"]
    assert len(stores) == 1
    assert float(stores[0]["balance"]) == pytest.approx(50.00)
