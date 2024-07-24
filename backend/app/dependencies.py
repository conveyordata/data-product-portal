from fastapi import Depends, HTTPException, status

from app.core.auth.auth import get_authenticated_user
from app.users.schema import User


async def only_for_admin(authenticated_user: User = Depends(get_authenticated_user)):
    if not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can execute this operation",
        )
