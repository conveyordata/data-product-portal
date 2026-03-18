from agno.os import AgentOS
from workflow_agents.adhoc_workflow import adhoc_workflow
from workflow_agents.intake_workflow import intake_workflow
from workflow_agents.workflow_agent import agent_with_workflows

agent_os = AgentOS(
    agents=[agent_with_workflows],
    workflows=[intake_workflow, adhoc_workflow],
    tracing=True,
)
app = agent_os.get_app()
