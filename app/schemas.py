from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


BalanceAmount = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]
PositiveMoneyAmount = Annotated[
    Decimal,
    Field(gt=0, max_digits=18, decimal_places=2),
]


class WalletStatus(StrEnum):
    active = "active"
    blocked = "blocked"
    closed = "closed"


class Wallet(BaseModel):
    id: UUID
    balance: BalanceAmount
    status: WalletStatus


class TransactionType(StrEnum):
    deposit = "deposit"
    withdraw = "withdraw"


class Transaction(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount: PositiveMoneyAmount
    balance_after: BalanceAmount
    created_at: datetime


class MoneyOperation(BaseModel):
    amount: PositiveMoneyAmount


class WalletStatusUpdate(BaseModel):
    status: WalletStatus
