import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Decode byte string to normal string for database storage
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        # Encode inputs to bytes and compare
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
