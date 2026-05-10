# **Model Context Protocol (MCP): Advanced Topics**

**Anthropic Academy Course Notes**

## **Course Overview**

* **Introduction**  
* **Core MCP Features**  
  * Sampling  
  * Log and progress notifications  
  * Roots  
* **Transports and communication**  
  * JSON message types  
  * The STDIO transport  
  * The StreamableHTTP transport  
  * StreamableHTTP in depth  
  * State and the StreamableHTTP transport  
* **Assessment and next steps**

## **Part 1: Core MCP Features**

### **1\. Sampling**

Sampling allows a server to access a language model like Claude through a connected MCP client. Instead of the server directly calling Claude, it asks the client to make the call on its behalf. This shifts the responsibility and cost of text generation from the server to the client.

**The Problem Sampling Solves**

Imagine you have an MCP server with a research tool that fetches information from Wikipedia. After gathering all that data, you need to summarize it into a coherent report.

* **Option 1:** Give the MCP server direct access to Claude. The server needs its own API key, handles authentication, manages costs, and implements all integration code. This adds significant complexity.  
* **Option 2 (Sampling):** The server generates a prompt and asks the client "Could you call Claude for me?" The client, which already has a connection to Claude, makes the call and returns the results.

**How Sampling Works**

1. Server completes its work (like fetching Wikipedia articles).  
2. Server creates a prompt asking for text generation.  
3. Server sends a sampling request to the client.  
4. Client calls Claude with the provided prompt.  
5. Client returns the generated text to the server.  
6. Server uses the generated text in its response.

**Benefits of Sampling**

* **Reduces server complexity:** The server doesn't need to integrate with language models directly.  
* **Shifts cost burden:** The client pays for token usage, not the server.  
* **No API keys needed:** The server doesn't need credentials for Claude.  
* **Perfect for public servers:** You don't want a public server racking up AI costs for every user.

**Implementation Example**

*Server Side:*

@mcp.tool()  
async def summarize(text\_to\_summarize: str, ctx: Context):  
    prompt \= f"""  
    Please summarize the following text:  
    {text\_to\_summarize}  
    """  
      
    result \= await ctx.session.create\_message(  
        messages=\[  
            SamplingMessage(  
                role="user",  
                content=TextContent(  
                    type="text",  
                    text=prompt  
                )  
            )  
        \],  
        max\_tokens=4000,  
        system\_prompt="You are a helpful research assistant",  
    )  
      
    if result.content.type \== "text":  
        return result.content.text  
    else:  
        raise ValueError("Sampling failed")

*Client Side:*

async def sampling\_callback(  
    context: RequestContext, params: CreateMessageRequestParams  
):  
    \# Call Claude using the Anthropic SDK  
    text \= await chat(params.messages)  
      
    return CreateMessageResult(  
        role="assistant",  
        model=model,  
        content=TextContent(type="text", text=text),  
    )

\# Initialization  
async with ClientSession(  
    read,  
    write,  
    sampling\_callback=sampling\_callback  
) as session:  
    await session.initialize()

**Downloads:** sampling.zip

### **2\. Log and Progress Notifications**

Logging and progress notifications are simple to implement but make a huge difference in user experience. When Claude calls a tool that takes time to complete, users typically see nothing until the operation finishes. With notifications enabled, users get real-time feedback (progress bars, status messages, logs) showing exactly what's happening.

**How It Works (Server-Side)**

In the Python MCP SDK, you use the Context argument provided to your tool functions.

@mcp.tool(  
    name="research",  
    description="Research a given topic"  
)  
async def research(  
    topic: str \= Field(description="Topic to research"),  
    \*,  
    context: Context  
):  
    await context.info("About to do research...")  
    await context.report\_progress(20, 100\)  
    sources \= await do\_research(topic)  
      
    await context.info("Writing report...")  
    await context.report\_progress(70, 100\)  
    results \= await generate\_report(sources)  
      
    return results

**Client-Side Implementation**

You must set up callback functions to handle these notifications:

async def logging\_callback(params: LoggingMessageNotificationParams):  
    print(params.data)

async def print\_progress\_callback(  
    progress: float, total: float | None, message: str | None  
):  
    if total is not None:  
        percentage \= (progress / total) \* 100  
        print(f"Progress: {progress}/{total} ({percentage:.1f}%)")  
    else:  
        print(f"Progress: {progress}")

