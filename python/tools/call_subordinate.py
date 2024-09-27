from agent import Agent
from python.helpers.tool import Tool, Response

class Delegation(Tool):

    def __init__(self, agent, **kwargs):
        super().__init__(agent, **kwargs)
        self.agent = agent  # Properly initialize the agent attribute

    async def execute(self, message="", reset="", **kwargs):
        # Create subordinate agent if it doesn't exist or if reset is True
        if (
            self.agent.get_data("subordinate") is None
            or str(reset).lower().strip() == "true"
        ):
            subordinate = Agent(
                agent_id=f"{self.agent.agent_id}_sub",
                name=f"Subordinate of {self.agent.name}",
                config=self.agent.config,
                context=self.agent.context,
            )
            subordinate.set_data("superior", self.agent)
            self.agent.set_data("subordinate", subordinate)
        # Run subordinate agent message loop
        response_message = await self.agent.get_data("subordinate").message_loop(
            message
        )
        return Response(
            message=response_message,
            break_loop=False,
        )
