from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import services
from app.schemas import MoneyOperation, Transaction, Wallet, WalletStatusUpdate


router = APIRouter(prefix="/wallets", tags=["wallets"])


def _wallet_inactive_exception(wallet_status: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Wallet is {wallet_status}",
    )


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
    except services.WalletInactiveError as error:
        raise _wallet_inactive_exception(error.wallet_status)


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
    except services.WalletInactiveError as error:
        raise _wallet_inactive_exception(error.wallet_status)
    except services.InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )


@router.patch("/{wallet_id}/status", response_model=Wallet)
async def set_wallet_status(
    wallet_id: UUID,
    status_update: WalletStatusUpdate,
    db: Session = Depends(get_db),
) -> Wallet:
    try:
        return services.set_wallet_status(db, wallet_id, status_update.status)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )


@router.get("/{wallet_id}/transactions", response_model=list[Transaction])
async def get_transactions(
    wallet_id: UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
) -> list[Transaction]:
    try:
        return services.get_transactions(db, wallet_id, limit, offset, order)
    except services.WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
