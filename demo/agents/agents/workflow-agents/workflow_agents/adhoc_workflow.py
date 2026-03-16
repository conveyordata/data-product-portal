"""Ad-hoc question workflow.

A user asks a data question, the system identifies relevant output ports,
creates an ephemeral data product as an access record (audit trail), then
delegates the answer to the data-agents container via A2A (HTTP call).
"""

from __future__ import annotations

import os

import httpx

from agno.db.sqlite import SqliteDb
from agno.workflow import Condition, Step, StepInput, StepOutput, Workflow

from workflow_agents.helpers import _format_ports_list, _parse_user_selection
from workflow_agents.portal_client import PortalClient

_AGENT_DATA_DIR = os.environ.get("AGENT_DATA_DIR", "/agent_data")
_PORTAL_URL = os.environ.get("PORTAL_URL", "http://localhost:8080")
_DATA_AGENTS_URL = os.environ.get("DATA_AGENTS_URL", "http://data-agents:7070")

# ---------------------------------------------------------------------------
# Session state keys:
#   question            : str   — original question
#   candidate_ports     : list  — from Portal search
#   presented_ports     : list  — filtered candidate list shown to user
#   selected_port_ids   : list  — confirmed by user
#   restricted_ids      : list  — ports needing human approval
#   ephemeral_dp_id     : str
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Step 1: identify_ports
# ---------------------------------------------------------------------------


def identify_ports_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    if session_state.get("selected_port_ids") is not None:
        return StepOutput(content="Ports already identified.", success=True)

    user_input = step_input.input or ""
    if isinstance(user_input, dict):
        user_input = str(user_input)

    # Second pass: user replied with their selection
    if "presented_ports" in session_state:
        presented = session_state["presented_ports"]
        selected_ids = _parse_user_selection(str(user_input), presented)

        # Classify into auto-approvable (public) vs restricted
        portal = PortalClient()
        restricted_ids: list[str] = []
        auto_approvable_ids: list[str] = []

        for dataset_id in selected_ids:
            try:
                port = portal.get_output_port(dataset_id)
                access_type = (port.get("access_type") or "").lower()
                if access_type == "restricted":
                    restricted_ids.append(dataset_id)
                else:
                    auto_approvable_ids.append(dataset_id)
            except Exception:
                auto_approvable_ids.append(dataset_id)

        session_state["selected_port_ids"] = selected_ids
        session_state["restricted_ids"] = restricted_ids

        if not selected_ids:
            return StepOutput(
                content="No ports selected — nothing to query.",
                success=True,
            )
        return StepOutput(
            content=f"Selected {len(selected_ids)} port(s) ({len(restricted_ids)} restricted).",
            success=True,
        )

    # First pass: search ports, filter private, present to user
    question = str(user_input).strip()
    if not question:
        question = session_state.get("question", "")

    session_state["question"] = question

    portal = PortalClient()
    ports = portal.search_output_ports(question) if len(question) >= 3 else []

    # Filter out private ports
    visible_ports = [
        p for p in ports if (p.get("access_type") or "").lower() != "private"
    ]

    if not visible_ports:
        session_state["selected_port_ids"] = []
        session_state["restricted_ids"] = []
        return StepOutput(
            content="No accessible output ports found for your question.",
            success=True,
        )

    session_state["presented_ports"] = [
        {
            "id": p["id"],
            "name": p.get("name", ""),
            "access_type": p.get("access_type", ""),
            "data_product": p.get("data_product", {}),
            "description": p.get("description", ""),
        }
        for p in visible_ports[:10]
    ]

    return StepOutput(
        content=_format_ports_list(visible_ports[:10]),
        success=False,
        stop=True,
    )


# ---------------------------------------------------------------------------
# Step 2: provision_ephemeral
# ---------------------------------------------------------------------------


def provision_ephemeral_executor(
    step_input: StepInput, session_state: dict
) -> StepOutput:
    if session_state.get("ephemeral_dp_id"):
        return StepOutput(
            content=f"Ephemeral access already created (id={session_state['ephemeral_dp_id']}).",
            success=True,
        )

    selected_ids: list[str] = session_state.get("selected_port_ids", [])
    if not selected_ids:
        return StepOutput(
            content="No ports selected; skipping ephemeral provisioning.", success=True
        )

    question = session_state.get("question", "")
    portal = PortalClient()

    try:
        result = portal.create_ephemeral_access(
            output_port_ids=selected_ids,
            ttl_hours=8,
            justification=question,
        )
        ephemeral_id = result.get("id")
    except Exception as exc:
        return StepOutput(
            content=f"Failed to create ephemeral access record: {exc}",
            success=False,
            stop=True,
        )

    session_state["ephemeral_dp_id"] = ephemeral_id

    # Fetch namespace for display (no YAML written — data-agents must NOT restart)
    try:
        dp = portal.get_data_product(ephemeral_id)
        namespace = dp.get("namespace", ephemeral_id)
    except Exception:
        namespace = ephemeral_id

    restricted_ids: list[str] = session_state.get("restricted_ids", [])
    # Encode restricted count as sentinel so the Condition evaluator can read it
    sentinel = f"RESTRICTED|{len(restricted_ids)}" if restricted_ids else "APPROVED"
    return StepOutput(
        content=f"{sentinel}\nEphemeral access record created (namespace=`{namespace}`, id=`{ephemeral_id}`).",
        success=True,
    )


