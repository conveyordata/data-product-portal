"""Intake workflow for creating a new data product through a guided multi-step process."""

from __future__ import annotations

import json
import os
from typing import Any

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.workflow import Condition, Step, StepInput, StepOutput, Workflow

from workflow_agents.helpers import (
    _format_ports_list,
    _fuzzy_match,
    _parse_requirements_json,
    _parse_user_selection,
)
from workflow_agents.portal_client import PortalClient


# ---------------------------------------------------------------------------
# Step 1: gather_requirements
# ---------------------------------------------------------------------------

_REQUIREMENTS_SYSTEM_PROMPT = """\
You are a data product intake assistant for the SwiftGear Data Product Portal.

Your goal is to help the user define a new data product. Follow these steps:

1. Ask the user for: name, description, purpose/use-case, domain, and type.
   - Do NOT ask for namespace — derive it automatically from the name (lowercase, spaces → hyphens, remove special chars).
   - Use the `get_data_product_types` tool to fetch available types before asking about type. Present the real type names to the user.
2. While gathering info, use the `search_data_products` tool to search for existing data products that might already serve the purpose.
3. Present any matches and ask the user if one of them works. If yes — tell the user to use the existing product and stop.
4. Once all fields are confirmed and no existing product fits, output EXACTLY the following completion block (nothing after it):

REQUIREMENTS_COMPLETE
```json
{"name": "...", "namespace": "...", "description": "...", "purpose": "...", "domain": "...", "type": "..."}
```

Rules:
- Derive namespace from name: lowercase, replace spaces with hyphens, strip non-alphanumeric chars (e.g. "Marketing Customer 360" → "marketing-customer-360")
- Use the exact type name returned by `get_data_product_types` in the JSON
- Keep asking until all fields are provided and confirmed
- Do NOT include the REQUIREMENTS_COMPLETE block unless the user has confirmed all fields
"""


def _make_requirements_agent(portal: PortalClient) -> Agent:
    from agno.tools import Toolkit
    from agno.tools.function import Function

    def search_existing_products(query: str) -> str:
        """Search for existing data products matching a description or purpose."""
        results = portal.search_data_products(query)
        if not results:
            return "No existing data products found matching that description."
        lines = [f"Found {len(results)} data product(s):"]
        for p in results[:5]:
            lines.append(
                f"- **{p.get('name')}** (`{p.get('namespace')}`): {p.get('description', '')}"
            )
        return "\n".join(lines)

    def get_data_product_types() -> str:
        """Fetch available data product types from the Portal."""
        types = portal.get_data_product_types()
        if not types:
            return "No data product types found."
        return "Available types:\n" + "\n".join(f"- {t['name']}" for t in types)

    toolkit = Toolkit(
        name="portal_search",
        tools=[
            Function.from_callable(search_existing_products),
            Function.from_callable(get_data_product_types),
        ],
    )

    return Agent(
        name="Requirements Gatherer",
        description="Gathers requirements for a new data product",
        instructions=_REQUIREMENTS_SYSTEM_PROMPT,
        model=Claude(id="claude-sonnet-4-5"),
        tools=[toolkit],
        db=SqliteDb(db_file="agno_intake_requirements_agent.db"),
        add_history_to_context=True,
        num_history_runs=10,
        markdown=True,
    )


def requirements_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    # Idempotency: already completed
    if session_state.get("requirements"):
        return StepOutput(content="Requirements already gathered.", success=True)

    portal = PortalClient()
    agent = _make_requirements_agent(portal)

    user_message = step_input.input or "I want to create a new data product."
    if isinstance(user_message, dict):
        user_message = str(user_message)

    # Use workflow session_id as agent session_id to maintain conversation continuity
    workflow_session_id: str | None = None
    if step_input.workflow_session:
        workflow_session_id = step_input.workflow_session.session_id

    run_kwargs: dict[str, Any] = {"stream": False}
    if workflow_session_id:
        run_kwargs["session_id"] = f"intake-req-{workflow_session_id}"

    response = agent.run(user_message, **run_kwargs)
    agent_text = response.content if response and response.content else ""

    requirements = _parse_requirements_json(str(agent_text))
    if requirements:
        # Ensure namespace is always derived from name if missing or empty
        if not requirements.get("namespace"):
            import re as _re

            ns = requirements["name"].lower()
            ns = _re.sub(r"[^a-z0-9]+", "-", ns).strip("-")
            requirements["namespace"] = ns
        session_state["requirements"] = requirements
        return StepOutput(
            content=f"Requirements gathered:\n```json\n{json.dumps(requirements, indent=2)}\n```",
            success=True,
        )

    # Not complete yet — pause workflow, show agent response to user
    return StepOutput(content=str(agent_text), success=False, stop=True)


# ---------------------------------------------------------------------------
# Step 2: create_data_product
# ---------------------------------------------------------------------------


