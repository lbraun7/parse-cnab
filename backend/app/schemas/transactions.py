from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    nature: str
    sign: int


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_type_id: int
    transaction_type: TransactionTypeResponse         
    occurred_at: datetime
    amount: Decimal
    cpf: str
    card: str
    store_owner: str
    store_name: str
    created_at: datetime


class StoreBalance(BaseModel):
    store_name: str
    store_owner: str
    balance: Decimal
    transactions: list[TransactionResponse]


class ImportResult(BaseModel):
    imported: int
    errors: int
    message: str


class StoreListResponse(BaseModel):
    stores: list[StoreBalance]
    total_stores: int
