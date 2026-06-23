import os
import configparser
from pathlib import Path
from dotenv import load_dotenv
from src.shared.core.properties.app_base_properties import BaseConfig, DatabaseSettings, AppSettings, JwtSettings

# Load environment variables from .env file if it exists
load_dotenv()

def load_properties() -> BaseConfig:
    env = os.getenv("ENVIRONMENT", "local").lower()
    
    # Resolve config directory relative to this file
    current_file = Path(__file__).resolve()
    backend_root = current_file.parents[4]  # goes up to fastapi-app
    config_path = backend_root / "config" / f"{env}.config.ini"
    
    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path)
    else:
        config.add_section("database")
        config.add_section("app")
        config.add_section("jwt")
        
    # Read values with fallbacks
    db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or config.get("database", "db_url", fallback="postgresql://chitfund_admin:chitfund_password@localhost:5432/chitfund_db")
    
    app_env = os.getenv("ENVIRONMENT") or config.get("app", "env", fallback=env)
    debug_val = os.getenv("DEBUG")
    if debug_val is not None:
        debug = debug_val.lower() in ("true", "1", "yes")
    else:
        debug = config.getboolean("app", "debug", fallback=True)
        
    secret_key = os.getenv("SECRET_KEY") or config.get("app", "secret_key", fallback="change_me_local")
    
    expire_minutes_val = os.getenv("TOKEN_EXPIRE_MINUTES")
    if expire_minutes_val is not None:
        token_expire_minutes = int(expire_minutes_val)
    else:
        token_expire_minutes = config.getint("app", "token_expire_minutes", fallback=60)
        
    # JWT values
    jwt_secret_key = os.getenv("JWT_SECRET_KEY") or config.get("jwt", "secret_key", fallback="jwt_secret_key_change_me")
    jwt_algorithm = os.getenv("JWT_ALGORITHM") or config.get("jwt", "algorithm", fallback="HS256")
    jwt_access_expiry = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRY") or config.get("jwt", "access_token_expiry", fallback="60"))
    jwt_refresh_expiry = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRY") or config.get("jwt", "refresh_token_expiry", fallback="7"))

    return BaseConfig(
        database=DatabaseSettings(db_url=db_url),
        app=AppSettings(
            env=app_env,
            debug=debug,
            secret_key=secret_key,
            token_expire_minutes=token_expire_minutes
        ),
        jwt=JwtSettings(
            secret_key=jwt_secret_key,
            algorithm=jwt_algorithm,
            access_token_expiry=jwt_access_expiry,
            refresh_token_expiry=jwt_refresh_expiry
        )
    )

# Export a singleton instance of properties
settings = load_properties()
