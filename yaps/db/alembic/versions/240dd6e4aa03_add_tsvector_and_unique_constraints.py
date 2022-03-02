"""Add tsvector and unique constraints

Revision ID: 240dd6e4aa03
Revises: b2b7c2c45598
Create Date: 2021-11-20 15:33:56.956267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "240dd6e4aa03"
down_revision = "b2b7c2c45598"
branch_labels = None
depends_on = None


def upgrade():
    # Add a function that returns "tsvector" for text field. It's necessary for FTS.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION make_tsvector(text TEXT)
          RETURNS tsvector AS $$
        BEGIN
          RETURN to_tsvector('russian', text) || to_tsvector('english', text);
        END
        $$ LANGUAGE 'plpgsql' IMMUTABLE;
        """
    )

    # Create GIN index for 'text' columns on 'messages' table - it's special for FTS
    op.create_index(
        op.f("ix__products__text"),
        "products",
        [sa.text("make_tsvector(text)")],
        postgresql_using="gin",
    )

    op.create_unique_constraint(
        op.f("uq__offers__partner_id_product_id"),
        "offers",
        ["partner_id", "product_id"],
    )
    op.create_unique_constraint(op.f("uq__users__email"), "users", ["email"])


def downgrade():
    op.drop_index(op.f("ix__products__text"), table_name="products")
    op.execute("DROP FUNCTION make_tsvector")
    op.drop_constraint(op.f("uq__users__email"), "users", type_="unique")
    op.drop_constraint(
        op.f("uq__offers__partner_id_product_id"), "offers", type_="unique"
    )
