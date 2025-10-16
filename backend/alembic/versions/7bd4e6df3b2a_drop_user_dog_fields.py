"""
Revision ID: 7bd4e6df3b2a
Revises: c5ff936cc90c
Create Date: 2025-10-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bd4e6df3b2a'
down_revision = 'c5ff936cc90c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('users') as batch_op:
        try:
            batch_op.drop_column('dog_name')
        except Exception:
            pass
        try:
            batch_op.drop_column('dog_photo_url')
        except Exception:
            pass


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        try:
            batch_op.add_column(sa.Column('dog_name', sa.String(length=100), nullable=True))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('dog_photo_url', sa.Text(), nullable=True))
        except Exception:
            pass
