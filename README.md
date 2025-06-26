# A2A Talking Quantum – Minimal Agent-to-Agent (A2A) Demo

This repository accompanies our Medium article **“A New Hope: When a SmolAgent Meets a LangGraph Agent to Talk About Quantum Squirrels”**.  
It demonstrates how to integrate remote agents into a SmolAgents-based host via the A2A protocol, combining the modular reasoning power of **SmolAgents** with the orchestration capabilities of **LangGraph**.

---

## Highlights

This example shows:
- A **remote (or local) LangGraph-based literary critic agent**, wrapped in an A2A-compatible server using `A2AStarletteApplication`
- A **local SmolAgent host system**, able to reason and call both:
  - remote (or local) classic tools via **MCP** (e.g., library document tools), and
  - remote (or local) agents via **A2A**
- A **proxy bootstrapping system** to expose remote A2A agents to the local SmolAgent host

Agents use protocols to collaborate: **MCP for tools**, **A2A for peer agents**.

---

## Setup

Create new `python==3.12` environment. Activate it.

```bash
git clone <repo-url>
cd <repo-dir>
pip install -r requirements.txt
```

If you are using `conda`, don't forget `conda install nb_conda_kernels`

---

## Start the Remote Literary Critic (A2A Agent Server)

This is the LangGraph-powered A2A agent server.
Start it from the host notebook (below) or manually:

```bash
python literature_critic.py --url <url> --openai-key <your openai key>
```

- Port: `52042` (default)
- Described by an `AgentCard` and accessible via A2A protocol

---

## MCP Tooling (Library Server)

In parallel, we also run a classic MCP tool server.
Start it from the host notebook (below) or manually:

```bash
python library_server.py
```

- Port: `58002` (default for MCP tools)
- Serves document tools: `get_library`, `get_document`

## Starting the host

The `host.ipynb` notebook brings together remote MCP tools and remote A2A agents with a local host to enable hybrid reasoning.  
To run it, simply open the Jupyter notebook and execute the cells in order.

```bash
jupyter notebook host.ipynb
```

If you started the A2A and / or tool server on different, remote machines (not localhost), then adjust the urls in the notebook accordingly.

---

## Bootstrap the Proxy Agents

The script `a2a_bootstrap_proxies.py` contains methods for discovering and registering remote A2A agents as SmolAgent-compatible proxies.  
It retrieves their `AgentCard`s and wraps each one in a lightweight proxy (`A2AMultiStepAgent`) that integrates smoothly with the SmolAgents host.

---

## The A2A Client

The `a2a_client.py` script is used to construct and provide `A2AMultiStepAgent` — a class derived from SmolAgents' `MultiStepAgent` — and a client to communicate directly with a remote A2A agent.

---

## Core Files

- `host.ipynb`: Sets up a compact local host and brings together the remote MCP tools and remote A2A agents
- `library_server.py`: A2AStarletteApplication exposing the LangGraph agent
- `literature_critic.py`: Defines the LangGraph-based literary critic agent
- `a2a_client.py`: Sends A2A messages to the remote agent
- `a2a_bootstrap_proxies.py`: Discovers remote agents and wraps them as proxy agents
- `build_mcp_tool_schema.py`: Creates tool schemas for MCP tools
- `library/`: Directory for document resources
- `requirements.txt`: Required packages

---

## License

Creative Commons BY-NC 4.0  
For non-commercial, educational use. Dependencies retain their respective licenses.

---

## Contact

📧 [kontakt@seasparks.de](mailto:kontakt@seasparks.de)
