import logging
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TransactionModel, WalletModel
from app.schemas import Transaction, TransactionType, Wallet


logger = logging.getLogger(__name__)


class WalletNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def create_wallet(db: Session) -> Wallet:
    wallet_model = WalletModel(id=str(uuid4()), balance=Decimal("0"))
    db.add(wallet_model)
    db.commit()
    db.refresh(wallet_model)

    logger.info("wallet created wallet_id=%s", wallet_model.id)
    return _wallet_to_schema(wallet_model)


def list_wallets(db: Session) -> list[Wallet]:
    wallet_models = db.scalars(select(WalletModel)).all()
    return [_wallet_to_schema(wallet_model) for wallet_model in wallet_models]


def get_wallet(db: Session, wallet_id: UUID) -> Wallet:
    wallet_model = _get_wallet_model(db, wallet_id)
    return _wallet_to_schema(wallet_model)


def deposit(db: Session, wallet_id: UUID, amount: Decimal) -> Wallet:
    wallet_model = _get_wallet_model(db, wallet_id)
    wallet_model.balance += amount
    _add_transaction(db, wallet_model, TransactionType.deposit, amount)
    db.commit()
    db.refresh(wallet_model)

    logger.info(
        "wallet deposit wallet_id=%s amount=%s balance_after=%s",
        wallet_model.id,
        amount,
        wallet_model.balance,
    )
    return _wallet_to_schema(wallet_model)


def withdraw(db: Session, wallet_id: UUID, amount: Decimal) -> Wallet:
    wallet_model = _get_wallet_model(db, wallet_id)
    if wallet_model.balance < amount:
        logger.warning(
            "wallet withdraw rejected wallet_id=%s amount=%s balance=%s",
            wallet_model.id,
            amount,
            wallet_model.balance,
        )
        raise InsufficientFundsError

    wallet_model.balance -= amount
    _add_transaction(db, wallet_model, TransactionType.withdraw, amount)
    db.commit()
    db.refresh(wallet_model)

    logger.info(
        "wallet withdraw wallet_id=%s amount=%s balance_after=%s",
        wallet_model.id,
        amount,
        wallet_model.balance,
    )
    return _wallet_to_schema(wallet_model)


def get_transactions(db: Session, wallet_id: UUID) -> list[Transaction]:
    _get_wallet_model(db, wallet_id)
    transaction_models = db.scalars(
        select(TransactionModel).where(TransactionModel.wallet_id == str(wallet_id))
    ).all()
    return [
        _transaction_to_schema(transaction_model)
        for transaction_model in transaction_models
    ]


def _get_wallet_model(db: Session, wallet_id: UUID) -> WalletModel:
    wallet_model = db.get(WalletModel, str(wallet_id))
    if wallet_model is None:
        raise WalletNotFoundError
    return wallet_model


def _add_transaction(
    db: Session,
    wallet: WalletModel,
    transaction_type: TransactionType,
    amount: Decimal,
) -> None:
    db.add(
        TransactionModel(
            id=str(uuid4()),
            wallet_id=wallet.id,
            type=transaction_type.value,
            amount=amount,
            balance_after=wallet.balance,
        )
    )


def _wallet_to_schema(wallet: WalletModel) -> Wallet:
    return Wallet(id=UUID(wallet.id), balance=wallet.balance)


def _transaction_to_schema(transaction: TransactionModel) -> Transaction:
    return Transaction(
        id=UUID(transaction.id),
        wallet_id=UUID(transaction.wallet_id),
        type=TransactionType(transaction.type),
        amount=transaction.amount,
        balance_after=transaction.balance_after,
    )
