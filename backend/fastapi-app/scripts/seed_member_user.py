import asyncio
import asyncpg
from pathlib import Path
import sys
import uuid

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from src.shared.core.properties.app_properties import settings
from src.shared.common.helpers.password_helper import hash_password

async def restore_and_seed():
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database.db_url)
    
    try:
        # Restore organizer
        await conn.execute("UPDATE users SET role='ORGANIZER' WHERE mobile='9505563253'")
        
        # Restore organizer's password just in case
        org_hashed = hash_password("Organizer@123")
        await conn.execute("UPDATE users SET password_hash=$1 WHERE mobile='9505563253'", org_hashed)
        print("Restored Organizer (9505563253) to role=ORGANIZER and password=Organizer@123")

        # Pick a different member that is NOT the organizer (mobile != '9505563253')
        member = await conn.fetchrow("SELECT id, organizer_id, mobile, full_name FROM members WHERE mobile != '9505563253' LIMIT 1")
        if not member:
            print("No suitable members found for testing. Please run seed_15_members.py.")
            return

        member_id = member['id']
        organizer_id = member['organizer_id']
        mobile = member['mobile']
        full_name = member['full_name']
        print(f"Found suitable member for testing: {full_name} ({mobile})")

        user = await conn.fetchrow("SELECT id FROM users WHERE mobile = $1", mobile)
        password = "Member@123"
        hashed_pw = hash_password(password)

        if user:
            print("User account for member already exists. Updating password to Member@123.")
            await conn.execute("UPDATE users SET password_hash=$1, role='MEMBER', member_id=$2 WHERE mobile=$3", hashed_pw, member_id, mobile)
        else:
            user_id = uuid.uuid4()
            await conn.execute("""
                INSERT INTO users (id, organizer_id, member_id, mobile, password_hash, role, is_active, must_change_password, is_deleted, version)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, FALSE, 1)
            """, user_id, organizer_id, member_id, mobile, hashed_pw, "MEMBER", True, False)

        print(f"--------------------------------------------------")
        print(f"MEMBER LOGIN DETAILS:")
        print(f"Mobile: {mobile}")
        print(f"Password: {password}")
        print(f"--------------------------------------------------")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(restore_and_seed())
