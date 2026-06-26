import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

import asyncio
import asyncpg
from src.shared.core.properties.app_properties import settings

async def check():
    conn = await asyncpg.connect(settings.database.db_url)
    try:
        user = await conn.fetchrow("SELECT id, member_id, mobile FROM users WHERE mobile='9876543210'")
        print(f"User: {user}")
        if not user: return
        
        member = await conn.fetchrow("SELECT id, full_name FROM members WHERE id=$1", user["member_id"])
        print(f"Member: {member}")
        
        mships = await conn.fetch("SELECT * FROM chit_memberships WHERE member_id=$1", user["member_id"])
        print(f"Memberships count: {len(mships)}")
        for m in mships:
            print(f"  - Chit Group ID: {m['chit_group_id']}, Shares: {m['number_of_shares']}")
            
        dues = await conn.fetch("SELECT * FROM monthly_member_dues WHERE member_id=$1", user["member_id"])
        print(f"Dues count: {len(dues)}")
        
    finally:
        await conn.close()

asyncio.run(check())
