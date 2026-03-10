from agno.os import AgentOS
from intake_agent.workflow import intake_workflow

agent_os = AgentOS(workflows=[intake_workflow], tracing=True)
app = agent_os.get_app()
