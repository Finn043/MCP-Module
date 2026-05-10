# Introduction to MCP — Anthropic Course Notes

![Introduction to MCP — Anthropic Course](images/figure%201.jpg)

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

![What is MCP?](images/figure%202.jpg)

**Model Context Protocol (MCP)** is a communication layer that provides Claude with context and tools without requiring you to write tedious integration code. It shifts the burden of tool definitions and execution away from your server to specialized MCP servers.

At its core, MCP defines a standard architecture:

- An **MCP Client** (your server/application) connects to one or more **MCP Servers**
- Each MCP Server contains **tools**, **prompts**, and **resources**
- Each MCP Server acts as an interface to some outside service

![MCP simplifies integrations — from N×M to N+M](images/figure%203.jpg)

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

![MCP Architecture — Host, Client, and Server](images/figure%204.jpg)

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

![Query flow — step by step](images/figure%205.jpg)

---

## MCP Servers

![MCP Servers — tools, resources, and prompts](images/figure%206.jpg)

MCP Servers provide access to data or functionality from outside services. They expose three types of primitives in a standardized way:

- **Tools** — Functions Claude can call to perform actions
- **Resources** — Data your app can fetch (like GET endpoints)
- **Prompts** — Pre-built instruction templates users can trigger

In our GitHub example, the MCP Server for GitHub contains tools like `get_repos()` and connects directly to GitHub's API. Your server communicates with the MCP server, which handles all the GitHub-specific implementation details.

---

## MCP Clients

![MCP Clients — the communication bridge](images/figure%207.jpg)

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

![Three Core Primitives — who controls what](images/figure%209.jpg)

| Primitive | Controlled By | Purpose | Example |
|---|---|---|---|
| **Tools** | Claude (model) | Give Claude new capabilities it can use autonomously | Running code, making calculations |
| **Resources** | Your app (application) | Fetch data into your app for UI or context | Autocomplete lists, document injection |
| **Prompts** | User | Predefined workflows users trigger on demand | Slash commands, workflow buttons |

---

## Project: Document Manager CLI

![Project overview — Document Manager CLI](images/figure%2010.jpg)

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

![Project file structure](images/figure%2011.jpg)

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

![Defining tools with the Python MCP SDK](images/figure%2012.jpg)

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

![MCP Server Inspector — browser-based testing](images/figure%2014.jpg)

The MCP SDK includes a built-in browser-based inspector for testing your server without a full application. It becomes an essential part of your development process — instead of writing separate test scripts or connecting to full applications, you can quickly iterate on tool implementations, test edge cases, and debug issues in real-time.

### Starting the Inspector

```bash
mcp dev mcp_server.py
# Opens at http://127.0.0.1:6274
```

### Workflow

1. Click **Connect** to start your MCP server (status changes from "Disconnected" to "Connected")
2. Navigate to **Tools** → click **List Tools** to see all available tools
3. Select a tool, fill in parameters, click **Run Tool**
4. Check results for success status and expected output

You can test tools in sequence — e.g., edit a document then read it to verify changes. The inspector maintains server state between calls, so edits persist and you can verify the complete functionality of your MCP server.

---

## Part 3 — Implementing the Client

![Client architecture overview](images/figure%2015.jpg)

The MCP client wraps the SDK's `ClientSession` and provides a clean interface for your application. In most real-world projects, you'll either implement an MCP client or an MCP server — not both. We build both in this project so you can see how they work together.

### Client Architecture

```
Your App → MCPClient (custom class) → ClientSession (SDK) → MCP Server
```

The client consists of two main components:
- **MCP Client** — A custom class we create to make using the session easier
- **Client Session** — The actual connection to the server (part of the MCP Python SDK)

The client manages connection lifecycle via `AsyncExitStack` — ensuring proper cleanup. It's what enables our code to interact with the MCP server at two key points: getting a list of available tools to send to Claude, and executing tools when Claude requests them.

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

