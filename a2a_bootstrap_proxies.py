# a2a_bootstrap_proxies.py  ───────────────────────────────────────────────
import asyncio, httpx
from typing import List
from a2a.client import A2ACardResolver, A2AClient
from a2a_client import A2AMultiStepAgent
from smolagents.monitoring import LogLevel

class A2AProxyBootstrap:
    """
    Discover one or more remote A2A agents *once*, turn them into
    `A2AMultiStepAgent` objects and expose them as a list that can be plugged
    into `CodeAgent(managed_agents=…)`.
    """

    def __init__(self, urls: List[str]):
        self._urls = urls
        self._proxies: List[A2AMultiStepAgent] = []

    async def _discover(self):
        proxies: List[A2AMultiStepAgent] = []
        async with httpx.AsyncClient(timeout=30) as client:
            for url in self._urls:
                card = await A2ACardResolver(client, url).get_agent_card()
                a2a_client = await A2AClient.get_client_from_agent_card_url(client, card.url)
                proxy = A2AMultiStepAgent(
                    name=card.name,
                    description=card.description,
                    a2a_client=a2a_client,
                    card=card,
                    #verbosity_level = LogLevel.DEBUG
                )
                proxies.append(proxy)
        return proxies

    def load(self) -> List[A2AMultiStepAgent]:
        """Return a *cached* list of proxy-agents so we only discover once."""
        if self._proxies:
            return self._proxies
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                self._proxies = loop.run_until_complete(self._discover())
            else:
                self._proxies = loop.run_until_complete(self._discover())
        except RuntimeError:
            self._proxies = asyncio.run(self._discover())

        return self._proxies