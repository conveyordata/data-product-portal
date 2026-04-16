import os
import yaml

from pathlib import Path
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.team import Team
from agno.team.mode import TeamMode
from agno.tools.postgres import PostgresTools
from agno.tools.file import FileTools

yaml_dir = os.environ.get("AGENT_CONFIGS_PATH", "/agent_configs")
model_id = os.environ.get("AGENT_MODEL_ID", "claude-sonnet-4-5")


def build_instructions(config: dict) -> str:
    name = config["name"]
    description = config.get("description", "")
    product_context = config.get("instructions", "")
    osi_files = config.get("osi_files", [])
    osi_file_list = "\n".join(f"  - {f}" for f in osi_files)

    allowed_schemas = config.get("allowed_schemas", [])
    if allowed_schemas:
        schema_list = ", ".join(f"`{s}`" for s in allowed_schemas)
        schema_restriction = (
            f"\n## Database Access\n\n"
            f"You have direct database access to **only** these PostgreSQL schemas: {schema_list}. "
            f"You cannot query any other schema — not even to list tables or check existence.\n\n"
            f"**Important:** your OSI semantic model files may reference other schemas as cross-domain "
            f"relationships. Those references are documentation metadata only. Do not describe those "
            f"schemas as ones you 'can see', 'have access to', or 'can query'. If asked what schemas "
            f"or tables you can query, list only the schemas above.\n"
        )
    else:
        schema_restriction = ""

    return f"""You are {name}, a data expert for the {description} product.

## Semantic Models
{osi_file_list or "  (none — run `task create-products` first)"}

{product_context}
{schema_restriction}
## Protocol (every data question)
1. Read all relevant semantic model files first.
2. Extract field expressions, metric formulas, domain instructions, and join conditions.
3. Query the database using only what the models define — never guess column names.
4. Cite which semantic rule or metric you applied.
5. If a user assumption contradicts the data, correct it with the actual figure.

Lead with the answer, then show SQL and results.
"""


def make_admin_agent() -> Agent:
    return Agent(
        name="Generic Database Agent",
        description="Full-access database agent for ad-hoc queries across all schemas.",
        instructions=(
            "You are a database assistant with full admin access to the PostgreSQL database. "
            "Use postgres tools to answer questions about any table or schema."
        ),
        model=Claude(id=model_id, cache_system_prompt=True),
        tools=[
            PostgresTools(
                host=os.environ.get("PROV_DEMO_DB_HOST", "postgresql-demo"),
                port=int(os.environ.get("PROV_DEMO_DB_PORT", "5432")),
                db_name=os.environ.get("PROV_DEMO_DB_NAME", "dpp_demo"),
                user=os.environ.get("PROV_DEMO_DB_ADMIN_USER", "postgres"),
                password=os.environ.get("PROV_DEMO_DB_ADMIN_PASSWORD", "abc123"),
            ),
        ],
        db=SqliteDb(db_file="agno_generic_database_agent.db"),
        add_history_to_context=False,
        num_history_runs=0,
        compress_tool_results=True,
        markdown=True,
    )


def make_fallback_agent() -> Agent:
    return Agent(
        name="Portal Assistant",
        description="General assistant for the Data Product Portal demo.",
        instructions=(
            "You are a helpful assistant for the SwiftGear Data Product Portal demo. "
            "Data product agents are provisioned automatically when data products are created in the portal. "
            "If no data product agents are available yet, let the user know they should run `task create-products` first."
        ),
        model=Claude(id=model_id, cache_system_prompt=True),
        markdown=True,
    )


def load_dynamic_agents():
    agents = []

    if not os.path.isdir(yaml_dir):
        return [make_fallback_agent()]

    for filename in os.listdir(yaml_dir):
        if not filename.endswith(".yml"):
            continue

        config_file = os.path.join(yaml_dir, filename)
        with open(config_file) as f:
            config = yaml.safe_load(f)

        postgres_cfg = config.get("postgres", {})

        primary_schema = config.get("allowed_schemas", ["public"])[0]
        agent = Agent(
            name=config["name"],
            description=config.get("description", ""),
            instructions=build_instructions(config),
            model=Claude(id=model_id, cache_system_prompt=True),
            tools=[
                PostgresTools(
                    host=postgres_cfg.get("host", "localhost"),
                    port=int(postgres_cfg.get("port", 5432)),
                    db_name=postgres_cfg.get("database", ""),
                    user=postgres_cfg.get("user", ""),
                    password=postgres_cfg.get("password", ""),
                    table_schema=primary_schema,
                ),
                FileTools(Path("/products")),
            ],
            db=SqliteDb(db_file=f"agno_{config['name'].replace(' ', '_')}.db"),
            add_history_to_context=False,
            num_history_runs=0,
            compress_tool_results=True,
            markdown=True,
        )
        agents.append(agent)

    return [make_admin_agent()] + (agents or [make_fallback_agent()])


def make_data_team(agents: list[Agent]) -> Team:
    return Team(
        name="SwiftGear Data Team",
        description=(
            "A coordinated team of domain-specific data product agents for SwiftGear. "
            "Routes questions to the right specialist and synthesises cross-domain answers."
        ),
        mode=TeamMode.route,
        model=Claude(id=model_id),
        members=agents,
        instructions=(
            "You are the SwiftGear Data Team coordinator. "
            "When a question touches a single data domain, delegate it directly to the relevant specialist agent. "
            "When a question spans multiple domains, delegate sub-questions to each specialist and combine their answers into one coherent response. "
            "Always cite which agent(s) provided the underlying data."
        ),
        markdown=True,
        add_datetime_to_context=True,
        show_members_responses=True,
    )


_dynamic_agents = load_dynamic_agents()
_team_members = [a for a in _dynamic_agents if a.name != "Generic Database Agent"]
_team = make_data_team(_team_members)

agent_os = AgentOS(agents=_dynamic_agents, teams=[_team], tracing=True)
app = agent_os.get_app()
