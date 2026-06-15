# Domain Entities

This document defines the schema models and attributes for all core domain tables.

---

### Organizer
**Purpose:**
Manage chit groups and collections.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `name`: Organizer's full name.
*   `mobile`: Contact phone number.

---

### ChitGroup
**Purpose:**
Represents one chit scheme.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `organizer_id`: Foreign key reference to Organizer.
*   `name`: Name/code of the chit group.
*   `duration_months`: Total duration (number of installments).
*   `member_count`: Current total enrolled members.
*   `monthly_amount`: Base installment amount per month.
*   `maintenance_charge`: Fee kept by organizer (commission).
*   `start_date`: Date the chit group begins operations.
*   `status`: Current state (draft, active, completed).

---

### Member
**Purpose:**
Participate in chit.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `name`: Member's full name.
*   `mobile`: Mobile phone number.
*   `address`: Home/postal address.
*   `status`: Status of the member (active, inactive).

---

### ChitMembership
**Purpose:**
Association table linking members to specific chit groups.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `chit_group_id`: Foreign key reference to ChitGroup.
*   `member_id`: Foreign key reference to Member.
*   `join_date`: Date the member joined this group.
*   `position_no`: Fixed seat/position number (1 to N) assigned in the group.
*   `won_status`: Boolean flag indicating if this member has already won an auction.

---

### Auction
**Purpose:**
Monthly bidding process.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `chit_group_id`: Foreign key reference to ChitGroup.
*   `month_no`: Month index of the auction (e.g. 1, 2, ...).
*   `winner_member_id`: Foreign key reference to Member (the winning bidder).
*   `bid_amount`: Winning discount amount.
*   `bonus_per_member`: Shared dividend distributed to each member: `(bid_amount - maintenance_charge) / total_members`.
*   `winner_receivable`: Final payout for the winner: `monthly_amount * total_members - maintenance_charge - bid_amount`.
*   `auction_date`: Timestamp when the auction was held.

---

### Bid
**Purpose:**
Individual bids placed during an auction.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `auction_id`: Foreign key reference to Auction.
*   `member_id`: Foreign key reference to Member.
*   `bid_amount`: Discount amount bid.

---

### Collection
**Purpose:**
Monthly payment tracking.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `auction_id`: Foreign key reference to Auction.
*   `member_id`: Foreign key reference to Member.
*   `payable_amount`: Net subscription due: `monthly_amount - bonus_amount`.
*   `paid_amount`: Total amount paid by the member.
*   `penalty_amount`: Applied interest or late fees.
*   `payment_date`: Timestamp when payment was completed.
*   `status`: Status of the collection (unpaid, paid, penalty_due).

---

### PassbookEntry
**Purpose:**
Receipt ledger record for member's passbook.

**Attributes:**
*   `id`: Unique identifier (UUID).
*   `collection_id`: Foreign key reference to Collection.
*   `member_id`: Foreign key reference to Member.
*   `month_no`: Installment month number.
*   `installment`: Base installment amount.
*   `bonus`: Dividend/bonus credited.
*   `payable`: Net amount paid/due.
*   `entry_date`: Timestamp of ledger entry creation.
