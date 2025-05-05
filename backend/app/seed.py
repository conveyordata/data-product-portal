from sqlalchemy.orm import Session

from app.authorization.service import AuthorizationService
from app.core.authz import Authorization
from app.database.database import get_db_session


async def seed_db(path: str):
    db: Session = next(get_db_session())

    raw_connection = db.get_bind().raw_connection()
    raw_cursor = raw_connection.cursor()
    raw_cursor.execute(open(path).read())

    raw_connection.commit()
    await Authorization.initialize()
    await AuthorizationService(db).reload_enforcer()
