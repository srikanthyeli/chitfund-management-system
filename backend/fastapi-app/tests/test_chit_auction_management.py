"""
Phase 4: Chit Auction Management Tests
Tests cover all 18 required scenarios.
"""
import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import date, datetime

pytestmark = pytest.mark.anyio


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def create_chit_group(db, organizer_id, user_id, status="ACTIVE") -> uuid.UUID:
    chit_id = uuid.uuid4()
    await db.execute("""
        INSERT INTO chit_groups (
            id, organizer_id, chit_code, chit_name, total_chit_value,
            monthly_installment_per_share, total_shares, duration_months,
            maintenance_charge, maintenance_charge_type, start_date,
            installment_due_day, status, allocated_shares, available_shares,
            created_by, is_deleted, version, created_at
        ) VALUES (
            $1, $2, $3, $4, 100000,
            6250, 16, 16,
            4000, 'FIXED', '2026-01-01',
            1, $5, 16, 0,
            $6, FALSE, 1, NOW()
        )
    """, chit_id, organizer_id, f"CHIT{uuid.uuid4().hex[:5]}", f"Test Chit {uuid.uuid4().hex[:4]}", status, user_id)
    return chit_id


async def create_member(db, organizer_id, user_id, is_active=True) -> uuid.UUID:
    member_id = uuid.uuid4()
    code = f"MEM{uuid.uuid4().hex[:6].upper()}"
    mobile = f"9{uuid.uuid4().hex[:9]}"
    await db.execute("""
        INSERT INTO members (id, organizer_id, member_code, full_name, mobile, is_active, is_deleted, version, created_at, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, FALSE, 1, NOW(), $7)
    """, member_id, organizer_id, code, f"Test Member {code}", mobile, is_active, user_id)
    return member_id


async def create_membership(db, organizer_id, chit_group_id, member_id, user_id, share_count=1, has_won=False) -> uuid.UUID:
    mem_id = uuid.uuid4()
    await db.execute("""
        INSERT INTO chit_memberships (
            id, organizer_id, chit_group_id, member_id, share_count,
            joined_at, status, has_won_auction, is_deleted, version, created_at, created_by
        ) VALUES ($1, $2, $3, $4, $5, NOW(), 'ACTIVE', $6, FALSE, 1, NOW(), $7)
    """, mem_id, organizer_id, chit_group_id, member_id, share_count, has_won, user_id)
    return mem_id


async def create_auction(db, organizer_id, chit_group_id, user_id, month=1, status="OPEN") -> uuid.UUID:
    auction_id = uuid.uuid4()
    await db.execute("""
        INSERT INTO chit_auctions (
            id, organizer_id, chit_group_id, auction_month_number, auction_date,
            status, gross_chit_amount, maintenance_charge, maximum_bid_discount,
            is_deleted, version, created_at, created_by
        ) VALUES ($1, $2, $3, $4, '2026-01-25', $5, 100000, 4000, 96000, FALSE, 1, NOW(), $6)
    """, auction_id, organizer_id, chit_group_id, month, status, user_id)
    return auction_id


async def create_bid(db, organizer_id, auction_id, chit_group_id, membership_id, member_id, user_id, amount) -> uuid.UUID:
    bid_id = uuid.uuid4()
    await db.execute("""
        INSERT INTO chit_auction_bids (
            id, organizer_id, chit_auction_id, chit_group_id, membership_id, member_id,
            bid_discount_amount, bid_time, status, is_deleted, version, created_at, created_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), 'ACTIVE', FALSE, 1, NOW(), $8)
    """, bid_id, organizer_id, auction_id, chit_group_id, membership_id, member_id, Decimal(str(amount)), user_id)
    return bid_id


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Test 1: Create auction successfully ─────────────────────────────────────

