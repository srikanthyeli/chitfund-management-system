"""rename dividend to bonus

Revision ID: f1e2d3c4b5a6
Revises: bb9536e43d6f
Create Date: 2026-06-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, None] = 'bb9536e43d6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # chit_auctions: dividend_per_share -> bonus_per_share
    op.alter_column('chit_auctions', 'dividend_per_share', new_column_name='bonus_per_share')

    # monthly_member_dues: dividend_per_share -> bonus_per_share, total_dividend_amount -> total_bonus_amount
    op.alter_column('monthly_member_dues', 'dividend_per_share', new_column_name='bonus_per_share')
    op.alter_column('monthly_member_dues', 'total_dividend_amount', new_column_name='total_bonus_amount')


def downgrade() -> None:
    op.alter_column('monthly_member_dues', 'total_bonus_amount', new_column_name='total_dividend_amount')
    op.alter_column('monthly_member_dues', 'bonus_per_share', new_column_name='dividend_per_share')
    op.alter_column('chit_auctions', 'bonus_per_share', new_column_name='dividend_per_share')
