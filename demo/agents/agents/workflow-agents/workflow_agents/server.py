from agno.os import AgentOS
from workflow_agents.adhoc_workflow import adhoc_workflow
from workflow_agents.intake_workflow import intake_workflow

agent_os = AgentOS(workflows=[intake_workflow, adhoc_workflow], tracing=True)
app = agent_os.get_app()
