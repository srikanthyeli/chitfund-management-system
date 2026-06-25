import pytest
import uuid
import json
from datetime import datetime, date

@pytest.mark.anyio
async def test_create_chit_group_success(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {
        "chit_name": "New Jan Lakhpati Scheme",
        "description": "Scheme description A",
        "total_shares": 10,
        "duration_months": 10,
        "monthly_installment_per_share": 10000,
        "total_chit_value": 100000,
        "maintenance_charge": 500,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-07-01",
        "installment_due_day": 10
    }

    # 1. Create Chit Group
    response = await client.post("/api/v1/chit-groups", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["chit_name"] == "New Jan Lakhpati Scheme"
    assert data["chit_code"] == "CHIT00001"
    assert data["status"] == "DRAFT"
    assert data["allocated_shares"] == 0
    assert data["available_shares"] == 10
    assert "id" in data

    # 2. Verify Database record
    chit_id = data["id"]
    row = await db_conn.fetchrow("SELECT * FROM chit_groups WHERE id = $1", uuid.UUID(chit_id))
    assert row is not None
    assert row["chit_code"] == "CHIT00001"

    # 3. Verify activity log
    logs = await db_conn.fetch("SELECT * FROM chit_group_activity_logs WHERE chit_group_id = $1", uuid.UUID(chit_id))
    assert len(logs) == 1
    assert logs[0]["action_type"] == "CHIT_CREATED"

@pytest.mark.anyio
async def test_create_chit_group_duplicate_name(client, test_organizer_a, test_organizer_b):
    headers_a = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {
        "chit_name": "Duplicate Group",
        "total_shares": 10,
        "duration_months": 10,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 50000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-08-01",
        "installment_due_day": 1
    }

    # Create once
    res1 = await client.post("/api/v1/chit-groups", json=payload, headers=headers_a)
    assert res1.status_code == 201

    # Create duplicate under organizer A (should block)
    res2 = await client.post("/api/v1/chit-groups", json=payload, headers=headers_a)
    assert res2.status_code == 409

    # Create same name under organizer B (should allow - isolation)
    headers_b = {"Authorization": f"Bearer {test_organizer_b['token']}"}
    res3 = await client.post("/api/v1/chit-groups", json=payload, headers=headers_b)
    assert res3.status_code == 201

@pytest.mark.anyio
async def test_create_chit_group_invalid_start_date(client, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {
        "chit_name": "Invalid Date Group",
        "total_shares": 10,
        "duration_months": 10,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 50000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-08-15", # Must be 1st of month
        "installment_due_day": 1
    }
    response = await client.post("/api/v1/chit-groups", json=payload, headers=headers)
    assert response.status_code == 422 # Pydantic validation error

@pytest.mark.anyio
async def test_update_chit_group_details(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # 1. Create Chit
    payload = {
        "chit_name": "Update Group",
        "total_shares": 10,
        "duration_months": 10,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 50000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-08-01",
        "installment_due_day": 1
    }
    res = await client.post("/api/v1/chit-groups", json=payload, headers=headers)
    chit_id = res.json()["id"]

    # 2. Update Details
    update_payload = {
        "chit_name": "Updated Group Name",
        "total_shares": 12,
        "duration_months": 12,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 60000
    }
    update_res = await client.put(f"/api/v1/chit-groups/{chit_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["chit_name"] == "Updated Group Name"
    assert data["total_shares"] == 12
    assert float(data["total_chit_value"]) == 60000

    # 3. Check activity logs
    logs = await db_conn.fetch(
        "SELECT * FROM chit_group_activity_logs WHERE chit_group_id = $1 AND action_type = 'CHIT_UPDATED'",
        uuid.UUID(chit_id)
    )
    assert len(logs) == 1

@pytest.mark.anyio
async def test_allocate_member_shares_workflow(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # 1. Onboard active Member
    member_res = await client.post("/api/v1/members", json={"full_name": "Alloc Member", "mobile": "9999911111"}, headers=headers)
    member_id = member_res.json()["id"]

    # 2. Create Chit Group (Total shares = 5)
    chit_res = await client.post("/api/v1/chit-groups", json={
        "chit_name": "Share Allocation Chit",
        "total_shares": 5,
        "duration_months": 5,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 25000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-09-01",
        "installment_due_day": 5
    }, headers=headers)
    chit_id = chit_res.json()["id"]

    # 3. Allocate 2 shares to Member
    alloc_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={
        "member_id": member_id,
        "share_count": 2,
        "remarks": "Allocated 2 shares"
    }, headers=headers)
    assert alloc_res.status_code == 200
    
    # Verify chit stats updated
    chit_detail = await client.get(f"/api/v1/chit-groups/{chit_id}", headers=headers)
    assert chit_detail.json()["allocated_shares"] == 2
    assert chit_detail.json()["available_shares"] == 3

    # 4. Try allocating duplicate membership (should block)
    dup_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={
        "member_id": member_id,
        "share_count": 1
    }, headers=headers)
    assert dup_res.status_code == 409

    # 5. Try allocating excess shares (3 available, requesting 4 - should block)
    excess_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={
        "member_id": member_id, # Actually block by duplicate check first, so create another member
    }, headers=headers)
    
    member2_res = await client.post("/api/v1/members", json={"full_name": "Alloc Member 2", "mobile": "9999911112"}, headers=headers)
    member2_id = member2_res.json()["id"]

    excess_res2 = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={
        "member_id": member2_id,
        "share_count": 4
    }, headers=headers)
    assert excess_res2.status_code == 409
    assert "exceed available shares" in excess_res2.json()["detail"]

@pytest.mark.anyio
async def test_update_and_remove_shares(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    member_res = await client.post("/api/v1/members", json={"full_name": "Share Worker", "mobile": "9999911115"}, headers=headers)
    member_id = member_res.json()["id"]

    chit_res = await client.post("/api/v1/chit-groups", json={
        "chit_name": "Share Adjusting Group",
        "total_shares": 5,
        "duration_months": 5,
        "monthly_installment_per_share": 5000,
        "total_chit_value": 25000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-10-01",
        "installment_due_day": 5
    }, headers=headers)
    chit_id = chit_res.json()["id"]

    # Allocate 1 share
    alloc = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={"member_id": member_id, "share_count": 1}, headers=headers)
    membership_id = alloc.json()["id"]

    # Update to 3 shares
    update_res = await client.put(
        f"/api/v1/chit-groups/{chit_id}/memberships/{membership_id}",
        json={"share_count": 3, "remarks": "Increased shares"},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["share_count"] == 3

    # Check chit stats
    detail_res = await client.get(f"/api/v1/chit-groups/{chit_id}", headers=headers)
    assert detail_res.json()["allocated_shares"] == 3

    # Soft remove member
    remove_res = await client.delete(
        f"/api/v1/chit-groups/{chit_id}/memberships/{membership_id}?remarks=Leaving%20scheme",
        headers=headers
    )
    assert remove_res.status_code == 200

    # Check chit stats reverted
    detail_res2 = await client.get(f"/api/v1/chit-groups/{chit_id}", headers=headers)
    assert detail_res2.json()["allocated_shares"] == 0
    assert detail_res2.json()["available_shares"] == 5

@pytest.mark.anyio
async def test_chit_status_transitions(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    member_res = await client.post("/api/v1/members", json={"full_name": "Full Member", "mobile": "9999911120"}, headers=headers)
    member_id = member_res.json()["id"]

    chit_res = await client.post("/api/v1/chit-groups", json={
        "chit_name": "Status Transition Chit",
        "total_shares": 2,
        "duration_months": 2,
        "monthly_installment_per_share": 1000,
        "total_chit_value": 2000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-11-01",
        "installment_due_day": 5
    }, headers=headers)
    chit_id = chit_res.json()["id"]

    # 1. Try marking ready_to_start without full allocation (should block)
    res_ready_fail = await client.post(f"/api/v1/chit-groups/{chit_id}/status", json={"status": "READY_TO_START"}, headers=headers)
    assert res_ready_fail.status_code == 400

    # 2. Allocate both shares
    await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={"member_id": member_id, "share_count": 2}, headers=headers)

    # 3. Mark ready_to_start (should pass now)
    res_ready_pass = await client.post(f"/api/v1/chit-groups/{chit_id}/status", json={"status": "READY_TO_START"}, headers=headers)
    assert res_ready_pass.status_code == 200
    assert res_ready_pass.json()["status"] == "READY_TO_START"

    # 4. Activate chit (should pass)
    res_active = await client.post(f"/api/v1/chit-groups/{chit_id}/status", json={"status": "ACTIVE"}, headers=headers)
    assert res_active.status_code == 200
    assert res_active.json()["status"] == "ACTIVE"

    # 5. Try updating shares while active (should block)
    res_alloc_fail = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships", json={"member_id": member_id, "share_count": 1}, headers=headers)
    assert res_alloc_fail.status_code == 400

@pytest.mark.anyio
async def test_tenant_isolation_chit_groups(client, test_organizer_a, test_organizer_b):
    headers_a = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    headers_b = {"Authorization": f"Bearer {test_organizer_b['token']}"}

    # Organizer A creates group
    res_a = await client.post("/api/v1/chit-groups", json={
        "chit_name": "Organizer A Chit",
        "total_shares": 5,
        "duration_months": 5,
        "monthly_installment_per_share": 1000,
        "total_chit_value": 5000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-11-01",
        "installment_due_day": 5
    }, headers=headers_a)
    chit_id = res_a.json()["id"]

    # Organizer B tries to view Organizer A's group (should 404)
    res_b_view = await client.get(f"/api/v1/chit-groups/{chit_id}", headers=headers_b)
    assert res_b_view.status_code == 404

    # Organizer B tries to update Organizer A's group
    res_b_update = await client.put(f"/api/v1/chit-groups/{chit_id}", json={"chit_name": "Hack"}, headers=headers_b)
    assert res_b_update.status_code == 404


@pytest.mark.anyio
async def test_bulk_allocate_equal_shares(client, db_conn, test_organizer_a, test_organizer_b):
    headers_a = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    headers_b = {"Authorization": f"Bearer {test_organizer_b['token']}"}

    # 1. Create 3 active members under Organizer A
    m1_res = await client.post("/api/v1/members", json={"full_name": "Bulk Mem 1", "mobile": "9812345601"}, headers=headers_a)
    m2_res = await client.post("/api/v1/members", json={"full_name": "Bulk Mem 2", "mobile": "9812345602"}, headers=headers_a)
    m3_res = await client.post("/api/v1/members", json={"full_name": "Bulk Mem 3", "mobile": "9812345603"}, headers=headers_a)
    assert m1_res.status_code == 201
    assert m2_res.status_code == 201
    assert m3_res.status_code == 201
    m1_id = m1_res.json()["id"]
    m2_id = m2_res.json()["id"]
    m3_id = m3_res.json()["id"]

    # 2. Create 1 member under Organizer B (to test tenant leakage checks)
    m_b_res = await client.post("/api/v1/members", json={"full_name": "Org B Mem", "mobile": "9812345609"}, headers=headers_b)
    m_b_id = m_b_res.json()["id"]

    # 3. Create Chit Group under Organizer A with 10 total shares
    chit_res = await client.post("/api/v1/chit-groups", json={
        "chit_name": "Bulk Allocation Test Chit",
        "total_shares": 10,
        "duration_months": 10,
        "monthly_installment_per_share": 2000,
        "total_chit_value": 20000,
        "maintenance_charge": 0,
        "maintenance_charge_type": "FIXED",
        "start_date": "2026-12-01",
        "installment_due_day": 5
    }, headers=headers_a)
    assert chit_res.status_code == 201
    chit_id = chit_res.json()["id"]

    # Test: Verify get_available_members returns existing_shares=0
    avail_res = await client.get(f"/api/v1/chit-groups/{chit_id}/available-members", headers=headers_a)
    assert avail_res.status_code == 200
    avail_members = avail_res.json()
    assert len(avail_members) >= 3
    # Check that m1, m2, m3 have existing_shares = 0
    m1_item = next(x for x in avail_members if x["id"] == m1_id)
    assert m1_item["existing_shares"] == 0

    # 4. Try bulk allocation where total shares requested exceeds total shares (3 members * 4 shares = 12 > 10)
    excess_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m1_id, m2_id, m3_id],
        "share_count_per_member": 4,
        "remarks": "Excess shares test"
    }, headers=headers_a)
    assert excess_res.status_code == 409
    assert "exceed available shares" in excess_res.json()["detail"]

    # 5. Try bulk allocation containing a member of another organizer
    leak_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m1_id, m_b_id],
        "share_count_per_member": 2
    }, headers=headers_a)
    assert leak_res.status_code == 404

    # 6. Try bulk allocation containing a non-existent member ID
    fake_id = "00000000-0000-0000-0000-000000000000"
    fake_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m1_id, fake_id],
        "share_count_per_member": 2
    }, headers=headers_a)
    assert fake_res.status_code == 404

    # 7. Successful bulk allocation of 2 shares each to Member 1 and Member 2 (Total: 4 shares)
    success_res1 = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m1_id, m2_id],
        "share_count_per_member": 2,
        "remarks": "First bulk allocation"
      }, headers=headers_a)
    assert success_res1.status_code == 200
    res1_data = success_res1.json()
    assert res1_data["selected_member_count"] == 2
    assert res1_data["shares_added"] == 4
    assert res1_data["total_allocated_shares"] == 4
    assert res1_data["available_shares"] == 6
    assert res1_data["created_membership_count"] == 2
    assert res1_data["updated_membership_count"] == 0

    # Test: Verify get_available_members now shows existing_shares=2 for m1, m2
    avail_res2 = await client.get(f"/api/v1/chit-groups/{chit_id}/available-members", headers=headers_a)
    assert avail_res2.status_code == 200
    avail_members2 = avail_res2.json()
    m1_item2 = next(x for x in avail_members2 if x["id"] == m1_id)
    m2_item2 = next(x for x in avail_members2 if x["id"] == m2_id)
    m3_item2 = next(x for x in avail_members2 if x["id"] == m3_id)
    assert m1_item2["existing_shares"] == 2
    assert m2_item2["existing_shares"] == 2
    assert m3_item2["existing_shares"] == 0

    # 8. Allocate more shares (mix of new and existing members):
    # Allocating 2 shares each to Member 1 (existing) and Member 3 (new) (Total: 4 shares added)
    success_res2 = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m1_id, m3_id],
        "share_count_per_member": 2,
        "remarks": "Mixed bulk allocation"
    }, headers=headers_a)
    assert success_res2.status_code == 200
    res2_data = success_res2.json()
    assert res2_data["selected_member_count"] == 2
    assert res2_data["shares_added"] == 4
    assert res2_data["total_allocated_shares"] == 8
    assert res2_data["available_shares"] == 2
    assert res2_data["created_membership_count"] == 1
    assert res2_data["updated_membership_count"] == 1

    # Verify that the database memberships match exactly:
    # m1 has 4 shares (2 + 2), m2 has 2 shares, m3 has 2 shares.
    chit_detail = await client.get(f"/api/v1/chit-groups/{chit_id}", headers=headers_a)
    assert chit_detail.status_code == 200
    memberships = chit_detail.json()["memberships"]
    assert len(memberships) == 3
    
    m1_mem = next(x for x in memberships if x["member_id"] == m1_id)
    m2_mem = next(x for x in memberships if x["member_id"] == m2_id)
    m3_mem = next(x for x in memberships if x["member_id"] == m3_id)
    assert m1_mem["share_count"] == 4
    assert m2_mem["share_count"] == 2
    assert m3_mem["share_count"] == 2

    # 9. Verify single activity log with action type BULK_MEMBERS_ALLOCATED
    activity_res = await client.get(f"/api/v1/chit-groups/{chit_id}/activity", headers=headers_a)
    assert activity_res.status_code == 200
    activities = activity_res.json()
    # Check that a log for BULK_MEMBERS_ALLOCATED exists
    bulk_logs = [act for act in activities if act["action_type"] == "BULK_MEMBERS_ALLOCATED"]
    assert len(bulk_logs) == 2 # We did it twice successfully
    
    # 10. Verify status boundary constraint (cannot allocate when status != DRAFT)
    # Transition to READY_TO_START first (allocate the remaining 2 shares to fill the 10 total shares)
    await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m2_id],
        "share_count_per_member": 2
    }, headers=headers_a)
    
    # Transition status
    status_res = await client.post(f"/api/v1/chit-groups/{chit_id}/status", json={"status": "READY_TO_START"}, headers=headers_a)
    assert status_res.status_code == 200
    
    # Try allocating now (should fail with 409 Conflict)
    fail_res = await client.post(f"/api/v1/chit-groups/{chit_id}/memberships/bulk-allocate", json={
        "member_ids": [m3_id],
        "share_count_per_member": 1
    }, headers=headers_a)
    assert fail_res.status_code == 409
    assert "DRAFT" in fail_res.json()["detail"]

