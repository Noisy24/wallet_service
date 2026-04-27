from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WalletModel(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    transactions: Mapped[list["TransactionModel"]] = relationship(
        back_populates="wallet",
        cascade="all, delete-orphan",
    )


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wallet_id: Mapped[str] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    wallet: Mapped[WalletModel] = relationship(back_populates="transactions")
