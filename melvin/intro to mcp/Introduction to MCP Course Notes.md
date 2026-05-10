# Introduction to MCP — Anthropic Course Notes

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [The Problem MCP Solves](#the-problem-mcp-solves)
3. [Architecture Overview](#architecture-overview)
4. [MCP Servers](#mcp-servers)
5. [MCP Clients](#mcp-clients)
6. [Three Core Primitives](#three-core-primitives)
7. [Project: Document Manager CLI](#project-document-manager-cli)
   - [Setup](#setup)
   - [Part 1 — Defining Tools](#part-1--defining-tools)
   - [Part 2 — The Server Inspector](#part-2--the-server-inspector)
   - [Part 3 — Implementing the Client](#part-3--implementing-the-client)
   - [Part 4 — Defining Resources](#part-4--defining-resources)
   - [Part 5 — Accessing Resources](#part-5--accessing-resources)
   - [Part 6 — Defining Prompts](#part-6--defining-prompts)
   - [Part 7 — Prompts in the Client](#part-7--prompts-in-the-client)
8. [MCP Review — When to Use Each Primitive](#mcp-review--when-to-use-each-primitive)
9. [Key Takeaways](#key-takeaways)

---

## What is MCP?

**Model Context Protocol (MCP)** is a communication layer that provides Claude with context and tools without requiring you to write tedious integration code. It shifts the burden of tool definitions and execution away from your server to specialized MCP servers.

At its core, MCP defines a standard architecture:

- An **MCP Client** (your server/application) connects to one or more **MCP Servers**
- Each MCP Server contains **tools**, **prompts**, and **resources**
- Each MCP Server acts as an interface to some outside service

---

## The Problem MCP Solves

Imagine building a chat interface where users ask Claude about their GitHub data. GitHub has massive functionality — repositories, pull requests, issues, projects, and more.

**Without MCP:** You'd need to create an incredible number of tool schemas and functions yourself — writing, testing, and maintaining all that integration code.

**With MCP:** An MCP Server for GitHub handles all of that. It wraps up tons of functionality and exposes it as a standardized set of tools. Your application connects to this MCP server instead of implementing everything from scratch.

### Common Questions

| Question | Answer |
|---|---|
| Who authors MCP Servers? | Anyone. Service providers often release their own official MCP implementations (e.g., AWS). |
| How is this different from calling APIs directly? | MCP servers provide tool schemas and functions already defined for you. Direct API calls require you to author those definitions yourself. |
| Isn't MCP just tool use? | No. MCP servers *provide* tool schemas; tool use is about how Claude *calls* those tools. They are complementary but different concepts. |

---

## Architecture Overview

### Basic Flow

```
User → Your Server → MCP Client → MCP Server → External API
                                          ↓
Claude ← Your Server ← MCP Client ← MCP Server ← External API Response
```

### Step-by-Step Query Flow

When a user asks "What repositories do I have?", here's the complete flow:

1. **User Query** — User submits their question to your server
2. **Tool Discovery** — Your server needs to know what tools are available
3. **List Tools Exchange** — Server asks MCP client for available tools; client sends `ListToolsRequest` to MCP server, receives `ListToolsResult`
4. **Claude Request** — Server sends the user's query + available tools to Claude
5. **Tool Use Decision** — Claude decides it needs to call a tool
6. **Tool Execution Request** — Server asks MCP client to run the tool Claude specified
7. **External API Call** — MCP client sends `CallToolRequest` to MCP server, which calls the actual API
8. **Results Flow Back** — API responds; data flows back through MCP server as `CallToolResult`
9. **Tool Result to Claude** — Server sends tool results back to Claude
10. **Final Response** — Claude formulates an answer using the data
11. **User Gets Answer** — Server delivers Claude's response back to the user

---

## MCP Servers

MCP Servers provide access to data or functionality from outside services. They expose three types of primitives in a standardized way:

- **Tools** — Functions Claude can call to perform actions
- **Resources** — Data your app can fetch (like GET endpoints)
- **Prompts** — Pre-built instruction templates users can trigger

In our GitHub example, the MCP Server for GitHub contains tools like `get_repos()` and connects directly to GitHub's API. Your server communicates with the MCP server, which handles all the GitHub-specific implementation details.

---

## MCP Clients

The MCP client is the communication bridge between your server and MCP servers. It handles message exchange and protocol details so your application doesn't have to.

### Transport Agnostic

MCP is transport agnostic — the client and server can communicate over different protocols:

- **Standard I/O** (most common — both run on the same machine)
- HTTP
- WebSockets
- Various other network protocols

### Key Message Types

| Request | Response | Purpose |
|---|---|---|
| `ListToolsRequest` | `ListToolsResult` | Ask "what tools do you provide?" |
| `CallToolRequest` | `CallToolResult` | Ask the server to run a specific tool |
| `ReadResourceRequest` | `ReadResourceResult` | Fetch resource data by URI |
| `ListPromptsRequest` | `ListPromptsResult` | List available prompt templates |
| `GetPromptRequest` | `GetPromptResult` | Get a specific prompt with args filled in |

---

## Three Core Primitives

| Primitive | Controlled By | Purpose | Example |
|---|---|---|---|
| **Tools** | Claude (model) | Give Claude new capabilities it can use autonomously | Running code, making calculations |
| **Resources** | Your app (application) | Fetch data into your app for UI or context | Autocomplete lists, document injection |
| **Prompts** | User | Predefined workflows users trigger on demand | Slash commands, workflow buttons |

---

## Project: Document Manager CLI

The course project is a CLI chat application that manages documents using MCP. It has a document MCP server and a client that connects to Claude.

### Setup

**Prerequisites:** Python 3.9+, Anthropic API Key

1. Configure `.env`:
   ```
   ANTHROPIC_API_KEY="your-key-here"
   CLAUDE_MODEL="claude-sonnet-4-20250514"
   ```

2. Install with `uv` (recommended):
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -e .
   uv run main.py
   ```

   Or without `uv`:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
   python main.py
   ```

### Project Structure

```
cli_project/
├── .env                    # API keys and config
├── main.py                 # Entry point — wires everything together
├── mcp_server.py           # MCP server with tools, resources, prompts
├── mcp_client.py           # MCP client — bridge to MCP server
├── pyproject.toml          # Dependencies
├── core/
│   ├── __init__.py
│   ├── claude.py           # Claude API wrapper
│   ├── chat.py             # Base chat logic with tool-use loop
│   ├── cli_chat.py         # CLI-specific chat (resources, prompts, @mentions)
│   ├── cli.py              # CLI interface (autocomplete, keybindings)
│   └── tools.py            # Tool discovery and execution manager
```

### Dependencies

```toml
# pyproject.toml
dependencies = [
    "anthropic>=0.51.0",
    "mcp[cli]>=1.8.0",
    "prompt-toolkit>=3.0.51",
    "python-dotenv>=1.1.0",
]
```

---

## Part 1 — Defining Tools

The Python MCP SDK uses decorators and type hints to define tools — no manual JSON schemas required.

### Server Setup

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}
```

### Read Document Tool

```python
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="Id of the document to read"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

### Edit Document Tool

```python
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="The new text to insert in place of the old text"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
```

### Key Benefits of the SDK Approach

- No manual JSON schema writing
- Type hints provide automatic validation
- `Field` descriptions help Claude understand parameters
- Error handling integrates naturally with Python exceptions
- Registration happens automatically through decorators

---

## Part 2 — The Server Inspector

The MCP SDK includes a built-in browser-based inspector for testing your server without a full application.

### Starting the Inspector

```bash
mcp dev mcp_server.py
# Opens at http://127.0.0.1:6274
```

### Workflow

1. Click **Connect** to start your MCP server
2. Navigate to **Tools** → click **List Tools** to see all tools
3. Select a tool, fill in parameters, click **Run Tool**
4. Check results for success and expected output

You can test tools in sequence — e.g., edit a document then read it to verify changes. The inspector maintains server state between calls.

---

## Part 3 — Implementing the Client

The MCP client wraps the SDK's `ClientSession` and provides a clean interface for your application.

### Client Architecture

```
Your App → MCPClient (custom class) → ClientSession (SDK) → MCP Server
```

The client manages connection lifecycle via `AsyncExitStack` — ensuring proper cleanup.

### Connection Setup

```python
class MCPClient:
    def __init__(self, command: str, args: list[str], env=None):
        self._command = command
        self._args = args
        self._session = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(command=self._command, args=self._args, env=self._env)
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(ClientSession(_stdio, _write))
        await self._session.initialize()
```

### Core Methods

```python
async def list_tools(self) -> list[types.Tool]:
    result = await self.session().list_tools()
    return result.tools

async def call_tool(self, tool_name: str, tool_input) -> types.CallToolResult | None:
    return await self.session().call_tool(tool_name, tool_input)
```

### Testing

```bash
uv run mcp_client.py    # Test client independently
uv run main.py          # Test full application
```

Try asking: *"What is the contents of the report.pdf document?"*

---

## Part 4 — Defining Resources

Resources expose data to clients — similar to GET handlers in an HTTP server. They're for **fetching information**, not performing actions.

### Direct Resources (Static URI)

```python
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())
```

### Templated Resources (Parameterized URI)

```python
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

The SDK automatically parses URI parameters and passes them as keyword arguments.

### MIME Types

| MIME Type | Use For |
|---|---|
| `"application/json"` | Structured data |
| `"text/plain"` | Plain text |
| `"application/pdf"` | Binary files |

The SDK handles serialization automatically — just return the data structure.

### Testing Resources

```bash
mcp dev mcp_server.py
```

In the inspector, you'll see **Resources** (static) and **Resource Templates** (parameterized) sections.

---

## Part 5 — Accessing Resources

Resources can be directly included in prompts rather than requiring tool calls — a more efficient way to provide context.

### Client Implementation

```python
import json
from pydantic import AnyUrl

async def read_resource(self, uri: str) -> Any:
    result = await self.session().read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if isinstance(resource, types.TextResourceContents):
        if resource.mimeType == "application/json":
            return json.loads(resource.text)

    return resource.text
```

The function checks MIME type: JSON is parsed into objects, everything else returns as raw text.

### In the CLI App

The `CliChat` class uses resources to implement `@` mentions:

```python
async def _extract_resources(self, query: str) -> str:
    mentions = [word[1:] for word in query.split() if word.startswith("@")]
    doc_ids = await self.list_docs_ids()
    mentioned_docs = []

    for doc_id in doc_ids:
        if doc_id in mentions:
            content = await self.get_doc_content(doc_id)
            mentioned_docs.append((doc_id, content))

    return "".join(
        f'\n<document id="{doc_id}">\n{content}\n</document>\n'
        for doc_id, content in mentioned_docs
    )
```

When a user types `@report.pdf`, the system fetches the resource content and injects it directly into the prompt — no tool calls needed.

---

## Part 6 — Defining Prompts

Prompts are pre-built, tested instruction templates. They give better results than ad-hoc user instructions because the server author invests time in crafting and testing them.

### Format Document Prompt

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text,
    but don't change the meaning of the report. Use the 'edit_document' tool to edit the document.
    After the document has been edited, respond with the final version of the doc.
    Don't explain your changes.
    """
    return [base.UserMessage(prompt)]
```

The function returns a list of `Message` objects that get sent directly to Claude. Variables like `doc_id` are interpolated at request time.

### Key Benefits

- **Consistency** — Users get reliable results every time
- **Expertise** — Domain knowledge encoded into prompts
- **Reusability** — Multiple clients use the same prompts
- **Maintenance** — Update prompts in one place

---

## Part 7 — Prompts in the Client

The client needs two methods: one to list available prompts, another to retrieve a specific prompt with arguments.

### Client Implementation

```python
async def list_prompts(self) -> list[types.Prompt]:
    result = await self.session().list_prompts()
    return result.prompts

async def get_prompt(self, prompt_name, args: dict[str, str]):
    result = await self.session().get_prompt(prompt_name, args)
    return result.messages
```

### In the CLI App

The `CliChat` class handles slash commands by fetching prompts:

```python
async def _process_command(self, query: str) -> bool:
    if not query.startswith("/"):
        return False

    words = query.split()
    command = words[0].replace("/", "")

    messages = await self.doc_client.get_prompt(command, {"doc_id": words[1]})
    self.messages += convert_prompt_messages_to_message_params(messages)
    return True
```

When a user types `/format plan.md`, the system:
1. Extracts the command (`format`) and argument (`plan.md`)
2. Calls `get_prompt` with those arguments
3. Converts the returned prompt messages into the format Claude expects
4. Sends them to Claude, who uses the tools to read and reformat the document

---

## MCP Review — When to Use Each Primitive

Each primitive is controlled by a different part of your application stack:

### Decision Guide

```
Need to give Claude new capabilities?       → Use TOOLS    (model-controlled)
Need to get data into your app for UI?       → Use RESOURCES (app-controlled)
Want predefined workflows for users?         → Use PROMPTS   (user-controlled)
```

### Real-World Examples in Claude's Interface

| Primitive | Example |
|---|---|
| **Tools** | When Claude executes code, performs calculations, searches the web |
| **Resources** | "Add from Google Drive" — app fetches and injects file content |
| **Prompts** | Workflow buttons below the chat input — predefined, optimized workflows |

### Summary Table

| Primitive | Controlled By | Returns | Use Case |
|---|---|---|---|
| **Tools** | Claude (AI model) | Action results | Give Claude autonomous capabilities |
| **Resources** | Your app code | Data (via URI) | Populate UI, augment prompts with context |
| **Prompts** | User actions | Message list | Trigger predefined, tested workflows |

---

## Key Takeaways

1. **MCP eliminates integration boilerplate** — Instead of writing tool schemas and API wrappers yourself, MCP servers provide them ready-to-use.

2. **Three primitives, three controllers** — Tools serve the model, resources serve the app, prompts serve the user. Choose based on *who* initiates the action.

3. **The Python SDK makes it easy** — Decorators, type hints, and `Field` descriptors replace manual JSON schemas. The SDK handles serialization and protocol details.

4. **Test with the Inspector** — `mcp dev mcp_server.py` gives you a browser-based UI to test tools, resources, and prompts without a full application.

5. **Resources > Tools for read-only data** — If you just need to fetch data (not perform actions), resources are more efficient because content is injected directly into the prompt.

6. **Prompts encode expertise** — Well-crafted, tested prompts give users consistently better results than ad-hoc instructions.

---

## Complete Code Reference

### `mcp_server.py` (Complete)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

from pydantic import Field
from mcp.server.fastmcp.prompts import base


# --- TOOLS (model-controlled) ---

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="Id of the document to read"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="The new text to insert in place of the old text"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


# --- RESOURCES (app-controlled) ---

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# --- PROMPTS (user-controlled) ---

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text,
    but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited,
    respond with the final version of the doc. Don't explain your changes.
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### `mcp_client.py` (Complete)

```python
import sys
import asyncio
import json
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    def __init__(self, command: str, args: list[str], env: Optional[dict] = None):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(command=self._command, args=self._args, env=self._env)
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(ClientSession(_stdio, _write))
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Client session not initialized. Call connect first.")
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, tool_input) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    async def main():
        async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as _client:
            pass

    asyncio.run(main())
```

### `core/tools.py` — Tool Discovery and Execution

```python
import json
from typing import Optional, Literal, List
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient
from anthropic.types import Message, ToolResultBlockParam


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in tool_models
            ]
        return tools

    @classmethod
    async def execute_tool_requests(cls, clients: dict[str, MCPClient], message: Message):
        tool_requests = [block for block in message.content if block.type == "tool_use"]
        tool_result_blocks = []

        for tool_request in tool_requests:
            client = await cls._find_client_with_tool(list(clients.values()), tool_request.name)
            if not client:
                tool_result_blocks.append({
                    "tool_use_id": tool_request.id,
                    "type": "tool_result",
                    "content": "Could not find that tool",
                    "is_error": True,
                })
                continue

            tool_output = await client.call_tool(tool_request.name, tool_request.input)
            items = tool_output.content if tool_output else []
            content_list = [item.text for item in items if isinstance(item, TextContent)]

            tool_result_blocks.append({
                "tool_use_id": tool_request.id,
                "type": "tool_result",
                "content": json.dumps(content_list),
                "is_error": tool_output.isError if tool_output else False,
            })

        return tool_result_blocks
```

### `core/chat.py` — Chat Loop with Tool Use

The base `Chat` class implements the core agentic loop:

1. Append user message to conversation
2. Send to Claude with all available tools
3. If Claude responds with `tool_use`, execute the tool and feed the result back
4. Repeat until Claude gives a final text response

### `core/cli_chat.py` — CLI-Specific Chat Logic

Extends `Chat` with:
- **`@` mentions** — Extracts `@document_name` references, fetches resource content, injects into prompt
- **`/` commands** — Looks up prompts from the MCP server and sends their messages to Claude
- **Resource helper methods** — `list_docs_ids()`, `get_doc_content()`, `get_prompt()`

### `main.py` — Entry Point

Wires everything together:
1. Loads `.env` config
2. Creates a `Claude` service instance
3. Opens an `MCPClient` connection to the document server
4. Supports additional MCP servers via command-line arguments
5. Creates `CliChat` and `CliApp`, then runs the CLI loop
