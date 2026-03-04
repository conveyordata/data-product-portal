import os
import yaml

from pathlib import Path
from mcp.client.stdio import StdioServerParameters
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from agno.skills import Skills, LocalSkills
from agno.tools.file import FileTools

yaml_dir = os.environ.get("AGENT_CONFIGS_PATH", "/agent_configs")
skill_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "skills", "postgres-semantic")
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
            instructions=config.get("instructions", ""),
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

    return agents or [make_fallback_agent()]


agent_os = AgentOS(agents=load_dynamic_agents(), tracing=True)
app = agent_os.get_app()
