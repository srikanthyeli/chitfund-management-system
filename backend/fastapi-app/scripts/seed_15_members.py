import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

import asyncio
import asyncpg
import uuid
from fastapi import HTTPException

from src.shared.core.properties.app_properties import settings
from src.shared.core.services.member_service import MemberService
from src.api.schemas.member_schema import MemberCreateRequest
from src.shared.common.helpers.password_helper import hash_password

class MockCurrentUser:
    def __init__(self, user_id, organizer_id):
        self.id = user_id
        self.organizer_id = organizer_id
        self.role = "ORGANIZER"

async def seed_15_members():
    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database.db_url)
    
    try:
        target_org_id = uuid.UUID("f7d329e1-a717-44a7-aed8-dc619f7f7170")
        target_user_id = uuid.UUID("8f9c8686-2a4b-42a1-8942-de85bba6d793")
        target_mobile = "1234567890"

        # 1. Clear conflicting records with target mobile
        await conn.execute("DELETE FROM users WHERE mobile = $1 AND id != $2", target_mobile, target_user_id)
        await conn.execute("DELETE FROM organizers WHERE mobile = $1 AND id != $2", target_mobile, target_org_id)

        # 2. Check and insert Organizer
        org_row = await conn.fetchrow("SELECT * FROM organizers WHERE id = $1", target_org_id)
        if not org_row:
            print("Creating organizer 'Yelisetty Srikanth'...")
            await conn.execute("""
                INSERT INTO organizers (id, organizer_code, name, mobile, is_active)
                VALUES ($1, $2, $3, $4, $5)
            """, target_org_id, "ORG00002", "Yelisetty Srikanth", target_mobile, True)
        else:
            print(f"Organizer 'Yelisetty Srikanth' exists.")

        # 3. Check and insert User
        user_row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", target_user_id)
        if not user_row:
            print("Creating user for organizer...")
            await conn.execute("""
                INSERT INTO users (id, organizer_id, mobile, password_hash, role, is_active, must_change_password)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, target_user_id, target_org_id, target_mobile, hash_password("Organizer@123"), "ORGANIZER", True, True)
        else:
            print("Organizer user exists.")

        print(f"Seeding members for Organizer: Yelisetty Srikanth ({target_org_id})")

        member_service = MemberService(conn)
        current_user = MockCurrentUser(target_user_id, target_org_id)

        # 2. Define 15 realistic members
        members_to_seed = [
            {"full_name": "Rajesh Patel", "mobile": "9876543210", "village": "Serilingampally"},
            {"full_name": "Sunita Rao", "mobile": "9876543211", "village": "Gachibowli"},
            {"full_name": "Anil Sharma", "mobile": "9876543212", "village": "Miyapur"},
            {"full_name": "Priya Verma", "mobile": "9876543213", "village": "Madhapur"},
            {"full_name": "Vijay Kumar", "mobile": "9876543214", "village": "Kondapur"},
            {"full_name": "Laxmi Nair", "mobile": "9876543215", "village": "Serilingampally"},
            {"full_name": "Suresh Reddy", "mobile": "9876543216", "village": "Gachibowli"},
            {"full_name": "Deepa Gupta", "mobile": "9876543217", "village": "Miyapur"},
            {"full_name": "Ramesh Prasad", "mobile": "9876543218", "village": "Madhapur"},
            {"full_name": "Gita Devi", "mobile": "9876543219", "village": "Kondapur"},
            {"full_name": "Mohan Singh", "mobile": "9876543220", "village": "Serilingampally"},
            {"full_name": "Radha Joshi", "mobile": "9876543221", "village": "Gachibowli"},
            {"full_name": "Sanjay Yadav", "mobile": "9876543222", "village": "Miyapur"},
            {"full_name": "Kavitha Swamy", "mobile": "9876543223", "village": "Madhapur"},
            {"full_name": "Vikram Malhotra", "mobile": "9876543224", "village": "Kondapur"}
        ]

        # 3. Insert each member
        for index, m in enumerate(members_to_seed, start=1):
            req = MemberCreateRequest(
                full_name=m["full_name"],
                mobile=m["mobile"],
                village=m["village"],
                mandal="Serilingampally",
                district="Rangareddy",
                state="Telangana",
                pincode="500032",
                aadhaar_last4=f"{1000 + index}"[-4:],
                notes="Seeded via automation script"
            )
            try:
                member = await member_service.create_member(current_user, req)
                print(f"[{index}/15] Seeded member {member.full_name} ({member.member_code}) successfully.")
            except HTTPException as e:
                if e.status_code == 409:
                    print(f"[{index}/15] Skipping: Member with mobile {m['mobile']} already exists.")
                else:
                    print(f"[{index}/15] Failed to seed {m['full_name']}: {e.detail}")
            except Exception as e:
                print(f"[{index}/15] Unexpected error for {m['full_name']}: {str(e)}")
                
        print("Done seeding members!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_15_members())
