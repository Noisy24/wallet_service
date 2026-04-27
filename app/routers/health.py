from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}
