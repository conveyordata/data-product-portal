import os
import yaml

from pathlib import Path
from mcp.client.stdio import StdioServerParameters
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.team import Team
from agno.team.mode import TeamMode
from agno.tools.mcp import MCPTools
from agno.skills import Skills, LocalSkills
from agno.tools.file import FileTools

yaml_dir = os.environ.get("AGENT_CONFIGS_PATH", "/agent_configs")
skill_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "skills", "postgres-semantic")
)


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

    return f"""You are the **{name}**, a specialized AI data expert embedded in SwiftGear's Data Product Portal.

## Identity & Expertise

You are a domain expert for the **{description}** data product. When someone asks who you are or what you know, introduce yourself as a data expert for this product and describe:
- The schemas and tables you own and what they contain
- The metrics and KPIs you can compute
- The business rules and semantic definitions that govern the data (e.g., monetary units, status filters, known gotchas)
- Which other data products you have access to (if any), and why

You are not a generic assistant. You have deep, specific knowledge of this data product and will use it to give authoritative, precise answers.

## Your Semantic Knowledge Base

Your semantic models (OSI YAML files) are your source of truth for business logic. They define field expressions, metric formulas, data quality rules, and cross-domain relationships.

Your models are located at:
{osi_file_list if osi_file_list else "  (no semantic models loaded yet — run `task create-products` first)"}

## Business Context

{product_context}
{schema_restriction}
## Mandatory Protocol for ALL Data Questions

For any question involving data, metrics, SQL, tables, analysis, or anything numerical:

1. **Read your semantic models first** — load all relevant OSI YAML files before using any database tools. This is non-negotiable, even for simple queries.
2. **Extract and apply business rules** — use exact field expressions, metric formulas, and domain instructions from the models.
3. **Only then query the database** — use MCP postgres tools with the correct expressions, filters, and joins from the semantic model.
4. **Show your reasoning** — briefly cite which rule or metric formula you applied (e.g., "per the semantic model, amounts are in cents so I divide by 100").
5. **Challenge incorrect premises** — if the user's assumption contradicts the actual data, say so directly and provide the correct figure.

Efficiency tip: read all relevant OSI files in a single batch call rather than one by one.

## Response Style

- Lead with the answer, then the evidence (SQL + result).
- Be concise but complete — include the actual numbers, not just the methodology.
- For identity questions: be specific about your domain, tables, metrics, and any known data quirks.
- Never guess column names or metric formulas — always derive them from the semantic model.
"""


def make_admin_agent() -> Agent:
    return Agent(
        name="Generic Database Agent",
        description="Full-access database agent for ad-hoc queries across all schemas.",
        instructions=(
            "You are a database assistant with full admin access to the PostgreSQL database. "
            "Use the MCP postgres tools to answer questions about any table or schema."
        ),
        model=Claude(id="claude-sonnet-4-5"),
        tools=[
            MCPTools(
                server_params=StdioServerParameters(
                    command="toolbox",
                    args=["--prebuilt", "postgres", "--stdio"],
                    env={
                        "POSTGRES_HOST": os.environ.get(
                            "PROV_DEMO_DB_HOST", "postgresql-demo"
                        ),
                        "POSTGRES_PORT": os.environ.get("PROV_DEMO_DB_PORT", "5432"),
                        "POSTGRES_DATABASE": os.environ.get(
                            "PROV_DEMO_DB_NAME", "dpp_demo"
                        ),
                        "POSTGRES_USER": os.environ.get(
                            "PROV_DEMO_DB_ADMIN_USER", "postgres"
                        ),
                        "POSTGRES_PASSWORD": os.environ.get(
                            "PROV_DEMO_DB_ADMIN_PASSWORD", "abc123"
                        ),
                    },
                )
            ),
        ],
        db=SqliteDb(db_file="agno_generic_database_agent.db"),
        add_datetime_to_context=True,
        add_history_to_context=False,
        num_history_runs=0,
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
        model=Claude(id="claude-sonnet-4-5"),
        add_datetime_to_context=True,
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

        agent = Agent(
            name=config["name"],
            description=config.get("description", ""),
            instructions=build_instructions(config),
            model=Claude(id="claude-sonnet-4-5"),
            skills=Skills(loaders=[LocalSkills(os.path.abspath(skill_path))]),
            tools=[
                MCPTools(
                    server_params=StdioServerParameters(
                        command="toolbox",
                        args=["--prebuilt", "postgres", "--stdio"],
                        env={
                            "POSTGRES_HOST": postgres_cfg.get("host", "localhost"),
                            "POSTGRES_PORT": str(postgres_cfg.get("port", 5432)),
                            "POSTGRES_DATABASE": postgres_cfg.get("database", ""),
                            "POSTGRES_USER": postgres_cfg.get("user", ""),
                            "POSTGRES_PASSWORD": postgres_cfg.get("password", ""),
                        },
                    )
                ),
                FileTools(Path("/products")),
            ],
            db=SqliteDb(db_file=f"agno_{config['name'].replace(' ', '_')}.db"),
            add_datetime_to_context=True,
            add_history_to_context=True,
            num_history_runs=3,
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
        model=Claude(id="claude-sonnet-4-5"),
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
