import pytest
import uuid
import json
from datetime import datetime

@pytest.mark.anyio
async def test_create_member_success(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {
        "full_name": "Ramesh Kumar",
        "mobile": "9876543210",
        "alternate_mobile": "9876543211",
        "email": "ramesh@example.com",
        "address": "123 Main St",
        "village": "Gachibowli",
        "mandal": "Serilingampally",
        "district": "Rangareddy",
        "state": "Telangana",
        "pincode": "500032",
        "aadhaar_last4": "1234",
        "notes": "Premium member"
    }

    # 1. Create Member
    response = await client.post("/api/v1/members", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Ramesh Kumar"
    assert data["mobile"] == "9876543210"
    assert data["member_code"] == "MEM00001"
    assert data["organizer_id"] == str(test_organizer_a["organizer_id"])
    assert data["is_active"] is True
    assert "id" in data

    # 2. Check Member exists in DB
    member_id = data["id"]
    member_row = await db_conn.fetchrow("SELECT * FROM members WHERE id = $1", uuid.UUID(member_id))
    assert member_row is not None
    assert member_row["member_code"] == "MEM00001"

    # 3. Check Audit Log
    logs = await db_conn.fetch("SELECT * FROM member_activity_logs WHERE member_id = $1", uuid.UUID(member_id))
    assert len(logs) == 1
    assert logs[0]["action_type"] == "MEMBER_CREATED"
    assert logs[0]["performed_by"] == test_organizer_a["user_id"]
    
    new_vals_log = json.loads(logs[0]["new_values"]) if isinstance(logs[0]["new_values"], str) else logs[0]["new_values"]
    assert "full_name" in new_vals_log

@pytest.mark.anyio
async def test_create_member_invalid_inputs(client, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # Invalid Mobile Format
    payload = {"full_name": "Ramesh Kumar", "mobile": "12345"}
    response = await client.post("/api/v1/members", json=payload, headers=headers)
    assert response.status_code == 400

    # Invalid Alternate Mobile
    payload = {"full_name": "Ramesh Kumar", "mobile": "9876543210", "alternate_mobile": "123"}
    response = await client.post("/api/v1/members", json=payload, headers=headers)
    assert response.status_code == 400

    # Invalid Email format
    payload = {"full_name": "Ramesh Kumar", "mobile": "9876543210", "email": "invalid-email"}
    response = await client.post("/api/v1/members", json=payload, headers=headers)
    assert response.status_code == 422 # Pydantic EmailStr validation triggers 422

    # Invalid Aadhaar Last 4
    payload = {"full_name": "Ramesh Kumar", "mobile": "9876543210", "aadhaar_last4": "12345"}
    response = await client.post("/api/v1/members", json=payload, headers=headers)
    assert response.status_code == 422

@pytest.mark.anyio
async def test_duplicate_mobile_validation(client, test_organizer_a, test_organizer_b):
    # Setup - Organizer A creates member with mobile 9876543210
    headers_a = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {"full_name": "Member A", "mobile": "9876543210"}
    response = await client.post("/api/v1/members", json=payload, headers=headers_a)
    assert response.status_code == 201

    # Organizer A tries to create another member with same mobile (Should block)
    payload2 = {"full_name": "Member A Copy", "mobile": "9876543210"}
    response = await client.post("/api/v1/members", json=payload2, headers=headers_a)
    assert response.status_code == 409
    assert response.json()["detail"] == "A member with this mobile number already exists"

    # Organizer B creates member with SAME mobile (Should allow - tenant isolated duplicates)
    headers_b = {"Authorization": f"Bearer {test_organizer_b['token']}"}
    payload_b = {"full_name": "Member B", "mobile": "9876543210"}
    response = await client.post("/api/v1/members", json=payload_b, headers=headers_b)
    assert response.status_code == 201

@pytest.mark.anyio
async def test_update_member_profile(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    payload = {"full_name": "Initial Name", "mobile": "9876543210", "notes": "initial note"}
    create_res = await client.post("/api/v1/members", json=payload, headers=headers)
    member_id = create_res.json()["id"]

    # Clear activity logs for testing clean update logs
    await db_conn.execute("DELETE FROM member_activity_logs WHERE member_id = $1", uuid.UUID(member_id))

    # Update member details (exclude mobile)
    update_payload = {"full_name": "Updated Name", "notes": "updated note"}
    update_res = await client.put(f"/api/v1/members/{member_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["full_name"] == "Updated Name"
    assert data["notes"] == "updated note"

    # Verify audit logs
    logs = await db_conn.fetch("SELECT * FROM member_activity_logs WHERE member_id = $1 ORDER BY created_at DESC", uuid.UUID(member_id))
    assert len(logs) == 1
    assert logs[0]["action_type"] == "MEMBER_UPDATED"
    
    old_vals_log = json.loads(logs[0]["old_values"]) if isinstance(logs[0]["old_values"], str) else logs[0]["old_values"]
    new_vals_log = json.loads(logs[0]["new_values"]) if isinstance(logs[0]["new_values"], str) else logs[0]["new_values"]
    
    assert old_vals_log == {"full_name": "Initial Name", "notes": "initial note"}
    assert new_vals_log == {"full_name": "Updated Name", "notes": "updated note"}

@pytest.mark.anyio
async def test_update_member_mobile_endpoint(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    create_res = await client.post("/api/v1/members", json={"full_name": "Test Mobile", "mobile": "9876543210"}, headers=headers)
    member_id = create_res.json()["id"]

    # Update mobile number successfully
    mobile_payload = {
        "old_mobile": "9876543210",
        "new_mobile": "9988776655",
        "confirm_new_mobile": "9988776655"
    }
    res = await client.patch(f"/api/v1/members/{member_id}/mobile", json=mobile_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["mobile"] == "9988776655"

    # Try updating again with wrong old mobile
    wrong_payload = {
        "old_mobile": "1234567890",
        "new_mobile": "9999999999",
        "confirm_new_mobile": "9999999999"
    }
    res = await client.patch(f"/api/v1/members/{member_id}/mobile", json=wrong_payload, headers=headers)
    assert res.status_code == 400

@pytest.mark.anyio
async def test_update_member_status(client, db_conn, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    create_res = await client.post("/api/v1/members", json={"full_name": "Status Guy", "mobile": "9876543210"}, headers=headers)
    member_id = create_res.json()["id"]

    # Deactivate Member
    status_payload = {"is_active": False, "remarks": "Left city"}
    res = await client.patch(f"/api/v1/members/{member_id}/status", json=status_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["is_active"] is False

    # Check Audit Log
    logs = await db_conn.fetch("SELECT * FROM member_activity_logs WHERE member_id = $1 ORDER BY created_at DESC", uuid.UUID(member_id))
    assert logs[0]["action_type"] == "MEMBER_DEACTIVATED"
    assert logs[0]["remarks"] == "Left city"

@pytest.mark.anyio
async def test_list_members_search_and_pagination(client, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # Onboard three members
    await client.post("/api/v1/members", json={"full_name": "Alice Smith", "mobile": "9000000001", "village": "Greenfield"}, headers=headers)
    await client.post("/api/v1/members", json={"full_name": "Bob Jones", "mobile": "9000000002", "village": "Lakeview"}, headers=headers)
    await client.post("/api/v1/members", json={"full_name": "Charlie Brown", "mobile": "9000000003", "village": "Lakeview"}, headers=headers)

    # Test list search by name
    res = await client.get("/api/v1/members?search=Alice", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["full_name"] == "Alice Smith"

    # Test list filter by active
    res = await client.get("/api/v1/members?is_active=true", headers=headers)
    assert len(res.json()["items"]) >= 3

@pytest.mark.anyio
async def test_tenant_isolation_member_management(client, test_organizer_a, test_organizer_b):
    # Organizer A creates a member
    headers_a = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    create_res = await client.post("/api/v1/members", json={"full_name": "Secret Member", "mobile": "9876543210"}, headers=headers_a)
    member_id = create_res.json()["id"]

    # Organizer B attempts to retrieve Organizer A's member (Should 404/403)
    headers_b = {"Authorization": f"Bearer {test_organizer_b['token']}"}
    res = await client.get(f"/api/v1/members/{member_id}", headers=headers_b)
    assert res.status_code == 404

    # Organizer B attempts to update Organizer A's member
    res = await client.put(f"/api/v1/members/{member_id}", json={"full_name": "Hack Name"}, headers=headers_b)
    assert res.status_code == 404

    # Organizer B attempts to update status of Organizer A's member
    res = await client.patch(f"/api/v1/members/{member_id}/status", json={"is_active": False}, headers=headers_b)
    assert res.status_code == 404

@pytest.mark.anyio
async def test_member_summary(client, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # Create 2 active, 1 inactive
    res1 = await client.post("/api/v1/members", json={"full_name": "Active 1", "mobile": "9000000011"}, headers=headers)
    id1 = res1.json()["id"]
    await client.post("/api/v1/members", json={"full_name": "Active 2", "mobile": "9000000012"}, headers=headers)
    res3 = await client.post("/api/v1/members", json={"full_name": "Inactive 1", "mobile": "9000000013"}, headers=headers)
    id3 = res3.json()["id"]
    
    # Deactivate the 3rd member
    await client.patch(f"/api/v1/members/{id3}/status", json={"is_active": False}, headers=headers)

    # Get summary
    res_summary = await client.get("/api/v1/members/summary", headers=headers)
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_members"] == 3
    assert summary["active_members"] == 2
    assert summary["inactive_members"] == 1
    assert summary["new_members_this_month"] == 3

@pytest.mark.anyio
async def test_dashboard_summary_integration(client, test_organizer_a):
    headers = {"Authorization": f"Bearer {test_organizer_a['token']}"}
    
    # Create member
    await client.post("/api/v1/members", json={"full_name": "Dash Member", "mobile": "9876543210"}, headers=headers)

    # Fetch dashboard summary
    res = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert res.status_code == 200
    assert res.json()["total_members"] == 1