def create_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    if session_state.get("data_product_id"):
        return StepOutput(
            content=f"Data product already created (id={session_state['data_product_id']}).",
            success=True,
        )

    try:
        portal = PortalClient()
        reqs: dict[str, Any] = session_state["requirements"]

        # Resolve domain
        domains = portal.get_domains()
        domain = _fuzzy_match(reqs.get("domain", ""), domains)
        if not domain:
            domain = domains[0] if domains else None
        if not domain:
            return StepOutput(
                content=f"Could not find domain '{reqs.get('domain')}'. Available: {[d['name'] for d in domains]}",
                success=False,
                stop=True,
            )

        # Resolve type
        types = portal.get_data_product_types()
        dp_type = _fuzzy_match(reqs.get("type", ""), types)
        if not dp_type:
            dp_type = types[0] if types else None
        if not dp_type:
            return StepOutput(
                content=f"Could not find data product type '{reqs.get('type')}'. Available: {[t['name'] for t in types]}",
                success=False,
                stop=True,
            )

        # Resolve lifecycle (use first available or "Draft")
        lifecycles = portal.get_lifecycles()
        lifecycle = _fuzzy_match("Draft", lifecycles) or (
            lifecycles[0] if lifecycles else None
        )
        if not lifecycle:
            return StepOutput(
                content="No lifecycle configurations found in Portal.",
                success=False,
                stop=True,
            )

        # Get current user as owner
        owner = portal.get_current_user()

        # Create the data product
        result = portal.create_data_product(
            name=reqs["name"],
            namespace=reqs["namespace"],
            description=reqs["description"],
            domain_id=domain["id"],
            type_id=dp_type["id"],
            lifecycle_id=lifecycle["id"],
            owner_id=owner["id"],
            about=reqs.get("purpose", ""),
        )

        dp_id = result.get("id")
        session_state["data_product_id"] = dp_id

        return StepOutput(
            content=f"Created data product **{reqs['name']}** (id=`{dp_id}`).",
            success=True,
        )
    except Exception as exc:
        return StepOutput(
            content=f"Failed to create data product: {exc}",
            success=False,
            stop=True,
        )


# ---------------------------------------------------------------------------
# Step 3: discover_ports
# ---------------------------------------------------------------------------


def discover_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    if session_state.get("ports_selected"):
        return StepOutput(content="Output ports already selected.", success=True)

    try:
        portal = PortalClient()
        reqs: dict[str, Any] = session_state.get("requirements", {})

        # Second pass: user has already seen the list and replied with their selection
        if "presented_ports" in session_state:
            user_input = step_input.input or ""
            if isinstance(user_input, dict):
                user_input = str(user_input)
            presented = session_state["presented_ports"]
            selected_ids = _parse_user_selection(str(user_input), presented)
            session_state["selected_dataset_ids"] = selected_ids
            session_state["ports_selected"] = True

            if selected_ids:
                count = len(selected_ids)
                return StepOutput(
                    content=f"Got it — requesting access to {count} output port(s)...",
                    success=True,
                )
            return StepOutput(
                content="No output ports selected — skipping access requests.",
                success=True,
            )

        # First pass: search and present ports
        purpose = reqs.get("purpose") or reqs.get("description") or ""
        ports = portal.search_output_ports(purpose) if len(purpose) >= 3 else []

        if not ports:
            session_state["selected_dataset_ids"] = []
            session_state["ports_selected"] = True
            return StepOutput(
                content="No relevant output ports found. Skipping access requests.",
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
            for p in ports[:10]
        ]
        return StepOutput(
            content=_format_ports_list(ports[:10]), success=False, stop=True
        )
    except Exception as exc:
        return StepOutput(
            content=f"Failed to discover output ports: {exc}",
            success=False,
            stop=True,
        )


# ---------------------------------------------------------------------------
# Step 4: request_access
# ---------------------------------------------------------------------------


def _encode_access_result(pending_ids: list[str]) -> str:
    if pending_ids:
        return f"PENDING|{len(pending_ids)}"
    return "ALL_APPROVED"


def request_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    # If already requested, re-encode the result for the Condition step
    if session_state.get("access_requested"):
        pending = session_state.get("pending_ids", [])
        return StepOutput(content=_encode_access_result(pending), success=True)

    selected_ids: list[str] = session_state.get("selected_dataset_ids", [])
    dp_id: str | None = session_state.get("data_product_id")
    if not dp_id:
        return StepOutput(
            content="Cannot request access: data product was not created successfully.",
            success=False,
            stop=True,
        )

    if not selected_ids:
        session_state["access_requested"] = True
        session_state["pending_ids"] = []
        session_state["auto_approved_ids"] = []
        return StepOutput(content="ALL_APPROVED", success=True)

    portal = PortalClient()

    public_ids: list[str] = []
    restricted_ids: list[str] = []
    private_ids: list[str] = []
    skip_notes: list[str] = []

    for dataset_id in selected_ids:
        try:
            port = portal.get_output_port(dataset_id)
            access_type = (port.get("access_type") or "").lower()
            if access_type == "public":
                public_ids.append(dataset_id)
            elif access_type == "private":
                private_ids.append(dataset_id)
                skip_notes.append(
                    f"- **{port.get('name', dataset_id)}** is private — cannot request access"
                )
            else:
                restricted_ids.append(dataset_id)
        except Exception:
            # Default to restricted if lookup fails
            restricted_ids.append(dataset_id)

    # Request access for public + restricted in a single call
    access_ids = public_ids + restricted_ids
    pending_ids: list[str] = []
    auto_approved_ids: list[str] = []

    if access_ids:
        justification = (
            f"Requested by intake workflow for data product '{session_state['requirements'].get('name', '')}'. "
            f"Purpose: {session_state['requirements'].get('purpose', '')}"
        )
        try:
            portal.request_output_port_access(dp_id, access_ids, justification)
        except Exception as e:
            return StepOutput(
                content=f"Failed to request access: {e}", success=False, stop=True
            )

        # Check which ones were auto-approved (public) vs pending (restricted)
        auto_approved_ids = list(public_ids)
        pending_ids = list(restricted_ids)

    session_state["pending_ids"] = pending_ids
    session_state["auto_approved_ids"] = auto_approved_ids
    session_state["private_ids"] = private_ids
    session_state["access_requested"] = True

    content = _encode_access_result(pending_ids)
    if skip_notes:
        content += "\n\n" + "\n".join(skip_notes)

    return StepOutput(content=content, success=True)


