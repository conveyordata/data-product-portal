import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authz.authorization import Authorization
from app.core.logging import logger
from app.database.database import SessionLocal
from app.users.model import User as UserModel

CHECK_INTERVAL_SECONDS = 60  # run every minute


async def revoke_expired_admins(db: Session) -> None:
    authorizer = Authorization()
    expired = (
        db.execute(
            select(UserModel)
            .where(UserModel.admin_expiry.isnot(None))
            .where(UserModel.admin_expiry <= datetime.now(timezone.utc))
        )
        .scalars()
        .all()
    )

    if expired:
        for user in expired:
            authorizer.revoke_admin_role(user_id=user.id)
            user.admin_expiry = None  # clear expiry

        db.commit()
        logger.info(f"[Auth] Revoked {len(expired)} expired admin role(s)")


async def check_expired_admins() -> None:
    while True:
        try:
            with SessionLocal() as db:
                await revoke_expired_admins(db)
        except Exception as e:
            # don't crash the loop if something fails
            logger.warning(f"[Auth] Expiry check failed: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
