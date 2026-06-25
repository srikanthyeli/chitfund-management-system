from pydantic import BaseModel
from typing import Optional

class DatabaseSettings(BaseModel):
    db_url: str

class AppSettings(BaseModel):
    env: str = "local"
    debug: bool = True
    secret_key: str = "change_me"
    token_expire_minutes: int = 60

class JwtSettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expiry: int = 60
    refresh_token_expiry: int = 7

class BaseConfig(BaseModel):
    database: DatabaseSettings
    app: AppSettings
    jwt: JwtSettings
