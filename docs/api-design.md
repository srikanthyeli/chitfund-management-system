# REST API Design Specification

This document details the REST API endpoints, request payloads, response structures, and HTTP status codes for the **Chit Fund Management System** backend.

---

## 1. Base URL & Authentication

*   **Base URL:** `/api/v1`
*   **Authentication:** Bearer Token (JWT issued after successful OTP verification).
*   **Headers:**
    *   `Content-Type: application/json`
    *   `Authorization: Bearer <JWT_TOKEN>`

---

## 2. API Endpoints

### 2.1 Authentication & Onboarding

#### `POST /auth/send-otp`
Sends a 6-digit verification code to the subscriber's phone number.
*   **Request Body:**
    ```json
    {
      "phone_number": "+919876543210"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "message": "OTP sent successfully",
      "session_id": "c30f40d7-21a4-4ea8-b2ad-5b23e20e8b4e"
    }
    ```

#### `POST /auth/verify-otp`
Verifies the OTP and issues a JWT access token.
*   **Request Body:**
    ```json
    {
      "session_id": "c30f40d7-21a4-4ea8-b2ad-5b23e20e8b4e",
      "otp_code": "123456"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer",
      "user": {
        "id": "e0a133b3-8a3c-44e2-a720-7f2a1b1d3d63",
        "phone_number": "+919876543210",
        "role": "subscriber"
      }
    }
    ```

---

### 2.2 Profiles & KYC

#### `GET /profile`
Retrieves the logged-in user's profile and KYC details.
*   **Response (200 OK):**
    ```json
    {
      "id": "e0a133b3-8a3c-44e2-a720-7f2a1b1d3d63",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "pan_number": "ABCDE1234F",
      "aadhaar_number": "123456789012",
      "kyc_status": "approved",
      "bank_details": {
        "bank_name": "State Bank of India",
        "account_no": "100023456789",
        "ifsc": "SBIN0001234"
      }
    }
    ```

#### `PUT /profile`
Updates subscriber profile and submits files for KYC.
*   **Request Body:**
    ```json
    {
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "pan_number": "ABCDE1234F",
      "aadhaar_number": "123456789012",
      "bank_name": "State Bank of India",
      "account_no": "100023456789",
      "ifsc": "SBIN0001234"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "message": "Profile updated successfully, KYC set to pending verification."
    }
    ```

---

### 2.3 Chit Groups & Schemes

#### `GET /groups`
Lists all chit groups the user is registered in (or available groups for enrollment if user is an admin).
*   **Response (200 OK):**
    ```json
    [
      {
        "id": "a90bb62f-cfd8-4f2f-8700-1cfa91176b6d",
        "group_code": "GRP-2026A-01",
        "scheme_name": "Kalyan ₹10k 50-Month",
        "chit_value": 500000.00,
        "duration_months": 50,
        "current_installment": 3,
        "status": "active",
        "is_member": true,
        "is_prized": false
      }
    ]
    ```

#### `GET /groups/{group_id}`
Retrieves details of a specific chit group including active member lists.
*   **Response (200 OK):**
    ```json
    {
      "id": "a90bb62f-cfd8-4f2f-8700-1cfa91176b6d",
      "group_code": "GRP-2026A-01",
      "status": "active",
      "chit_value": 500000.00,
      "installment_count": 50,
      "current_installment": 3,
      "start_date": "2026-04-15",
      "members": [
        { "user_id": "e0a133...", "full_name": "John Doe", "is_prized": false },
        { "user_id": "b0a244...", "full_name": "Jane Smith", "is_prized": true, "prized_installment": 2 }
      ]
    }
    ```

---

### 2.4 Auctions & Live Bidding

#### `GET /groups/{group_id}/auctions/active`
Checks if there is an active auction today and returns its details.
*   **Response (200 OK):**
    ```json
    {
      "id": "f56b784a-7bc9-4da9-9c12-32a2f9b23b3f",
      "group_id": "a90bb62f-cfd8-4f2f-8700-1cfa91176b6d",
      "installment_no": 3,
      "status": "ongoing",
      "scheduled_at": "2026-06-15T15:00:00Z",
      "min_discount": 25000.00,
      "max_discount": 200000.00,
      "current_highest_discount": 75000.00,
      "time_remaining_seconds": 1850
    }
    ```

#### `POST /auctions/{auction_id}/bids`
Places a discount bid during an active auction.
*   **Request Body:**
    ```json
    {
      "bid_discount": 80000.00
    }
    ```
*   **Response (201 Created):**
    ```json
    {
      "id": "d12e848d-df98-468e-ad72-9a0db28cfbf8",
      "auction_id": "f56b784a-7bc9-4da9-9c12-32a2f9b23b3f",
      "user_id": "e0a133b3-8a3c-44e2-a720-7f2a1b1d3d63",
      "bid_discount": 80000.00,
      "created_at": "2026-06-15T15:20:12Z"
    }
    ```

#### `GET /auctions/{auction_id}/bids`
Fetch bid history of an ongoing or completed auction.
*   **Response (200 OK):**
    ```json
    [
      { "bid_discount": 80000.00, "user_id": "e0a133...", "created_at": "2026-06-15T15:20:12Z" },
      { "bid_discount": 75000.00, "user_id": "d4e211...", "created_at": "2026-06-15T15:15:30Z" }
    ]
    ```

---

### 2.5 Payments & Passbook

#### `GET /groups/{group_id}/passbook`
Retrieves the member's digital passbook entries for a specific group.
*   **Response (200 OK):**
    ```json
    [
      {
        "installment_no": 1,
        "amount_due": 10000.00,
        "dividend_earned": 0.00,
        "penalty_applied": 0.00,
        "amount_paid": 10000.00,
        "status": "paid",
        "updated_at": "2026-04-10T11:30:00Z"
      },
      {
        "installment_no": 2,
        "amount_due": 10000.00,
        "dividend_earned": 3000.00,
        "penalty_applied": 0.00,
        "amount_paid": 7000.00,
        "status": "paid",
        "updated_at": "2026-05-09T14:15:00Z"
      },
      {
        "installment_no": 3,
        "amount_due": 10000.00,
        "dividend_earned": 2500.00,
        "penalty_applied": 50.00,
        "amount_paid": 0.00,
        "status": "unpaid",
        "updated_at": "2026-06-15T22:42:00Z"
      }
    ]
    ```

#### `POST /payments/checkout`
Initiates an online payment transaction for an installment.
*   **Request Body:**
    ```json
    {
      "group_id": "a90bb62f-cfd8-4f2f-8700-1cfa91176b6d",
      "installment_no": 3
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "transaction_id": "t89a31bc-7d31-419b-a320-f1c7d23d8c11",
      "amount": 7550.00,
      "payment_url": "https://api.paymentgateway.com/checkout?token=tok_123456"
    }
    ```

#### `POST /payments/webhook`
Webhook called by payment gateway to verify payment success.
*   **Request Body:**
    ```json
    {
      "transaction_id": "t89a31bc-7d31-419b-a320-f1c7d23d8c11",
      "status": "success",
      "gateway_reference": "pay_9812739218"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "status": "updated",
      "passbook_status": "paid"
    }
    ```

---

### 2.6 Dashboard & Reports (Foreman Only)

#### `GET /admin/dashboard/overview`
Aggregated indicators for the foreman portal.
*   **Response (200 OK):**
    ```json
    {
      "total_active_groups": 12,
      "total_active_subscribers": 600,
      "collection_efficiency_percentage": 98.4,
      "total_dues_outstanding": 45000.00,
      "total_foreman_commission_mtd": 125000.00
    }
    ```
