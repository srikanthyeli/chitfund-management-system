import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain password against its hashed version."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
