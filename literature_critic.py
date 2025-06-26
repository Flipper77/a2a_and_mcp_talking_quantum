# literature_critic.py  – A2A-exposed LangGraph Agent
import os
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.utils import get_message_text, new_agent_text_message
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

# --- LangChain / LangGraph bits -----------------------------------------
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

def create_app(args):
    # ---- LLM -----------------------------------------------------------------

    llm = ChatOpenAI(
        model        = "gpt-4o",
        openai_api_key = args.openai_key,
        temperature  = 0.7,
    )

    # ---- LangGraph agent -----------------------------------------------------
    # `prompt=` lets us inject a *single* system prompt that applies before every run.
    graph = create_react_agent(
        model  = llm,
        tools  = [],
        prompt = (
            "You are a meticulous literary critic. "
            "Return a short, witty critique — no ‘thought / action’ narration."
        ),
    )

    # ----  A2A executor --------------------------------------------------------
    class LiteratureCriticExecutor(AgentExecutor):
        async def execute(self, ctx: RequestContext, q: EventQueue):
            user_text = get_message_text(ctx.message) or "No readable text."
            inputs = {"messages": [("user", user_text)]}
            result = await graph.ainvoke(inputs)
            final_msg = result["messages"][-1].content
            q.enqueue_event(new_agent_text_message(final_msg))

        async def cancel(self, *_):  # nothing long-running here
            pass

    # -----  AgentCard + app ----------------------------------------
    agent_card = AgentCard(
        name             = "literary_critic",
        description      = "Provides a literary critique and analysis of the supplied original text.",
        version          = "1.1.0",
        url              = args.url,
        defaultInputModes  = ["text"],
        defaultOutputModes = ["text"],
        capabilities     = AgentCapabilities(),
        skills=[AgentSkill(
            id          = "literary_critique",
            name        = "Literary Critic",
            description = "Provides literary critique and analysis.",
            tags        = ["literature", "critique", "analysis"],
            examples    = ["Critique this poem.", "Analyse this short story."],
            inputModes  = ["text"],
            outputModes = ["text"],
        )],
    )

    app = A2AStarletteApplication(
        agent_card   = agent_card,
        http_handler = DefaultRequestHandler(
            LiteratureCriticExecutor(), task_store=lambda: None
        ),
    ).build()

    return app


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default=os.getenv("A2A_AGENT_URL", "http://localhost:52042"))
    parser.add_argument("--openai-key", type=str, default=os.getenv("OPENAI_API_KEY",""))
    args = parser.parse_args()

    if not args.openai_key:
        raise ValueError("Missing OpenAI API key")

    from urllib.parse import urlparse

    parsed_url = urlparse(args.url)
    port = parsed_url.port or 52042

    app = create_app(args)

    print(f"Starting agent at {args.url}")
    uvicorn.run(app, host="0.0.0.0", port=port)