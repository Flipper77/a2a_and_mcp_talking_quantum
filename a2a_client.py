# a2a_client.py
from uuid import uuid4
import asyncio
import httpx
from typing import Optional, List, Dict
from a2a.client import A2AClient
from a2a.types import AgentCard, SendMessageRequest, Message, TextPart
from smolagents.agents import MultiStepAgent
from smolagents.monitoring import LogLevel


def _new_text_message(text: str, message_id: Optional[str] = None) -> Message:
    return Message(
        messageId=message_id or str(uuid4()),
        role="user",
        parts=[TextPart(type="text/plain", text=text)],
    )


class DummyModel:
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        return "[dummy model response]"


class A2AMultiStepAgent(MultiStepAgent):
    def __init__(
        self,
        name: str,
        description: str,
        a2a_client: A2AClient,
        card: AgentCard,
        managed_agent_prompt: Optional[str] = None,
        verbosity_level: LogLevel = LogLevel.DEBUG,  # <- Add this default param
    ):
        super().__init__(
            name=name,
            description=description,
            model=DummyModel(),
            tools=[],
            verbosity_level=verbosity_level  # <- Forward it here
        )
        self.a2a_client = a2a_client
        self.card = card
        self.prompt_template = managed_agent_prompt or "{task}"


    def initialize_system_prompt(self) -> Optional[str]:
        # Let A2A agent define the full prompt logic
        return None

    async def run(self, task: str, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=30) as http_client:
            a2a = await A2AClient.get_client_from_agent_card_url(
                http_client, self.card.url
            )

            message = _new_text_message(task)
            request = SendMessageRequest(params={"message": message})
            response = await a2a.send_message(request)

            # unwrap → Message → Parts → first TextPart
            for part in response.root.result.parts:
                if getattr(part.root, "kind", None) == "text":
                    return part.root.text
        return "No valid text found."


    def __call__(self, *args, **kwargs) -> str:
        # Support both `agent("text")` and `agent(task="text")`
        if args:
            task = args[0]
        else:
            task = kwargs.get("task")
        if task is None:
            raise ValueError("No task input provided to A2AMultiStepAgent.")
        return asyncio.run(self.run(task))