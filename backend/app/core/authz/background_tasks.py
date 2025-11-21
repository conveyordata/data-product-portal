import asyncio

from sqlalchemy import func, select

from app.core.authz.authorization import Authorization
from app.core.logging import logger
from app.database.database import SessionLocal
from app.users.model import User as UserModel

CHECK_INTERVAL_SECONDS = 60  # run every minute


async def check_expired_admins() -> None:
    authorizer = Authorization()
    while True:
        try:
            with SessionLocal() as db:
                # query admin roles with expiry in the past
                expired = (
                    db.execute(
                        select(UserModel)
                        .where(UserModel.admin_expiry.isnot(None))
                        .where(UserModel.admin_expiry <= func.now())
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

        except Exception as e:
            # don't crash the loop if something fails
            logger.warning(f"[Auth] Expiry check failed: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
