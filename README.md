# Agentic Commerce POC

Proof of concept for an **agentic conversational commerce system** built with LangGraph, LangChain, FastAPI and WebSockets.

The project explores how multiple specialized AI agents can collaborate inside a controlled workflow while keeping business rules, runtime data and orchestration separated from the model.

## What this project explores

The POC focuses on a conversational shopping scenario where an AI assistant can:

* interact naturally with a user;
* understand commercial intent;
* delegate product searches to a specialized agent;
* execute tools against runtime catalog data;
* return product and offer information;
* continue the conversation after a handoff;
* manage interaction state with LangGraph;
* stream internal execution events through WebSockets;
* support deterministic actions such as selection, purchase flows and session closing.

The main objective is not to build a complete e-commerce platform, but to experiment with **agent orchestration, tool calling, runtime context and real-time interaction**.

## Architecture

```text
User
  │
  ▼
Attention Agent
  │
  ├── Conversation
  ├── Intent understanding
  ├── Purchase interaction
  │
  └── Handoff
        │
        ▼
Search Agent
  │
  ├── Product search
  ├── Offers
  ├── Comparison
  └── Recommendations

        │
        ▼
      Tools
  │
  ├── Product catalog
  └── Offers

LangGraph
  │
  ├── State
  ├── Routing
  ├── Commands
  ├── Interrupts
  └── Conversation lifecycle

FastAPI + WebSocket
  │
  └── Real-time events and UI communication
```

## Main concepts

### Specialized agents

The system separates responsibilities between agents instead of using a single model for every task.

The **Attention Agent** owns the user conversation and decides when another capability is required.

The **Search Agent** specializes in querying products, offers and commercial information.

### Agent handoffs

Agents can transfer execution between each other using LangGraph commands while preserving the shared conversation state.

### Tool calling

Agents do not receive the complete product catalog directly in their prompt.

Catalog and offer data remain outside the model and are accessed through controlled tools when required.

### Runtime context

Business data can be provided through runtime context, keeping it separate from conversational context.

This allows the model to access capabilities without unnecessarily injecting all available data into its prompt.

### Real-time events

The application uses WebSockets to expose events such as:

```text
node_status
tool_status
agent activity
search activity
interaction events
```

This allows the frontend to represent what is happening during the execution of the graph.

## Project structure

```text
agentic-commerce-poc/

├── agentes/
├── comunicacion/
├── config/
├── data/
├── dominio/
├── graph/
├── skills/
├── tools/
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

The project separates:

* agent behavior;
* graph orchestration;
* tools;
* domain logic;
* communication;
* skills;
* configuration;
* runtime data.

## Technologies

* Python
* LangGraph
* LangChain
* FastAPI
* WebSockets
* Azure OpenAI / OpenAI-compatible models
* Pydantic

## Running the project

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in a local `.env` file.

Example:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT=
```

Do not commit the `.env` file to the repository.

Run the application:

```bash
python main.py
```

## Status

This repository is an experimental POC used to evaluate patterns for:

* multi-agent architectures;
* agent handoffs;
* LangGraph orchestration;
* tool usage;
* runtime context;
* streaming;
* human interaction;
* conversational commerce.

It is intentionally kept small enough to understand, modify and experiment with.

## License

This project is intended for educational and experimental purposes.
