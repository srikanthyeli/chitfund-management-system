CREATE TABLE passbook_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID UNIQUE NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    month_no INTEGER NOT NULL CHECK (month_no > 0),
    installment DECIMAL(12, 2) NOT NULL CHECK (installment >= 0),
    bonus DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (bonus >= 0),
    payable DECIMAL(12, 2) NOT NULL CHECK (payable >= 0),
    entry_date TIMESTAMP NOT NULL DEFAULT NOW(),

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

CREATE INDEX idx_passbook_entries_collection_id ON passbook_entries(collection_id);
CREATE INDEX idx_passbook_entries_member_id ON passbook_entries(member_id);
