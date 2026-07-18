import asyncio
import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()
async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    users = await conn.fetch('SELECT id, mobile, password_hash FROM users LIMIT 5')
    for u in users:
        print(dict(u))
    await conn.close()
asyncio.run(main())
