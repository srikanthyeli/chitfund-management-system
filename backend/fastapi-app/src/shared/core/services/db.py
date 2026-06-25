from contextlib import contextmanager
from src.shared.core.database import SessionLocal

@contextmanager
def transaction_context():
    """
    Context manager for database transactions.
    It automatically commits on success and rolls back on exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
