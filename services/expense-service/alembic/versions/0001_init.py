from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        'expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(12,2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=False),
        sa.Column('merchant', sa.String(length=128), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_table(
        'idempotency_keys',
        sa.Column('key', sa.String(length=128), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('month_yr', sa.String(length=7), nullable=False),
        sa.Column('spent', sa.Numeric(14,2), nullable=False, server_default="0"),
        sa.Column('version', sa.Integer, nullable=False, server_default="1"),
    )
    op.create_unique_constraint("uq_budget_user_month", "budgets", ["user_id","month_yr"])

def downgrade() -> None:
    op.drop_table('budgets')
    op.drop_table('idempotency_keys')
    op.drop_table('expenses')