# ---------------------------------------------------------------------------
# Condition: has_pending_approvals
# ---------------------------------------------------------------------------


def has_pending_approvals(step_input: StepInput) -> bool:
    content = step_input.previous_step_content or ""
    return str(content).startswith("PENDING|")


# ---------------------------------------------------------------------------
# Step 5a: check_approvals
# ---------------------------------------------------------------------------


def check_approvals_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    pending_ids: list[str] = session_state.get("pending_ids", [])
    dp_id: str = session_state["data_product_id"]

    if not pending_ids:
        return StepOutput(content="All approvals received.", success=True)

    portal = PortalClient()
    input_ports = portal.get_input_ports(dp_id)

    # Build a map: output_port_id → status
    status_map: dict[str, str] = {}
    for link in input_ports:
        op_id = str(
            link.get("output_port_id") or link.get("input_port", {}).get("id", "")
        )
        if op_id:
            status_map[op_id] = str(link.get("status", "pending")).lower()

    approved_now: list[str] = []
    denied_now: list[str] = []
    still_pending: list[str] = []

    for pid in pending_ids:
        status = status_map.get(pid, "pending")
        if status == "approved":
            approved_now.append(pid)
        elif status == "denied":
            denied_now.append(pid)
        else:
            still_pending.append(pid)

    # Update state
    auto_approved = session_state.get("auto_approved_ids", [])
    session_state["auto_approved_ids"] = auto_approved + approved_now
    session_state["pending_ids"] = still_pending

    if denied_now:
        denied_names = denied_now
        note = f"Access was denied for {len(denied_now)} port(s): {', '.join(denied_names)}."
        if not still_pending:
            return StepOutput(content=note, success=True)
        return StepOutput(
            content=f"{note}\n\nStill waiting for approval of {len(still_pending)} port(s). Send any message to check again.",
            success=False,
            stop=True,
        )

    if still_pending:
        return StepOutput(
            content=(
                f"Still waiting for approval of {len(still_pending)} port(s). "
                "Once approved in the Portal, send any message here to continue."
            ),
            success=False,
            stop=True,
        )

    return StepOutput(content="All access requests approved.", success=True)


# ---------------------------------------------------------------------------
# Step 6: handoff
# ---------------------------------------------------------------------------


def handoff_executor(step_input: StepInput, session_state: dict) -> StepOutput:
    reqs: dict[str, Any] = session_state.get("requirements", {})
    name = reqs.get("name", "your data product")
    dp_id = session_state.get("data_product_id", "")
    auto_approved = session_state.get("auto_approved_ids", [])
    private = session_state.get("private_ids", [])

    portal_url = os.environ.get("PORTAL_URL", "http://localhost:8080")

    lines = [
        f"Your data product **{name}** is ready! Here's a summary:\n",
        f"- Portal link: {portal_url}/data-products/{dp_id}",
        f"- Access granted to **{len(auto_approved)}** output port(s)",
    ]
    if private:
        lines.append(
            f"- **{len(private)}** private port(s) were skipped (access not available)"
        )

    return StepOutput(content="\n".join(lines), success=True)


# ---------------------------------------------------------------------------
# Workflow assembly
# ---------------------------------------------------------------------------

intake_workflow = Workflow(
    id="intake",
    name="Data Product Intake",
    description="Creates a new data product through a guided multi-step process",
    steps=[
        Step(name="gather_requirements", executor=requirements_executor),
        Step(name="create_data_product", executor=create_executor),
        Step(name="discover_ports", executor=discover_executor),
        Step(name="request_access", executor=request_executor),
        Condition(
            name="pending_check",
            evaluator=has_pending_approvals,
            steps=[Step(name="check_approvals", executor=check_approvals_executor)],
        ),
        Step(name="handoff", executor=handoff_executor),
    ],
    session_state={},
    db=SqliteDb(db_file="agno_intake_workflow.db"),
)
