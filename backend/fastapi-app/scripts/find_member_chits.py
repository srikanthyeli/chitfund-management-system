import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

import asyncio
import asyncpg
import uuid

from src.shared.core.properties.app_properties import settings
from src.shared.common.helpers.password_helper import hash_password

async def find_member_with_chits():
    conn = await asyncpg.connect(settings.database.db_url)
    try:
        mships = await conn.fetch("SELECT member_id, count(*) as count FROM chit_memberships GROUP BY member_id ORDER BY count DESC LIMIT 1")
        if not mships:
            print("No members have chits!")
            return
            
        member_id = mships[0]['member_id']
        member = await conn.fetchrow("SELECT * FROM members WHERE id=$1", member_id)
        print(f"Member with chits: {member['full_name']} ({member['mobile']})")
        
        # Check if they have a user account, if not create one
        user = await conn.fetchrow("SELECT id FROM users WHERE mobile=$1", member['mobile'])
        if not user:
            print("Creating user account for this member...")
            hashed_pw = hash_password("Member@123")
            await conn.execute("""
                INSERT INTO users (id, organizer_id, member_id, mobile, password_hash, role, is_active, must_change_password, is_deleted, version)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, FALSE, 1)
            """, uuid.uuid4(), member['organizer_id'], member_id, member['mobile'], hashed_pw, "MEMBER", True, False)
        else:
            print("User account exists for this member.")
        
    finally:
        await conn.close()

asyncio.run(find_member_with_chits())
