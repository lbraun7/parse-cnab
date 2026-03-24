from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, String, Numeric, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transaction_types.id", ondelete="CASCADE"), nullable=False
    )

    transaction_type: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False)
    card: Mapped[str] = mapped_column(String(12), nullable=False)
    store_owner: Mapped[str] = mapped_column(String(14), nullable=False)
    store_name: Mapped[str] = mapped_column(String(19), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    transaction_type: Mapped["TransactionType"] = relationship("TransactionType", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_store_name", "store_name"),
        Index("ix_transactions_user_id_store", "user_id", "store_name"),
    )

class TransactionType(Base):
    __tablename__ = "transaction_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(50), nullable=False)
    nature: Mapped[str] = mapped_column(String(7), nullable=False)
    sign: Mapped[int] = mapped_column(Integer, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="transaction_type", cascade="all, delete-orphan"
    )