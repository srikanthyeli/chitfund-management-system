CREATE TABLE auctions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chit_group_id UUID NOT NULL REFERENCES chit_groups(id) ON DELETE RESTRICT,
    month_no INTEGER NOT NULL CHECK (month_no > 0),
    winner_member_id UUID REFERENCES members(id) ON DELETE RESTRICT,
    bid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (bid_amount >= 0),
    bonus_per_member DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (bonus_per_member >= 0),
    winner_receivable DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (winner_receivable >= 0),
    auction_date TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Business Constraints
    CONSTRAINT uq_group_month_auction UNIQUE (chit_group_id, month_no),

    -- Standard Audit Columns
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_auctions_group_id ON auctions(chit_group_id);
CREATE INDEX idx_auctions_winner_member_id ON auctions(winner_member_id);
