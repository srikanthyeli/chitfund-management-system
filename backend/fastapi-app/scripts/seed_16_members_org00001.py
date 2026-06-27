import sys
from pathlib import Path

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

ORGANIZER_ID = uuid.UUID("e6ff5f5e-b514-44e6-849a-314959fe9c32")
USER_ID      = uuid.UUID("57a39853-653f-4f7c-87b5-15fbe5675765")

class MockCurrentUser:
    def __init__(self):
        self.id           = USER_ID
        self.organizer_id = ORGANIZER_ID
        self.role         = "ORGANIZER"

MEMBERS = [
    {"full_name": "Arjun Reddy",       "mobile": "9100000001", "village": "Vijayawada"},
    {"full_name": "Lakshmi Devi",       "mobile": "9100000002", "village": "Guntur"},
    {"full_name": "Venkata Rao",        "mobile": "9100000003", "village": "Rajahmundry"},
    {"full_name": "Padmavathi Naidu",   "mobile": "9100000004", "village": "Kakinada"},
    {"full_name": "Srinivas Murthy",    "mobile": "9100000005", "village": "Nellore"},
    {"full_name": "Anitha Krishnan",    "mobile": "9100000006", "village": "Tirupati"},
    {"full_name": "Ravi Shankar",       "mobile": "9100000007", "village": "Vizag"},
    {"full_name": "Sarada Devi",        "mobile": "9100000008", "village": "Eluru"},
    {"full_name": "Nagarjuna Babu",     "mobile": "9100000009", "village": "Ongole"},
    {"full_name": "Kamala Kumari",      "mobile": "9100000010", "village": "Kurnool"},
    {"full_name": "Suresh Babu",        "mobile": "9100000011", "village": "Anantapur"},
    {"full_name": "Hymavathi Rao",      "mobile": "9100000012", "village": "Vizianagaram"},
    {"full_name": "Ramana Prasad",      "mobile": "9100000013", "village": "Srikakulam"},
    {"full_name": "Tulasi Devi",        "mobile": "9100000014", "village": "Bhimavaram"},
    {"full_name": "Krishna Mohan",      "mobile": "9100000015", "village": "Tenali"},
    {"full_name": "Vasantha Lakshmi",   "mobile": "9100000016", "village": "Machilipatnam"},
]

async def main():
    conn = await asyncpg.connect(settings.database.db_url)
    try:
        service      = MemberService(conn)
        current_user = MockCurrentUser()

        for i, m in enumerate(MEMBERS, start=1):
            req = MemberCreateRequest(
                full_name=m["full_name"],
                mobile=m["mobile"],
                village=m["village"],
                mandal="Serilingampally",
                district="Rangareddy",
                state="Telangana",
                pincode="500032",
                aadhaar_last4=f"{2000 + i}"[-4:],
                notes="Seeded via seed_16_members_org00001"
            )
            try:
                member = await service.create_member(current_user, req)
                print(f"[{i:02d}/16] ✓ {member.full_name} ({member.member_code})")
            except HTTPException as e:
                if e.status_code == 409:
                    print(f"[{i:02d}/16] skip – {m['mobile']} already exists")
                else:
                    print(f"[{i:02d}/16] error – {m['full_name']}: {e.detail}")
            except Exception as e:
                print(f"[{i:02d}/16] error – {m['full_name']}: {e}")

        print("\nDone.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
