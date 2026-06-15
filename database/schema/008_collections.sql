CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_id UUID NOT NULL REFERENCES auctions(id) ON DELETE RESTRICT,
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    payable_amount DECIMAL(12, 2) NOT NULL CHECK (payable_amount >= 0),
    paid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0),
    penalty_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (penalty_amount >= 0),
    payment_date TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'UNPAID' CHECK (status IN ('UNPAID', 'PAID', 'PENALTY_DUE')),

    -- Business Constraints
    CONSTRAINT uq_auction_member_collection UNIQUE (auction_id, member_id),

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

CREATE INDEX idx_collections_auction_id ON collections(auction_id);
CREATE INDEX idx_collections_member_id ON collections(member_id);
CREATE INDEX idx_collections_status ON collections(status);
