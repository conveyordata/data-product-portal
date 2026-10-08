from app.groups.model import GroupMembership


def group_has_member(session, group_id, member_identity_id) -> bool:
    return (
        session.get(
            GroupMembership,
            (group_id, member_identity_id),
        )
        is not None
    )
