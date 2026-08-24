import asyncio
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import text

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.core.authz.watcher import (
    CHANNEL,
    listen_for_policy_changes,
    notify_policy_update,
)
from app.database.database import engine


class TestNotifyPolicyUpdate:
    def test_executes_notify_and_commits(self):
        mock_conn = MagicMock()
        mock_ctx = MagicMock(
            __enter__=MagicMock(return_value=mock_conn),
            __exit__=MagicMock(return_value=False),
        )

        with patch("app.core.authz.watcher.engine") as mock_engine:
            mock_engine.connect.return_value = mock_ctx
            notify_policy_update()

        mock_conn.execute.assert_called_once()
        sql = str(mock_conn.execute.call_args[0][0])
        assert "NOTIFY" in sql
        assert CHANNEL in sql
        mock_conn.commit.assert_called_once()

    def test_swallows_exceptions(self):
        with patch("app.core.authz.watcher.engine") as mock_engine:
            mock_engine.connect.side_effect = RuntimeError("db down")
            notify_policy_update()  # must not raise


class TestListenForPolicyChanges:
    def _run_task(self, coro):
        async def runner():
            task = asyncio.create_task(coro)
            await asyncio.sleep(0)
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            return task

        return asyncio.run(runner())

    def test_adds_listener_on_correct_channel(self):
        mock_conn = AsyncMock()

        with patch("app.core.authz.watcher.asyncpg.connect", return_value=mock_conn):
            self._run_task(listen_for_policy_changes(MagicMock()))

        mock_conn.add_listener.assert_called_once()
        assert mock_conn.add_listener.call_args[0][0] == CHANNEL

    def test_closes_connection_on_cancel(self):
        mock_conn = AsyncMock()

        with patch("app.core.authz.watcher.asyncpg.connect", return_value=mock_conn):
            self._run_task(listen_for_policy_changes(MagicMock()))

        mock_conn.close.assert_called_once()

    def test_reconnects_after_connection_error(self):
        mock_connect = AsyncMock(side_effect=OSError("connection refused"))

        async def runner():
            task = asyncio.create_task(listen_for_policy_changes(MagicMock()))
            await asyncio.sleep(0)  # let task attempt connect, fail, and enter sleep(5)
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            return task

        with patch("app.core.authz.watcher.asyncpg.connect", mock_connect):
            task = asyncio.run(runner())

        mock_connect.assert_called_once()
        assert task.cancelled()

    def test_on_change_called_when_notification_received(self):
        on_change = MagicMock()
        captured_cb = []
        mock_conn = AsyncMock()

        async def capture_listener(channel, cb):
            captured_cb.append(cb)

        mock_conn.add_listener.side_effect = capture_listener

        async def runner():
            task = asyncio.create_task(listen_for_policy_changes(on_change))
            await asyncio.sleep(0)  # let task reach add_listener
            assert captured_cb, "listener callback was not registered"
            await captured_cb[0](mock_conn, 0, CHANNEL, "")
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

        with patch("app.core.authz.watcher.asyncpg.connect", return_value=mock_conn):
            asyncio.run(runner())
        on_change.assert_called_once()


class TestAuthorizationReloadPolicy:
    def test_reload_policy__resolves_stale_in_memory(self, authorizer: Authorization):
        """Proves the original bug: a role assigned by another worker is invisible
        until reload_policy() is called."""
        role = "staleness_test_role"
        user = "staleness_test_user"
        resource = "staleness_test_resource"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[action])
        assert (
            authorizer.has_access(sub=user, dom="*", obj=resource, act=action) is False
        )

        # Another worker writes the grouping policy directly to the DB
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO casbin_rule (ptype, v0, v1, v2) VALUES ('g', :u, :r, :obj)"
                ),
                {"u": user, "r": role, "obj": resource},
            )
            conn.commit()

        # In-memory is still stale: access denied despite the DB having the assignment
        authorizer._cache.clear()
        assert (
            authorizer.has_access(sub=user, dom="*", obj=resource, act=action) is False
        )

        # reload_policy() reads from DB: access is now correctly granted
        authorizer.reload_policy()
        assert (
            authorizer.has_access(sub=user, dom="*", obj=resource, act=action) is True
        )

        # Cleanup
        with engine.connect() as conn:
            conn.execute(
                text(
                    "DELETE FROM casbin_rule WHERE ptype='g' AND v0=:u AND v1=:r AND v2=:obj"
                ),
                {"u": user, "r": role, "obj": resource},
            )
            conn.commit()
        authorizer.remove_role_permissions(role_id=role)

    def test_reload_policy_loads_and_clears_cache(self, authorizer: Authorization):
        authorizer._cache["sentinel"] = True

        with patch.object(authorizer._enforcer, "load_policy") as mock_load:
            authorizer.reload_policy()

        mock_load.assert_called_once()
        assert len(authorizer._cache) == 0

    def test_after_update_calls_notify(self, authorizer: Authorization):
        with patch("app.core.authz.authorization.notify_policy_update") as mock_notify:
            authorizer._after_update()

        mock_notify.assert_called_once()
