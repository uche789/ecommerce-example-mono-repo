import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def validate_api_key(api_key_header: str = Security(api_key_header)):
    stored_api_key = os.getenv('X_API_KEY')
    if stored_api_key != api_key_header:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")