CREATE TABLE chit_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chit_group_id UUID NOT NULL REFERENCES chit_groups(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    join_date TIMESTAMP NOT NULL DEFAULT NOW(),
    position_no INTEGER NOT NULL CHECK (position_no > 0),
    won_status BOOLEAN NOT NULL DEFAULT FALSE,

    -- Business Constraints
    CONSTRAINT uq_chit_group_member UNIQUE (chit_group_id, member_id),
    CONSTRAINT uq_chit_group_position UNIQUE (chit_group_id, position_no),

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

CREATE INDEX idx_chit_memberships_group_id ON chit_memberships(chit_group_id);
CREATE INDEX idx_chit_memberships_member_id ON chit_memberships(member_id);