Behind the scenes:
1. Your application uses the client to get available tools
2. These tools are sent to Claude along with your question
3. Claude decides to use the `read_doc_contents` tool
4. Your application uses the client to execute that tool
5. The result is returned to Claude, who then responds to you

The client acts as the bridge between your application logic and the MCP server's functionality, making it easy to integrate powerful tools into your AI workflows.

---

## Part 4 — Defining Resources

![Resources — app-controlled data access](images/figure%2017.jpg)

Resources expose data to clients — similar to GET handlers in an HTTP server. They're for **fetching information**, not performing actions. Resources can be directly included in prompts rather than requiring tool calls — a more efficient way to provide context to the AI model. When a user mentions a document, your system automatically injects its contents into the prompt sent to Claude, eliminating the need for Claude to use tools to fetch the information.

Resources follow a request-response pattern. When your client needs data, it sends a `ReadResourceRequest` with a URI to identify which resource it wants. The MCP server processes this request and returns the data in a `ReadResourceResult`.

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

![Accessing resources via @ mentions](images/figure%2019.jpg)

Resources can be directly included in prompts rather than requiring tool calls — a more efficient way to provide context. When a user types something like "What's in the @..." the code recognizes this as a resource request, sends a `ReadResourceRequest` to the MCP server, and gets back a `ReadResourceResult` with the actual content.

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

When a user types `@report.pdf`, the system fetches the resource content and injects it directly into the prompt — no tool calls needed. This creates a much smoother user experience compared to having the AI model make separate tool calls to access document contents. The resource content becomes part of the initial context, allowing for immediate responses about the data.

---

## Part 6 — Defining Prompts

![Defining prompts — user-controlled workflows](images/figure%2020.jpg)

Prompts are pre-built, tested instruction templates. They give better results than ad-hoc user instructions because the server author invests time in crafting and testing them.

**Why use prompts?** Users can already ask Claude to do most tasks directly. For example, a user could type "reformat the report.pdf in markdown" and get decent results. But they'll get much better results if you provide a thoroughly tested, specialized prompt that handles edge cases and follows best practices. As the MCP server author, you can spend time crafting, testing, and evaluating prompts that work consistently across different scenarios. Users benefit from this expertise without having to become prompt engineering experts themselves.

Prompts work best when they're specialized for your MCP server's domain. A document management server might have prompts for formatting, summarizing, or analyzing documents. A data analysis server might have prompts for generating reports or visualizations. The goal is to provide prompts that are so well-crafted and tested that users prefer them over writing their own instructions from scratch.

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
- **Expertise** — Domain knowledge encoded into prompts by server authors who invest time in crafting, testing, and evaluating them
- **Reusability** — Multiple client applications can use the same prompts
- **Maintenance** — Update prompts in one place to improve all clients

---

## Part 7 — Prompts in the Client

![Prompts in the client — slash commands](images/figure%2022.jpg)

The client needs two methods: one to list available prompts, another to retrieve a specific prompt with arguments filled in.

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

### The Prompt Lifecycle

The complete workflow for prompts is:

1. **Write and evaluate** a prompt relevant to your server's functionality
2. **Define the prompt** in your MCP server using the `@mcp.prompt` decorator
3. **Clients request the prompt** at any time via `list_prompts` / `get_prompt`
4. **Arguments provided by the client** become keyword arguments in your prompt function
5. **The function returns formatted messages** ready for the AI model

This system creates reusable, parameterized prompts that maintain consistency while allowing customization through variables.

---

## MCP Review — When to Use Each Primitive

![When to use each primitive](images/figure%2024.jpg)

Each primitive is controlled by a different part of your application stack:

### Tools: Model-Controlled

Tools are controlled entirely by Claude. The AI model decides when to call these functions, and the results are used directly by Claude to accomplish tasks. Tools are perfect for giving Claude additional capabilities it can use autonomously. When you ask Claude to "calculate the square root of 3 using JavaScript," it's Claude that decides to use a JavaScript execution tool to run the calculation.

### Resources: App-Controlled

