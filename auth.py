from fastapi import Header, HTTPException
from app.database import is_valid_api_key


async def require_api_key(x_api_key: str = Header(...)):
    if not is_valid_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return x_api_key
