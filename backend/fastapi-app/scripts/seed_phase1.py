import asyncio
import asyncpg
from pathlib import Path
import sys

# Add backend directory to Python path so src can be imported
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from src.shared.core.properties.app_properties import settings
from src.shared.common.helpers.password_helper import hash_password
from src.shared.core.repository.user_repository import UserRepository

async def seed_admin():
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database.db_url)
    
    try:
        user_repo = UserRepository(conn)
        mobile = "9999999999"
        
        existing = await user_repo.get_user_by_mobile(mobile)
        if existing:
            print(f"Admin user with mobile {mobile} already exists.")
            return

        print("Creating admin user...")
        user_data = {
            "mobile": mobile,
            "password_hash": hash_password("Admin@123"),
            "role": "ADMIN",
            "is_active": True,
            "must_change_password": False
        }
        
        await user_repo.create_user(user_data)
        print("Admin user seeded successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_admin())
