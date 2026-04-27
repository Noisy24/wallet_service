from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import services
from app.schemas import MoneyOperation, Transaction, Wallet


router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("", response_model=Wallet, status_code=status.HTTP_201_CREATED)
async def create_wallet(db: Session = Depends(get_db)) -> Wallet:
    return services.create_wallet(db)


@router.get("", response_model=list[Wallet])
async def list_wallets(db: Session = Depends(get_db)) -> list[Wallet]:
    return services.list_wallets(db)


@router.get("/{wallet_id}", response_model=Wallet)
async def get_wallet(wallet_id: UUID, db: Session = Depends(get_db)) -> Wallet:
    try:
        return services.get_wallet(db, wallet_id)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )


@router.post("/{wallet_id}/deposit", response_model=Wallet)
async def deposit(
    wallet_id: UUID,
    operation: MoneyOperation,
    db: Session = Depends(get_db),
) -> Wallet:
    try:
        return services.deposit(db, wallet_id, operation.amount)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )


@router.post("/{wallet_id}/withdraw", response_model=Wallet)
async def withdraw(
    wallet_id: UUID,
    operation: MoneyOperation,
    db: Session = Depends(get_db),
) -> Wallet:
    try:
        return services.withdraw(db, wallet_id, operation.amount)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    except services.InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )


@router.get("/{wallet_id}/transactions", response_model=list[Transaction])
async def get_transactions(
    wallet_id: UUID,
    db: Session = Depends(get_db),
) -> list[Transaction]:
    try:
        return services.get_transactions(db, wallet_id)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
