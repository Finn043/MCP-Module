# **Introduction to Model Context Protocol (MCP)**

**Source:** Anthropic Academy Course (14/14 Lessons Completed)

## **1\. Introducing MCP**

Model Context Protocol (MCP) is a communication layer that provides Claude with context and tools without requiring you to write tedious integration code. It shifts the burden of tool definitions and execution from your server to specialized **MCP Servers**.

### **The Problem MCP Solves**

If you build a chat interface to ask Claude about GitHub data, Claude needs tools to access GitHub's API. Without MCP, you would have to write, test, and maintain tool schemas and functions for every GitHub feature (repos, PRs, issues, etc.).

### **How MCP Works**

* **MCP Servers:** Specialized interfaces that expose tools, prompts, and resources in a standardized way. They wrap up outside service functionality (like GitHub's API).  
* **MCP Clients:** Your application connects to the MCP server instead of implementing API calls from scratch.  
* **Key Difference from Tool Use:** MCP servers provide the defined schemas and functions for you, whereas "tool use" is how Claude actually calls those tools. Anyone (e.g., AWS, GitHub) can author an official MCP server.

## **2\. MCP Clients**

The MCP client is the communication bridge between your server and MCP servers. It handles message exchanges and protocol details.

* **Transport Agnostic:** Clients and servers can communicate via standard input/output (stdio), HTTP, WebSockets, or other network protocols.  
* **Key Message Types:**  
  * ListToolsRequest / ListToolsResult: Asking the server what tools are available.  
  * CallToolRequest / CallToolResult: Running a specific tool and receiving the results.

### **The Complete Execution Flow**

1. **User Query:** User submits a question.  
2. **Tool Discovery:** Your server asks the MCP client for available tools (ListToolsRequest).  
3. **Claude Request:** Server sends the user query \+ tools to Claude.  
4. **Tool Use Decision:** Claude decides to call a tool.  
5. **Execution:** Server asks MCP client to run the tool. MCP client sends CallToolRequest to MCP server.  
6. **Results:** External API (e.g., GitHub) responds. Data flows back as CallToolResult.  
7. **Final Response:** Server sends results to Claude, who formulates the final answer for the user.

## **3\. Defining Tools with MCP**

Using the official Python SDK simplifies building MCP servers. You can define tools with Python decorators instead of complex JSON schemas.

### **Setting Up the Server**

from mcp.server.fastmcp import FastMCP

mcp \= FastMCP("DocumentMCP", log\_level="ERROR")

docs \= {  
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",  
    "report.pdf": "The report details the state of a 20m condenser tower."  
}

### **Tool Definition (Read & Edit)**

Using Pydantic Field provides argument descriptions that help Claude understand the tool.

@mcp.tool(  
    name="read\_doc\_contents",  
    description="Read the contents of a document and return it as a string."  
)  
def read\_document(  
    doc\_id: str \= Field(description="Id of the document to read")  
):  
    if doc\_id not in docs:  
        raise ValueError(f"Doc with id {doc\_id} not found")  
    return docs\[doc\_id\]

@mcp.tool(  
    name="edit\_document",  
    description="Edit a document by replacing a string..."  
)  
def edit\_document(  
    doc\_id: str \= Field(description="Id of the document that will be edited"),  
    old\_str: str \= Field(description="The text to replace..."),  
    new\_str: str \= Field(description="The new text to insert...")  
):  
    if doc\_id not in docs:  
        raise ValueError(f"Doc with id {doc\_id} not found")  
    docs\[doc\_id\] \= docs\[doc\_id\].replace(old\_str, new\_str)

**Benefits of the SDK:** No manual JSON schemas, automatic validation via type hints, integrated error handling, and automatic tool registration.

## **4\. The Server Inspector**

The Python MCP SDK includes a built-in browser-based inspector for real-time debugging.

* **Command:** mcp dev mcp\_server.py  
* **Features:** Connect to the server locally, view available resources/tools/prompts, execute tools manually, and test state management.

## **5\. Implementing a Client**

The client allows application code to communicate with the MCP server. It requires careful resource management to clean up connections.

\# List available tools  
async def list\_tools(self) \-\> list\[types.Tool\]:  
    result \= await self.session().list\_tools()  
    return result.tools

\# Execute a tool  
async def call\_tool(  
    self, tool\_name: str, tool\_input: dict  
) \-\> types.CallToolResult | None:  
    return await self.session().call\_tool(tool\_name, tool\_input)

## **6\. Defining & Accessing Resources**

**Resources** expose data to clients (like HTTP GET handlers) without requiring Claude to use a tool. Perfect for document mentions (e.g., @document\_name).

* **Direct Resources:** Static URIs.  
  @mcp.resource("docs://documents", mime\_type="application/json")  
  def list\_docs() \-\> list\[str\]:  
      return list(docs.keys())

* **Templated Resources:** Dynamic URIs with parameters.  
  @mcp.resource("docs://documents/{doc\_id}", mime\_type="text/plain")  
  def fetch\_doc(doc\_id: str) \-\> str:  
      return docs\[doc\_id\]

### **Accessing Resources (Client Side)**

Resources return a result with content and a MIME type.

async def read\_resource(self, uri: str) \-\> Any:  
    result \= await self.session().read\_resource(AnyUrl(uri))  
    resource \= result.contents\[0\]  
      
    if isinstance(resource, types.TextResourceContents):  
        if resource.mimeType \== "application/json":  
            return json.loads(resource.text)  
    return resource.text

## **7\. Defining & Using Prompts**

**Prompts** are pre-built, high-quality instructions (templates) that handle edge cases better than user-written prompts.

### **Defining Prompts (Server)**

@mcp.prompt(  
    name="format",  
    description="Rewrites the contents of the document in Markdown format."  
)  
def format\_document(  
    doc\_id: str \= Field(description="Id of the document to format")  
) \-\> list\[base.Message\]:  
    prompt \= f"""  
    Your goal is to reformat a document to be written with markdown syntax.  
    The id of the document you need to reformat is:  
    \<document\_id\>{doc\_id}\</document\_id\>  
    """  
    return \[base.UserMessage(prompt)\]

### **Retrieving Prompts (Client)**

async def list\_prompts(self) \-\> list\[types.Prompt\]:  
    result \= await self.session().list\_prompts()  
    return result.prompts

async def get\_prompt(self, prompt\_name, args: dict\[str, str\]):  
    result \= await self.session().get\_prompt(prompt\_name, args)  
    return result.messages

## **8\. MCP Review: The 3 Core Primitives**

Understanding when to use each primitive is based on what controls them:

1. **Tools (Model-Controlled):** Claude decides when to use them. Used to give the AI autonomous capabilities (e.g., executing code, fetching live API data).  
2. **Resources (App-Controlled):** Your application decides when to fetch them. Used to populate UI elements or inject context automatically (e.g., Google Drive document integration).  
3. **Prompts (User-Controlled):** Users trigger these via UI interactions (buttons, slash commands). Used for predefined, optimized workflows.