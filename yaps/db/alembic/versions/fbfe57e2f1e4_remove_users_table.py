"""Remove Users table

Revision ID: fbfe57e2f1e4
Revises: f40bb5ee0b2a
Create Date: 2021-11-22 15:01:46.086797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fbfe57e2f1e4"
down_revision = "f40bb5ee0b2a"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    conn.execute(
        """
        ALTER TABLE personal_offers
        ADD COLUMN user_email TEXT NOT NULL DEFAULT ''
    """
    )

    conn.execute(
        """
        UPDATE personal_offers po
            SET user_email =
            CASE
                WHEN (po.user_id = 1) THEN 'test@yandex.ru'
                WHEN (po.user_id = 2) THEN 'nekomanda@yandex.ru'
            END
    """
    )

    conn.execute(
        """
        ALTER TABLE personal_offers
        ALTER COLUMN user_email DROP DEFAULT,
        DROP user_id;
    """
    )

    conn.execute("DROP TABLE users")


def downgrade():
    """
    Если придется откатить - можно будет просто накатить дамп базы
    """
    pass
