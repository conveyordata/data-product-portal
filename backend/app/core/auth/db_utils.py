import uuid

from sqlalchemy import func, select
from sqlalchemy.sql.visitors import iterate

from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID


def is_user_admin(user_id: uuid.UUID):
    from app.users.model import User

    return (
        select(User.id)
        .where(User.id == user_id)
        .where(User.admin_expiry > func.now())
        .exists()
    )


def is_system_account(user_id: uuid.UUID):
    from app.users.model import User

    return (
        select(User.id)
        .where(User.id == user_id)
        .where(User.external_id == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
        .exists()
    )


def statement_references_model(statement, model) -> bool:
    """Checks if a SQLAlchemy statement references a specific model's table."""
    try:
        selected_columns = list(statement.selected_columns)
    except Exception:
        selected_columns = []

    if not selected_columns:
        return False

    for selected in selected_columns:
        for node in iterate(selected, {}):
            if getattr(node, "table", None) is model.__table__:
                return True

    return False
