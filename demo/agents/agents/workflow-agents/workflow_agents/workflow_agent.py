from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.workflow import WorkflowTools


from workflow_agents.adhoc_workflow import adhoc_workflow
# from workflow_agents.intake_workflow import intake_workflow

agent_with_workflows = Agent(
    name="Data Product Agent with Workflows",
    description="Routes user requests to the correct workflow: data product intake or ad-hoc data questions.",
    instructions="""You help users answer ad-hoc data questions at SwiftGear.
You have access to the adhoc_workflow. Use it to answer the user's data question.""",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[
        # WorkflowTools(workflow=intake_workflow),
        WorkflowTools(workflow=adhoc_workflow),
    ],
)