\# Applying callbacks during execution  
async def run():  
    async with stdio\_client(server\_params) as (read, write):  
        async with ClientSession(  
            read,  
            write,  
            logging\_callback=logging\_callback  
        ) as session:  
            await session.initialize()  
              
            await session.call\_tool(  
                name="add",  
                arguments={"a": 1, "b": 3},  
                progress\_callback=print\_progress\_callback,  
            )

**Downloads:** notifications.zip

### **3\. Roots**

Roots grant MCP servers access to specific files and folders on your local machine.

**The Problem Roots Solve**

Without roots, if a user asks Claude to "convert biking.mp4 to mov format", Claude has no way to search your entire file system to find where that file lives. Providing full absolute paths every time is not user-friendly.

**Roots in Action**

1. User asks to convert a video file.  
2. Claude calls list\_roots to see what directories it can access.  
3. Claude calls read\_dir on accessible directories to find the file.  
4. Once found, Claude calls the conversion tool with the full path.

**Implementation Details & Security**

The MCP SDK doesn't automatically enforce root restrictions; you must implement this. A typical pattern is creating an is\_path\_allowed() helper function that checks if a requested path falls within the approved roots list before performing any file operations.

**Key Benefits:**

* **User-friendly:** No need to type full file paths.  
* **Focused search:** Faster file discovery within approved directories.  
* **Security:** Prevents access to sensitive files outside approved areas.  
* **Flexibility:** Roots can be provided through tools or injected into prompts.

**Downloads:** roots.zip

## **Part 2: Transports and Communication**

### **4\. JSON Message Types**

All MCP communication happens through JSON messages. The complete list of message types is defined in the official MCP specification repository on GitHub using TypeScript to describe data structures.

**Message Categories:**

1. **Request-Result Messages:** Always come in pairs (e.g., Call Tool Request → Call Tool Result, Initialize Request → Initialize Result).  
2. **Notification Messages:** One-way messages detailing system events with no response expected (e.g., Progress Notification, Logging Message Notification).

**Client vs. Server Messages:**

MCP is a **bidirectional protocol**. Clients send requests to servers, but servers can *also* send requests to clients (like Sampling requests), and both can broadcast notifications.

### **5\. The STDIO Transport**

The most common transport for local development is the stdio transport, where the client launches the MCP server as a subprocess and communicates through standard input/output streams.

* Client sends messages via server's stdin.  
* Server responds via stdout.  
* Works only when client and server run on the same machine.

**The Three-Message Handshake:**

Every MCP connection must start with:

1. Initialize Request (Client)  
2. Initialize Result (Server)  
3. Initialized Notification (Client)

Stdio is the "ideal" baseline because bidirectional communication is seamless without HTTP constraints.

### **6\. The StreamableHTTP Transport**

StreamableHTTP enables remote connections over HTTP. However, standard HTTP is designed for clients to make requests to servers, making server-initiated requests (like sampling and notifications) challenging.

**The SSE Workaround (StreamableHTTP in Depth)**

StreamableHTTP solves HTTP limitations using Server-Sent Events (SSE):

1. **Initial Connection:** Client initializes and receives an mcp-session-id header.  
2. **SSE Connection:** Client makes a GET request to establish a persistent SSE connection. The server uses this to stream messages back to the client at any time.  
3. **Tool Calls:** When calling a tool, two connections are active:  
   * *Primary SSE Connection:* Stays open indefinitely for server-initiated requests/progress.  
   * *Tool-Specific SSE Connection:* Created via POST for the specific call and closes when the final result is sent.

### **7\. State and the StreamableHTTP Transport**

If you need to scale an MCP server horizontally (e.g., multiple instances behind a load balancer), coordinating the GET SSE connection and POST requests across different server instances becomes highly complex.

**stateless\_http**

Setting stateless\_http=True eliminates this coordination problem to allow scaling, but breaks the SSE workaround:

* No session IDs (server can't track clients).  
* No server-to-client requests (no sampling).  
* No progress reports or resource subscriptions.  
* *Benefit:* Client initialization is no longer required.

**json\_response**

Setting json\_response=True disables streaming for POST requests.

* No intermediate progress or log messages during execution.  
* Returns only the final tool result as plain JSON.

**When to use these flags:**

* **stateless\_http:** When you need load-balancer scaling, don't need server-to-client communication, and aren't using AI model sampling.  
* **json\_response:** When integrating with systems expecting plain JSON or when you don't need streaming updates.

**Downloads:** transport-http.zip