from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import composite, registry

from prodik.domain.fraud import FraudRule
from prodik.domain.transaction import (
    Transaction,
    TransactionChannel,
    TransactionLocation,
    TransactionStatus,
)
from prodik.domain.user import Gender, MaritalStatus, Role, User, UserCredentials

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

user_account_table = Table(
    "user_account",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("email", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("role", Enum(Role), nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("region", String),
    Column("gender", Enum(Gender)),
    Column("age", Integer),
    Column("marital_status", Enum(MaritalStatus)),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)


user_credentials_table = Table(
    "user_credentials",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
)


fraud_rule_table = Table(
    "fraud_rule_table",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("name", String, nullable=False),
    Column("description", String),
    Column("dsl_expression", String, nullable=False),
    Column("enabled", Boolean, nullable=False),
    Column("priority", Integer, nullable=False, default=1),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)

transaction_table = Table(
    "transaction_table",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
    Column("amount", Float, nullable=False),
    Column("currency_code", String, nullable=False),
    Column("status", Enum(TransactionStatus), nullable=False),
    Column("merchant_id", String),
    Column("merchant_category_code", String),
    Column("timestamp", String),
    Column("ip_address", String),
    Column("device_id", String),
    Column("channel", Enum(TransactionChannel)),
    Column("location_country", String),
    Column("location_city", String),
    Column("location_latitude", Float),
    Column("location_longitude", Float),
    Column("metadata", JSON),
    Column("is_fraud", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True)),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(FraudRule, fraud_rule_table)
    registry_mapper.map_imperatively(User, user_account_table)
    registry_mapper.map_imperatively(UserCredentials, user_credentials_table)
    registry_mapper.map_imperatively(
        Transaction,
        transaction_table,
        properties={
            "location": composite(
                TransactionLocation,
                transaction_table.c.location_country,
                transaction_table.c.location_city,
                transaction_table.c.location_latitude,
                transaction_table.c.location_longitude,
            ),
        },
    )