# ---------------------------------------------------------------------------
# Condition: has_restricted_ports
# ---------------------------------------------------------------------------


def has_restricted_ports(step_input: StepInput) -> bool:
    content = str(step_input.previous_step_content or "")
    return content.startswith("RESTRICTED|")


# ---------------------------------------------------------------------------
# Step 3 (conditional): wait_for_approvals
# ---------------------------------------------------------------------------


def wait_for_approvals_executor(
    step_input: StepInput, session_state: dict
) -> StepOutput:
    restricted_ids: list[str] = session_state.get("restricted_ids", [])
    ephemeral_dp_id: str = session_state.get("ephemeral_dp_id", "")

    if not restricted_ids or not ephemeral_dp_id:
        return StepOutput(content="No restricted ports to wait for.", success=True)

    portal = PortalClient()
    try:
        input_ports = portal.get_input_ports(ephemeral_dp_id)
    except Exception as exc:
        return StepOutput(
            content=f"Failed to check approval status: {exc}",
            success=False,
            stop=True,
        )

    status_map: dict[str, str] = {}
    for link in input_ports:
        op_id = str(
            link.get("output_port_id") or link.get("input_port", {}).get("id", "")
        )
        if op_id:
            status_map[op_id] = str(link.get("status", "pending")).lower()

    still_pending = [
        pid for pid in restricted_ids if status_map.get(pid, "pending") == "pending"
    ]
    newly_denied = [
        pid for pid in restricted_ids if status_map.get(pid, "pending") == "denied"
    ]

    if still_pending:
        return StepOutput(
            content=(
                f"Waiting for approval of {len(still_pending)} restricted port(s). "
                f"Approve them in the Portal ({_PORTAL_URL}), then send any message to continue."
            ),
            success=False,
            stop=True,
        )

    if newly_denied:
        return StepOutput(
            content=f"Access denied for {len(newly_denied)} port(s). Proceeding with approved ports only.",
            success=True,
        )

    return StepOutput(content="All restricted ports approved.", success=True)


# ---------------------------------------------------------------------------
# Step 4: call_data_team
# ---------------------------------------------------------------------------


def call_data_team_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    selected_ids: list[str] = session_state.get("selected_port_ids", [])
    if not selected_ids:
        return StepOutput(
            content="No ports were selected, so there is nothing to query.",
            success=True,
        )

    question = session_state.get("question", "")

    try:
        response = httpx.post(
            f"{_DATA_AGENTS_URL}/v1/teams/swiftgear-data-team/runs",
            json={"message": question, "stream": False},
            timeout=120.0,
        )
        response.raise_for_status()
        answer = response.json().get("content", "")
    except Exception as exc:
        return StepOutput(
            content=f"Failed to reach the data team: {exc}",
            success=False,
            stop=True,
        )

    ephemeral_id = session_state.get("ephemeral_dp_id", "")
    footer = (
        f"\n\n---\n*This access is recorded as an ephemeral data product "
        f"(`{ephemeral_id}`) and will expire in 8 hours.*"
    )

    return StepOutput(content=str(answer) + footer, success=True)


# ---------------------------------------------------------------------------
# Workflow assembly
# ---------------------------------------------------------------------------

adhoc_workflow = Workflow(
    id="adhoc",
    name="Ad-hoc Data Question",
    description="Answer an ad-hoc data question by identifying relevant output ports, creating ephemeral access, and delegating to the data team",
    steps=[
        Step(name="identify_ports", executor=identify_ports_executor),
        Step(name="provision_ephemeral", executor=provision_ephemeral_executor),
        Condition(
            name="has_restricted",
            evaluator=has_restricted_ports,
            steps=[
                Step(name="wait_for_approvals", executor=wait_for_approvals_executor)
            ],
        ),
        Step(name="call_data_team", executor=call_data_team_executor),
    ],
    session_state={},
    db=SqliteDb(db_file=f"{_AGENT_DATA_DIR}/agno_adhoc_workflow.db"),
)
