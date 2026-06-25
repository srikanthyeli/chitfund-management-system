"""phase 4 chit auction management

Revision ID: a1b2c3d4e5f6
Revises: 7930155d9176
Create Date: 2026-06-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7930155d9176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------
    # 1. Create chit_auctions table first (referenced by chit_memberships)
    # -----------------------------------------------------------------
    op.create_table(
        'chit_auctions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organizer_id', sa.UUID(), nullable=False),
        sa.Column('chit_group_id', sa.UUID(), nullable=False),
        sa.Column('auction_month_number', sa.Integer(), nullable=False),
        sa.Column('auction_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='OPEN'),
        sa.Column('gross_chit_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('maintenance_charge', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0'),
        sa.Column('total_discount_amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('maximum_bid_discount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('winner_membership_id', sa.UUID(), nullable=True),
        sa.Column('winner_member_id', sa.UUID(), nullable=True),
        sa.Column('winner_payout_amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('dividend_per_share', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('finalized_at', sa.DateTime(), nullable=True),
        sa.Column('finalized_by_user_id', sa.UUID(), nullable=True),
        # AuditMixin columns
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.UUID(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['chit_group_id'], ['chit_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organizer_id'], ['organizers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['finalized_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
        # winner_membership_id and winner_member_id FKs added AFTER their tables exist
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chit_group_id', 'auction_month_number', name='uq_chit_auctions_group_month'),
        sa.CheckConstraint('gross_chit_amount > 0', name='chk_chit_auctions_gross_amount'),
        sa.CheckConstraint('maintenance_charge >= 0', name='chk_chit_auctions_maintenance_charge'),
        sa.CheckConstraint('auction_month_number >= 1', name='chk_chit_auctions_month_number'),
    )
    op.create_index(op.f('ix_chit_auctions_organizer_id'), 'chit_auctions', ['organizer_id'], unique=False)
    op.create_index(op.f('ix_chit_auctions_chit_group_id'), 'chit_auctions', ['chit_group_id'], unique=False)
    op.create_index(op.f('ix_chit_auctions_status'), 'chit_auctions', ['status'], unique=False)

    # -----------------------------------------------------------------
    # 2. Add winner FK on chit_auctions -> chit_memberships (self-referential via memberships)
    #    (These are nullable; added after chit_memberships exists)
    # -----------------------------------------------------------------
    op.create_foreign_key(
        'fk_chit_auctions_winner_membership',
        'chit_auctions', 'chit_memberships',
        ['winner_membership_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_chit_auctions_winner_member',
        'chit_auctions', 'members',
        ['winner_member_id'], ['id'],
        ondelete='SET NULL'
    )

    # -----------------------------------------------------------------
    # 3. Extend chit_memberships with winner tracking fields
    # -----------------------------------------------------------------
    op.add_column('chit_memberships', sa.Column('has_won_auction', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('chit_memberships', sa.Column('won_auction_id', sa.UUID(), nullable=True))
    op.add_column('chit_memberships', sa.Column('won_month_number', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_chit_memberships_won_auction',
        'chit_memberships', 'chit_auctions',
        ['won_auction_id'], ['id'],
        ondelete='SET NULL'
    )

    # -----------------------------------------------------------------
    # 4. Create chit_auction_bids table
    # -----------------------------------------------------------------
    op.create_table(
        'chit_auction_bids',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organizer_id', sa.UUID(), nullable=False),
        sa.Column('chit_auction_id', sa.UUID(), nullable=False),
        sa.Column('chit_group_id', sa.UUID(), nullable=False),
        sa.Column('membership_id', sa.UUID(), nullable=False),
        sa.Column('member_id', sa.UUID(), nullable=False),
        sa.Column('bid_discount_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('bid_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        # AuditMixin columns
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.UUID(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['chit_auction_id'], ['chit_auctions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chit_group_id'], ['chit_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['chit_memberships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organizer_id'], ['organizers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chit_auction_id', 'membership_id', name='uq_chit_auction_bids_auction_membership'),
        sa.CheckConstraint('bid_discount_amount > 0', name='chk_chit_auction_bids_discount_positive'),
    )
    op.create_index(op.f('ix_chit_auction_bids_organizer_id'), 'chit_auction_bids', ['organizer_id'], unique=False)
    op.create_index(op.f('ix_chit_auction_bids_chit_auction_id'), 'chit_auction_bids', ['chit_auction_id'], unique=False)
    op.create_index(op.f('ix_chit_auction_bids_membership_id'), 'chit_auction_bids', ['membership_id'], unique=False)
    op.create_index(op.f('ix_chit_auction_bids_status'), 'chit_auction_bids', ['status'], unique=False)

    # -----------------------------------------------------------------
    # 5. Create monthly_member_dues table
    # -----------------------------------------------------------------
    op.create_table(
        'monthly_member_dues',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organizer_id', sa.UUID(), nullable=False),
        sa.Column('chit_group_id', sa.UUID(), nullable=False),
        sa.Column('chit_auction_id', sa.UUID(), nullable=False),
        sa.Column('membership_id', sa.UUID(), nullable=False),
        sa.Column('member_id', sa.UUID(), nullable=False),
        sa.Column('month_number', sa.Integer(), nullable=False),
        sa.Column('share_count', sa.Integer(), nullable=False),
        sa.Column('gross_installment_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('dividend_per_share', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('total_dividend_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('net_payable_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('payment_status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        # AuditMixin columns
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.UUID(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['chit_auction_id'], ['chit_auctions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chit_group_id'], ['chit_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['membership_id'], ['chit_memberships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organizer_id'], ['organizers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chit_auction_id', 'membership_id', name='uq_monthly_dues_auction_membership'),
        sa.CheckConstraint('share_count > 0', name='chk_monthly_dues_share_count'),
        sa.CheckConstraint('month_number >= 1', name='chk_monthly_dues_month_number'),
    )
    op.create_index(op.f('ix_monthly_member_dues_organizer_id'), 'monthly_member_dues', ['organizer_id'], unique=False)
    op.create_index(op.f('ix_monthly_member_dues_chit_group_id'), 'monthly_member_dues', ['chit_group_id'], unique=False)
    op.create_index(op.f('ix_monthly_member_dues_chit_auction_id'), 'monthly_member_dues', ['chit_auction_id'], unique=False)
    op.create_index(op.f('ix_monthly_member_dues_membership_id'), 'monthly_member_dues', ['membership_id'], unique=False)
    op.create_index(op.f('ix_monthly_member_dues_payment_status'), 'monthly_member_dues', ['payment_status'], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index(op.f('ix_monthly_member_dues_payment_status'), table_name='monthly_member_dues')
    op.drop_index(op.f('ix_monthly_member_dues_membership_id'), table_name='monthly_member_dues')
    op.drop_index(op.f('ix_monthly_member_dues_chit_auction_id'), table_name='monthly_member_dues')
    op.drop_index(op.f('ix_monthly_member_dues_chit_group_id'), table_name='monthly_member_dues')
    op.drop_index(op.f('ix_monthly_member_dues_organizer_id'), table_name='monthly_member_dues')
    op.drop_table('monthly_member_dues')

    op.drop_index(op.f('ix_chit_auction_bids_status'), table_name='chit_auction_bids')
    op.drop_index(op.f('ix_chit_auction_bids_membership_id'), table_name='chit_auction_bids')
    op.drop_index(op.f('ix_chit_auction_bids_chit_auction_id'), table_name='chit_auction_bids')
    op.drop_index(op.f('ix_chit_auction_bids_organizer_id'), table_name='chit_auction_bids')
    op.drop_table('chit_auction_bids')

    op.drop_constraint('fk_chit_memberships_won_auction', 'chit_memberships', type_='foreignkey')
    op.drop_column('chit_memberships', 'won_month_number')
    op.drop_column('chit_memberships', 'won_auction_id')
    op.drop_column('chit_memberships', 'has_won_auction')

    op.drop_constraint('fk_chit_auctions_winner_member', 'chit_auctions', type_='foreignkey')
    op.drop_constraint('fk_chit_auctions_winner_membership', 'chit_auctions', type_='foreignkey')
    op.drop_index(op.f('ix_chit_auctions_status'), table_name='chit_auctions')
    op.drop_index(op.f('ix_chit_auctions_chit_group_id'), table_name='chit_auctions')
    op.drop_index(op.f('ix_chit_auctions_organizer_id'), table_name='chit_auctions')
    op.drop_table('chit_auctions')
