# Use Cases, Bounded Contexts & User Stories

This document outlines the core functional requirements, system boundaries, and user narratives for the Chit Fund Management System.

---

## 1. Use Cases

### Maintainer (Organizer) Use Cases
*   **Create Chit:** Initialize a new chit group with specified duration, values, and maintenance charges.
*   **Add Members:** Enroll approved members into active or draft chit groups.
*   **Conduct Auction:** Open and manage the monthly bidding process.
*   **Record Winner:** Finalize the auction and record the winning member, discount, and calculated bonus.
*   **Record Collections:** Log subscriber payments for each month's installment.
*   **Generate Receipt:** Create digital payment receipts and update the passbook ledger.
*   **View Reports:** Access insights on payments, overdue amounts, and system performance.

### Member (Subscriber) Use Cases
*   **View Passbook:** View personal payment status, due amounts, and dividends per month.
*   **View Payment History:** Access a log of all completed transactions and receipts.
*   **View Bonus History:** See historical dividends earned from previous auctions.
*   **View Winning Details:** Check information regarding past auction winners and discount amounts.

---

## 2. Bounded Contexts

These contexts define the boundaries of each module in the FastAPI backend (`app/` structure).

```text
Authentication Context (auth/)
       |
Member Context (members/)
       |
Chit Context (chits/)
       |
Auction Context (auctions/)
       |
Collection Context (collections/)
       |
Reporting Context (reports/)
```

---

## 3. Core User Stories

### Story 1: Creating a Chit Group
```text
As a Maintainer,
I want to create a chit group,
so that I can manage members.
```

### Story 2: Monthly Auction Management
```text
As a Maintainer,
I want to conduct monthly auctions,
so that I can select the winner.
```

### Story 3: Payment Tracking & Transparency
```text
As a Member,
I want to see my payment history,
so that I can verify collections.
```