async def test_create_auction_success(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")

    resp = await client.post(
        f"/api/v1/chit-groups/{chit_id}/auctions",
        json={"auction_month_number": 1, "auction_date": "2026-01-25", "maintenance_charge": 4000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["auction_month_number"] == 1
    assert data["status"] == "OPEN"
    assert Decimal(str(data["gross_chit_amount"])) == Decimal("100000.00")
    assert Decimal(str(data["maximum_bid_discount"])) == Decimal("96000.00")


# ─── Test 2: Only organizer can create auction ────────────────────────────────

async def test_only_organizer_can_create_auction(db_conn, client, test_admin, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")

    resp = await client.post(
        f"/api/v1/chit-groups/{chit_id}/auctions",
        json={"auction_month_number": 1, "auction_date": "2026-01-25", "maintenance_charge": 4000},
        headers=auth_headers(test_admin["token"]),
    )
    assert resp.status_code == 403


# ─── Test 3: Cannot create duplicate auction for same chit and month ──────────

async def test_no_duplicate_auction_same_month(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    await create_auction(db_conn, org_id, chit_id, user_id, month=1)

    resp = await client.post(
        f"/api/v1/chit-groups/{chit_id}/auctions",
        json={"auction_month_number": 1, "auction_date": "2026-01-25", "maintenance_charge": 4000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409


# ─── Test 4: Inactive member cannot bid ──────────────────────────────────────

async def test_inactive_member_cannot_bid(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    inactive_member_id = await create_member(db_conn, org_id, user_id, is_active=False)

    # Create membership with inactive member (status ACTIVE but member is_active=False)
    mem_id = uuid.uuid4()
    await db_conn.execute("""
        INSERT INTO chit_memberships (
            id, organizer_id, chit_group_id, member_id, share_count,
            joined_at, status, has_won_auction, is_deleted, version, created_at, created_by
        ) VALUES ($1, $2, $3, $4, 1, NOW(), 'INACTIVE', FALSE, FALSE, 1, NOW(), $5)
    """, mem_id, org_id, chit_id, inactive_member_id, user_id)

    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)

    resp = await client.post(
        f"/api/v1/chit-auctions/{auction_id}/bids",
        json={"membership_id": str(mem_id), "bid_discount_amount": 5000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


# ─── Test 5: Previous winner cannot bid again ────────────────────────────────

async def test_previous_winner_cannot_bid(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    member_id = await create_member(db_conn, org_id, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id, month=1)
    # Create membership marked as already won
    mem_id = await create_membership(db_conn, org_id, chit_id, member_id, user_id, has_won=True)

    auction_id2 = await create_auction(db_conn, org_id, chit_id, user_id, month=2)

    resp = await client.post(
        f"/api/v1/chit-auctions/{auction_id2}/bids",
        json={"membership_id": str(mem_id), "bid_discount_amount": 5000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


# ─── Test 6: Member cannot submit duplicate bid ───────────────────────────────

async def test_no_duplicate_bid(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    member_id = await create_member(db_conn, org_id, user_id)
    mem_id = await create_membership(db_conn, org_id, chit_id, member_id, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem_id, member_id, user_id, 5000)

    resp = await client.post(
        f"/api/v1/chit-auctions/{auction_id}/bids",
        json={"membership_id": str(mem_id), "bid_discount_amount": 6000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 409


# ─── Test 7: Highest bid wins ────────────────────────────────────────────────

async def test_highest_bid_wins(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    m2 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    mem2 = await create_membership(db_conn, org_id, chit_id, m2, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)

    await create_bid(db_conn, org_id, auction_id, chit_id, mem1, m1, user_id, 10000)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem2, m2, user_id, 15000)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert str(data["winner_membership_id"]) == str(mem2)
    assert str(data["winner_member_id"]) == str(m2)


# ─── Test 8: Tie selects earliest bid ────────────────────────────────────────

async def test_tie_bid_selects_earliest(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    m2 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    mem2 = await create_membership(db_conn, org_id, chit_id, m2, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)

    # Insert bids with explicit bid_time order
    bid1_id = uuid.uuid4()
    bid2_id = uuid.uuid4()
    await db_conn.execute("""
        INSERT INTO chit_auction_bids (id, organizer_id, chit_auction_id, chit_group_id, membership_id, member_id,
            bid_discount_amount, bid_time, status, is_deleted, version, created_at, created_by)
        VALUES ($1,$2,$3,$4,$5,$6, 15000, '2026-01-25 10:00:00', 'ACTIVE', FALSE, 1, NOW(), $7)
    """, bid1_id, org_id, auction_id, chit_id, mem1, m1, user_id)
    await db_conn.execute("""
        INSERT INTO chit_auction_bids (id, organizer_id, chit_auction_id, chit_group_id, membership_id, member_id,
            bid_discount_amount, bid_time, status, is_deleted, version, created_at, created_by)
        VALUES ($1,$2,$3,$4,$5,$6, 15000, '2026-01-25 11:00:00', 'ACTIVE', FALSE, 1, NOW(), $7)
    """, bid2_id, org_id, auction_id, chit_id, mem2, m2, user_id)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200
    # mem1 placed bid earlier — should win
    assert str(resp.json()["winner_membership_id"]) == str(mem1)


# ─── Test 9: Winner payout calculation is correct ────────────────────────────

async def test_winner_payout_calculation(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem1, m1, user_id, 15000)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # gross=100000, maintenance=4000, discount=15000 → payout=81000
    assert Decimal(str(data["winner_payout_amount"])) == Decimal("81000.00")


# ─── Test 10: Dividend per share calculation ──────────────────────────────────

async def test_dividend_per_share_calculation(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    # 16 shares total (one member holds all for simplicity — or create 16 members)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id, share_count=16)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem1, m1, user_id, 15000)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # 15000 / 16 = 937.50
    assert Decimal(str(data["dividend_per_share"])) == Decimal("937.50")


# ─── Test 11: Multi-share member receives correct dividend ────────────────────

async def test_multi_share_dividend(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    m2 = await create_member(db_conn, org_id, user_id)
    # m1 has 2 shares, m2 has 14 shares = 16 total
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id, share_count=2)
    mem2 = await create_membership(db_conn, org_id, chit_id, m2, user_id, share_count=14)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem2, m2, user_id, 15000)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    # dividend_per_share = 15000/16 = 937.50
    assert Decimal(str(data["dividend_per_share"])) == Decimal("937.50")

    # Verify dues for m1 (2 shares): total_dividend = 937.50 * 2 = 1875
    dues = await client.get(f"/api/v1/chit-auctions/{auction_id}/dues", headers=auth_headers(token))
    assert dues.status_code == 200
    m1_due = next(d for d in dues.json() if str(d["member_id"]) == str(m1))
    assert Decimal(str(m1_due["total_dividend_amount"])) == Decimal("1875.00")
    # net_payable = 6250*2 - 1875 = 10625
    assert Decimal(str(m1_due["net_payable_amount"])) == Decimal("10625.00")


# ─── Test 12: Monthly dues generated for all active memberships ───────────────

async def test_dues_generated_for_all_memberships(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    members = [await create_member(db_conn, org_id, user_id) for _ in range(4)]
    memberships = [await create_membership(db_conn, org_id, chit_id, m, user_id, share_count=4) for m in members]
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, memberships[0], members[0], user_id, 12000)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 200

    dues = await client.get(f"/api/v1/chit-auctions/{auction_id}/dues", headers=auth_headers(token))
    assert len(dues.json()) == 4  # One due per membership


# ─── Test 13: Auction cannot be finalized twice ───────────────────────────────

async def test_cannot_finalize_twice(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem1, m1, user_id, 10000)

    r1 = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert r1.status_code == 200

    r2 = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert r2.status_code == 400


# ─── Test 14: Cannot bid with amount > max allowed ────────────────────────────

async def test_bid_exceeds_max_allowed(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)

    resp = await client.post(
        f"/api/v1/chit-auctions/{auction_id}/bids",
        json={"membership_id": str(mem1), "bid_discount_amount": 97000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


# ─── Test 15: Auction with no bids cannot be finalized ───────────────────────

async def test_cannot_finalize_with_no_bids(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    await create_member(db_conn, org_id, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)

    resp = await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))
    assert resp.status_code == 400


# ─── Test 16: Cannot create auction on DRAFT chit ────────────────────────────

async def test_cannot_create_auction_on_draft_chit(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="DRAFT")

    resp = await client.post(
        f"/api/v1/chit-groups/{chit_id}/auctions",
        json={"auction_month_number": 1, "auction_date": "2026-01-25", "maintenance_charge": 4000},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


# ─── Test 17: Activity logs are created on finalization ───────────────────────

async def test_activity_logs_created(db_conn, client, test_organizer_a):
    org_id = test_organizer_a["organizer_id"]
    user_id = test_organizer_a["user_id"]
    token = test_organizer_a["token"]

    chit_id = await create_chit_group(db_conn, org_id, user_id, status="ACTIVE")
    m1 = await create_member(db_conn, org_id, user_id)
    mem1 = await create_membership(db_conn, org_id, chit_id, m1, user_id)
    auction_id = await create_auction(db_conn, org_id, chit_id, user_id)
    await create_bid(db_conn, org_id, auction_id, chit_id, mem1, m1, user_id, 10000)

    await client.post(f"/api/v1/chit-auctions/{auction_id}/finalize", headers=auth_headers(token))

    logs = await db_conn.fetch(
        "SELECT action_type FROM chit_group_activity_logs WHERE chit_group_id=$1 ORDER BY created_at",
        chit_id
    )
    action_types = [r["action_type"] for r in logs]
    # Note: AUCTION_CREATED is only logged when auction is created via the API endpoint,
    # not via the raw SQL helper used in this test. We validate finalization logs here.
    assert "AUCTION_FINALIZED" in action_types
    assert "AUCTION_WINNER_DECLARED" in action_types
    assert "MONTHLY_DUES_GENERATED" in action_types


# ─── Test 18: Organizer B cannot access organizer A's auction ────────────────

async def test_cross_organizer_isolation(db_conn, client, test_organizer_a, test_organizer_b):
    org_a_id = test_organizer_a["organizer_id"]
    user_a_id = test_organizer_a["user_id"]
    token_b = test_organizer_b["token"]

    chit_id = await create_chit_group(db_conn, org_a_id, user_a_id, status="ACTIVE")
    auction_id = await create_auction(db_conn, org_a_id, chit_id, user_a_id)

    resp = await client.get(f"/api/v1/chit-auctions/{auction_id}", headers=auth_headers(token_b))
    assert resp.status_code == 404