Resources are controlled by your application code. Your app decides when to fetch resource data and how to use it — typically for UI elements or to add context to conversations. In our project, we used resources in two ways: fetching data to populate autocomplete options in the UI, and retrieving content to augment prompts with additional context. Think of the "Add from Google Drive" feature in Claude's interface — the application code determines which documents to show and handles injecting their content into the chat context.

### Prompts: User-Controlled

Prompts are triggered by user actions. Users decide when to run these predefined workflows through UI interactions like button clicks, menu selections, or slash commands. Prompts are ideal for implementing workflows that users can trigger on demand. In Claude's interface, those workflow buttons below the chat input are examples of prompts — predefined, optimized workflows that users can start with a single click.

### Decision Guide

![Decision guide — which primitive to use](images/figure%2025.jpg)

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

![Key takeaways](images/figure%2028.jpg)

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

---

## Slide Reference Index

All 29 course slides are saved in the `images/` folder. Below is a complete index of every slide with a brief description:

| Slide | File | Description |
|:---:|---|---|
| 1 | [figure 1.jpg](images/figure%201.jpg) | Course title — Introduction to MCP |
| 2 | [figure 2.jpg](images/figure%202.jpg) | What is MCP? — Protocol overview |
| 3 | [figure 3.jpg](images/figure%203.jpg) | The N×M integration problem (before vs. after MCP) |
| 4 | [figure 4.jpg](images/figure%204.jpg) | MCP Architecture — Host → Client → Server |
| 5 | [figure 5.jpg](images/figure%205.jpg) | Step-by-step query flow diagram |
| 6 | [figure 6.jpg](images/figure%206.jpg) | MCP Servers — tools, resources, and prompts |
| 7 | [figure 7.jpg](images/figure%207.jpg) | MCP Clients — the communication bridge |
| 8 | [figure 8.jpg](images/figure%208.jpg) | Key message types — request/response pairs |
| 9 | [figure 9.jpg](images/figure%209.jpg) | Three core primitives — who controls what |
| 10 | [figure 10.jpg](images/figure%2010.jpg) | Project overview — Document Manager CLI |
| 11 | [figure 11.jpg](images/figure%2011.jpg) | Project setup and file structure |
| 12 | [figure 12.jpg](images/figure%2012.jpg) | Part 1 — Defining tools with the SDK |
| 13 | [figure 13.jpg](images/figure%2013.jpg) | Tool implementation — read and edit documents |
| 14 | [figure 14.jpg](images/figure%2014.jpg) | Part 2 — The Server Inspector |
| 15 | [figure 15.jpg](images/figure%2015.jpg) | Part 3 — Client architecture and connection setup |
| 16 | [figure 16.jpg](images/figure%2016.jpg) | Client code — session management and core methods |
| 17 | [figure 17.jpg](images/figure%2017.jpg) | Part 4 — Defining resources (static and templated) |
| 18 | [figure 18.jpg](images/figure%2018.jpg) | Resource code — URI templates and MIME types |
| 19 | [figure 19.jpg](images/figure%2019.jpg) | Part 5 — Accessing resources via @ mentions |
| 20 | [figure 20.jpg](images/figure%2020.jpg) | Part 6 — Defining prompts |
| 21 | [figure 21.jpg](images/figure%2021.jpg) | Prompt implementation — format_document example |
| 22 | [figure 22.jpg](images/figure%2022.jpg) | Part 7 — Using prompts in the client |
| 23 | [figure 23.jpg](images/figure%2023.jpg) | Slash command handling code |
| 24 | [figure 24.jpg](images/figure%2024.jpg) | MCP Review — when to use each primitive |
| 25 | [figure 25.jpg](images/figure%2025.jpg) | Decision guide — tools vs. resources vs. prompts |
| 26 | [figure 26.jpg](images/figure%2026.jpg) | Real-world examples in Claude's interface |
| 27 | [figure 27.jpg](images/figure%2027.jpg) | Summary table of all primitives |
| 28 | [figure 28.jpg](images/figure%2028.jpg) | Key takeaways |
| 29 | [figure 29.jpg](images/figure%2029.jpg) | Course completion and next steps |
