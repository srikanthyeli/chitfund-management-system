import pytest
import pytest_asyncio
import asyncpg
from httpx import AsyncClient, ASGITransport
import uuid
from datetime import datetime, timedelta

from src.api.main import app
from src.shared.core.database import get_db_session
from src.shared.core.properties.app_properties import settings
from src.shared.common.helpers.password_helper import hash_password
from src.shared.common.helpers.jwt_helper import create_access_token

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture
async def db_conn():
    conn = await asyncpg.connect(settings.database.db_url)
    tr = conn.transaction()
    await tr.start()

    async def override_get_db_session():
        yield conn

    app.dependency_overrides[get_db_session] = override_get_db_session
    yield conn

    await tr.rollback()
    await conn.close()
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

async def create_test_user_session(db, user_id):
    session_id = uuid.uuid4()
    now = datetime.utcnow()
    access_exp = now + timedelta(minutes=30)
    refresh_exp = now + timedelta(days=7)
    refresh_token = f"test_refresh_{uuid.uuid4()}"
    
    query = """
        INSERT INTO user_sessions (
            id, user_id, device_id, device_name, ip_address, refresh_token, 
            login_at, access_token_expires_at, refresh_token_expires_at, is_active, 
            version, created_at, is_deleted
        )
        VALUES ($1, $2, 'test_device', 'test_name', '127.0.0.1', $3, $4, $5, $6, TRUE, 1, $4, FALSE)
        RETURNING id
    """
    await db.execute(query, session_id, user_id, refresh_token, now, access_exp, refresh_exp)
    return session_id

@pytest_asyncio.fixture
async def test_admin(db_conn):
    # Create admin user
    user_id = uuid.uuid4()
    mobile = f"99{uuid.uuid4().hex[:8]}"
    query = """
        INSERT INTO users (id, mobile, password_hash, role, is_active, must_change_password, version, created_at, is_deleted)
        VALUES ($1, $2, $3, 'ADMIN', TRUE, FALSE, 1, NOW(), FALSE)
    """
    await db_conn.execute(query, user_id, mobile, hash_password("Password@123"))
    
    session_id = await create_test_user_session(db_conn, user_id)
    
    payload = {
        "user_id": str(user_id),
        "organizer_id": None,
        "role": "ADMIN",
        "session_id": str(session_id),
        "token_type": "access"
    }
    token = create_access_token(payload)
    return {"token": token, "user_id": user_id}

@pytest_asyncio.fixture
async def test_organizer_a(db_conn):
    org_id = uuid.uuid4()
    org_code = f"ORG{uuid.uuid4().hex[:5].upper()}"
    org_mobile = f"88{uuid.uuid4().hex[:8]}"
    
    # Create Organizer Org
    query_org = """
        INSERT INTO organizers (id, organizer_code, name, mobile, is_active, version, created_at, is_deleted)
        VALUES ($1, $2, 'Organizer A Corp', $3, TRUE, 1, NOW(), FALSE)
    """
    await db_conn.execute(query_org, org_id, org_code, org_mobile)

    # Create Organizer User
    user_id = uuid.uuid4()
    user_mobile = f"77{uuid.uuid4().hex[:8]}"
    query_user = """
        INSERT INTO users (id, organizer_id, mobile, password_hash, role, is_active, must_change_password, version, created_at, is_deleted)
        VALUES ($1, $2, $3, $4, 'ORGANIZER', TRUE, FALSE, 1, NOW(), FALSE)
    """
    await db_conn.execute(query_user, user_id, org_id, user_mobile, hash_password("Password@123"))
    
    session_id = await create_test_user_session(db_conn, user_id)
    
    payload = {
        "user_id": str(user_id),
        "organizer_id": str(org_id),
        "role": "ORGANIZER",
        "session_id": str(session_id),
        "token_type": "access"
    }
    token = create_access_token(payload)
    return {"token": token, "organizer_id": org_id, "user_id": user_id}

@pytest_asyncio.fixture
async def test_organizer_b(db_conn):
    org_id = uuid.uuid4()
    org_code = f"ORG{uuid.uuid4().hex[:5].upper()}"
    org_mobile = f"66{uuid.uuid4().hex[:8]}"
    
    # Create Organizer Org
    query_org = """
        INSERT INTO organizers (id, organizer_code, name, mobile, is_active, version, created_at, is_deleted)
        VALUES ($1, $2, 'Organizer B Corp', $3, TRUE, 1, NOW(), FALSE)
    """
    await db_conn.execute(query_org, org_id, org_code, org_mobile)

    # Create Organizer User
    user_id = uuid.uuid4()
    user_mobile = f"55{uuid.uuid4().hex[:8]}"
    query_user = """
        INSERT INTO users (id, organizer_id, mobile, password_hash, role, is_active, must_change_password, version, created_at, is_deleted)
        VALUES ($1, $2, $3, $4, 'ORGANIZER', TRUE, FALSE, 1, NOW(), FALSE)
    """
    await db_conn.execute(query_user, user_id, org_id, user_mobile, hash_password("Password@123"))
    
    session_id = await create_test_user_session(db_conn, user_id)
    
    payload = {
        "user_id": str(user_id),
        "organizer_id": str(org_id),
        "role": "ORGANIZER",
        "session_id": str(session_id),
        "token_type": "access"
    }
    token = create_access_token(payload)
    return {"token": token, "organizer_id": org_id, "user_id": user_id}
