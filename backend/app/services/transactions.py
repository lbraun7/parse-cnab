from decimal import Decimal
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transactions import Transaction
from app.schemas.transactions import StoreBalance, TransactionResponse
from app.services.parsers import ParsedLine


async def save_transactions(
    db: AsyncSession,
    lines: list[ParsedLine],
    user_id: int,
) -> int:
    objects = [
        Transaction(
            user_id=user_id,
            transaction_type_id=line.transaction_type_id,
            occurred_at=line.occurred_at,
            amount=line.amount,
            cpf=line.cpf,
            card=line.card,
            store_owner=line.store_owner,
            store_name=line.store_name,
        )
        for line in lines
    ]
    db.add_all(objects)
    await db.flush()
    return len(objects)


async def get_stores_with_balance(
    db: AsyncSession,
    user_id: int,
) -> list[StoreBalance]:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .options(selectinload(Transaction.transaction_type))
        .order_by(Transaction.store_name, Transaction.occurred_at)
    )
    transactions = result.scalars().all()

    stores: dict[str, dict] = defaultdict(
        lambda: {"store_owner": "", "transactions": [], "balance": Decimal("0.00")}
    )

    for t in transactions:
        s = stores[t.store_name]
        s["store_owner"] = t.store_owner
        s["transactions"].append(t)
        s["balance"] += t.amount * t.transaction_type.sign

    return [
        StoreBalance(
            store_name=name,
            store_owner=data["store_owner"],
            balance=data["balance"],
            transactions=[TransactionResponse.model_validate(tx) for tx in data["transactions"]],
        )
        for name, data in sorted(stores.items())
    ]
