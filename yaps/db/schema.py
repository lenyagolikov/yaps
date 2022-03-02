from sqlalchemy import (
    Column,
    ForeignKey,
    MetaData,
    String,
    Table,
    Integer,
    Identity,
    Numeric,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import ARRAY

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    # Именование индексов
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    # Именование уникальных индексов
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    # Именование CHECK-constraint-ов
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    # Именование внешних ключей
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    # Именование первичных ключей
    "pk": "pk__%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

personal_offers_table = Table(
    "personal_offers",
    metadata,
    Column(
        "user_email",
        String,
        primary_key=True,
    ),
    Column(
        "offer_id",
        Integer,
        ForeignKey("offers.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("price", Numeric(10, 2), nullable=False),
    Column("cashback_percent", Numeric(10, 2), nullable=True),
    Column("cashback_amount", Numeric(10, 2), nullable=True),
)

products_table = Table(
    "products",
    metadata,
    Column("id", Integer, Identity(start=1), primary_key=True),
    Column("name", String(500), nullable=False),
    Column("description", String(500), nullable=False),
    Column("text", Text, nullable=False),
    Column("images", ARRAY(String(500)), nullable=False),
    Column("props", JSON, nullable=False),
)

partners_table = Table(
    "partners",
    metadata,
    Column("id", Integer, Identity(start=1), primary_key=True),
    Column("name", String(500), nullable=False),
    Column("link", Text, nullable=False),
)

offers_table = Table(
    "offers",
    metadata,
    Column("id", Integer, Identity(start=1), primary_key=True),
    Column(
        "partner_id",
        Integer,
        ForeignKey("partners.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("price", Numeric(10, 2), nullable=False),
    Column("old_price", Numeric(10, 2), nullable=True),
    Column("cashback_percent", Numeric(10, 2), nullable=True),
    Column("cashback_amount", Numeric(10, 2), nullable=True),
    UniqueConstraint("partner_id", "product_id"),
)
