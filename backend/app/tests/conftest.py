import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.transactions import TransactionType

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        types = [
            TransactionType(id=1, description="Débito",                 nature="entrada", sign=1),
            TransactionType(id=2, description="Boleto",                 nature="saida",   sign=-1),
            TransactionType(id=3, description="Financiamento",          nature="saida",   sign=-1),
            TransactionType(id=4, description="Crédito",                nature="entrada", sign=1),
            TransactionType(id=5, description="Recebimento Empréstimo", nature="entrada", sign=1),
            TransactionType(id=6, description="Vendas",                 nature="entrada", sign=1),
            TransactionType(id=7, description="Recebimento TED",        nature="entrada", sign=1),
            TransactionType(id=8, description="Recebimento DOC",        nature="entrada", sign=1),
            TransactionType(id=9, description="Aluguel",                nature="saida",   sign=-1),
        ]
        session.add_all(types)
        await session.commit()
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_token():
    return create_access_token({"sub": "1", "email": "test@example.com"})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
