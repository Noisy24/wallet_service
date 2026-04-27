from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Wallet(BaseModel):
    id: UUID
    balance: Decimal = Field(ge=0)


class TransactionType(StrEnum):
    deposit = "deposit"
    withdraw = "withdraw"


class Transaction(BaseModel):
    id: UUID
    wallet_id: UUID
    type: TransactionType
    amount: Decimal = Field(gt=0)
    balance_after: Decimal = Field(ge=0)


class MoneyOperation(BaseModel):
    amount: Decimal = Field(gt=0)
