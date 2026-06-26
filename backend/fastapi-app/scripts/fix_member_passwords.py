import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

import asyncio
import asyncpg

from src.shared.core.properties.app_properties import settings
from src.shared.common.helpers.password_helper import hash_password

async def fix_member_passwords():
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database.db_url)
    
    try:
        new_password = "Member@123"
        hashed_pw = hash_password(new_password)
        
        # Update all users with role MEMBER to have Member@123 as password
        result = await conn.execute("UPDATE users SET password_hash = $1 WHERE role = 'MEMBER'", hashed_pw)
        
        print(f"Updated passwords for members. Result: {result}")
        print("Now you should be able to log in with Member@123!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_member_passwords())
