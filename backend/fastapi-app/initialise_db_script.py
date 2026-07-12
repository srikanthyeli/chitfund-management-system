import asyncio
import uuid
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import src
backend_root = Path(__file__).resolve().parent
sys.path.append(str(backend_root))

from src.shared.core.database import init_pool, close_pool
import src.shared.core.database as database
from src.shared.core.properties.constants import UserRole

async def create_admin():
    await init_pool()
    
    # You can change this mobile number to your actual mobile number
    admin_mobile = "9999999999"  
    
    async with database.async_pg_pool.acquire() as conn:
        try:
            # Check if admin already exists
            row = await conn.fetchrow("SELECT id FROM users WHERE mobile = $1", admin_mobile)
            if row:
                print(f"Admin user with mobile {admin_mobile} already exists. User ID: {row['id']}")
            else:
                # Create new admin user
                admin_id = str(uuid.uuid4())
                await conn.execute(
                    """
                INSERT INTO users (id, mobile, role, is_active, is_deleted, version)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                admin_id, admin_mobile, UserRole.ADMIN.value, True, False, 1
                )
                print(f"✅ Successfully created ADMIN user with mobile: {admin_mobile}")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            print("Make sure you have run your database migrations (alembic upgrade head) first!")
            
    await close_pool()

if __name__ == "__main__":
    asyncio.run(create_admin())
