CREATE TABLE chit_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organizer_id UUID NOT NULL REFERENCES organizers(id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL,
    duration_months INTEGER NOT NULL CHECK (duration_months > 0),
    member_count INTEGER NOT NULL DEFAULT 0 CHECK (member_count >= 0),
    monthly_amount DECIMAL(12, 2) NOT NULL CHECK (monthly_amount > 0),
    maintenance_charge DECIMAL(12, 2) NOT NULL CHECK (maintenance_charge >= 0),
    start_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'ACTIVE', 'COMPLETED')),

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

CREATE INDEX idx_chit_groups_organizer_id ON chit_groups(organizer_id);
CREATE INDEX idx_chit_groups_status ON chit_groups(status);
