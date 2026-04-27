from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_wallet() -> None:
    response = client.post("/wallets")

    assert response.status_code == 201
    assert response.json()["balance"] == "0.00"
    assert "id" in response.json()


def test_list_wallets() -> None:
    first_wallet = client.post("/wallets").json()
    second_wallet = client.post("/wallets").json()

    response = client.get("/wallets")

    assert response.status_code == 200
    assert response.json() == [first_wallet, second_wallet]


def test_deposit_money() -> None:
    wallet = client.post("/wallets").json()

    response = client.post(
        f"/wallets/{wallet['id']}/deposit",
        json={"amount": "150.50"},
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "150.50"


def test_deposit_rejects_more_than_two_decimal_places() -> None:
    wallet = client.post("/wallets").json()

    response = client.post(
        f"/wallets/{wallet['id']}/deposit",
        json={"amount": "10.999"},
    )

    assert response.status_code == 422


def test_withdraw_money() -> None:
    wallet = client.post("/wallets").json()
    client.post(f"/wallets/{wallet['id']}/deposit", json={"amount": "200"})

    response = client.post(
        f"/wallets/{wallet['id']}/withdraw",
        json={"amount": "35.75"},
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "164.25"


def test_withdraw_rejects_more_than_two_decimal_places() -> None:
    wallet = client.post("/wallets").json()
    client.post(f"/wallets/{wallet['id']}/deposit", json={"amount": "200"})

    response = client.post(
        f"/wallets/{wallet['id']}/withdraw",
        json={"amount": "1.999"},
    )

    assert response.status_code == 422


def test_withdraw_fails_when_balance_is_too_low() -> None:
    wallet = client.post("/wallets").json()

    response = client.post(
        f"/wallets/{wallet['id']}/withdraw",
        json={"amount": "1"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient funds"}


def test_get_transactions() -> None:
    wallet = client.post("/wallets").json()
    client.post(f"/wallets/{wallet['id']}/deposit", json={"amount": "200"})
    client.post(f"/wallets/{wallet['id']}/withdraw", json={"amount": "50"})

    response = client.get(f"/wallets/{wallet['id']}/transactions")

    assert response.status_code == 200
    transactions = response.json()
    assert response.json() == [
        {
            "id": transactions[0]["id"],
            "wallet_id": wallet["id"],
            "type": "deposit",
            "amount": "200.00",
            "balance_after": "200.00",
            "created_at": transactions[0]["created_at"],
        },
        {
            "id": transactions[1]["id"],
            "wallet_id": wallet["id"],
            "type": "withdraw",
            "amount": "50.00",
            "balance_after": "150.00",
            "created_at": transactions[1]["created_at"],
        },
    ]


def test_get_transactions_supports_pagination_and_desc_order() -> None:
    wallet = client.post("/wallets").json()
    client.post(f"/wallets/{wallet['id']}/deposit", json={"amount": "100"})
    client.post(f"/wallets/{wallet['id']}/withdraw", json={"amount": "10"})
    client.post(f"/wallets/{wallet['id']}/deposit", json={"amount": "25"})

    response = client.get(
        f"/wallets/{wallet['id']}/transactions",
        params={"limit": 2, "offset": 1, "order": "desc"},
    )

    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 2
    assert [transaction["type"] for transaction in transactions] == [
        "withdraw",
        "deposit",
    ]


def test_get_transactions_rejects_invalid_pagination() -> None:
    wallet = client.post("/wallets").json()

    response = client.get(
        f"/wallets/{wallet['id']}/transactions",
        params={"limit": 0},
    )

    assert response.status_code == 422
