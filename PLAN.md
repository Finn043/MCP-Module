# MCP Learning Module — Plan

## 📋 Overview

Interactive learning module để học MCP (Model Context Protocol) từ foundation đến advanced.

**Target Audience:** Người mới bắt đầu, muốn hiểu MCP từ gốc.

**Learning Style:** Theory → Demo → Interactive Exercise → Quiz

---

## 🎯 Learning Goals

1. Hiểu Process và File Descriptors
2. Master stdin/stdout communication
3. Hiểu JSON-RPC 2.0 protocol
4. Xây dựng MCP server cơ bản
5. Hiểu MCP transport (stdio vs SSE)
6. Xây dựng MCP tool thực tế

---

## 📚 Module Structure

### Phase 1: Foundation (Process & I/O)

| Lesson | Title | Topics | Status |
|--------|-------|--------|--------|
| 00 | Process la gi? | Process vs Program, PID, spawn process | ✅ Done |
| 01 | stdin/stdout | Standard I/O, read/write, pipe, flush | 🔄 In Progress |
| 02 | stderr | Error handling, separate streams | ⏳ Todo |
| 03 | File Descriptors | FD numbers, redirect, FD table | ⏳ Todo |

### Phase 2: Protocol (JSON-RPC)

| Lesson | Title | Topics | Status |
|--------|-------|--------|--------|
| 04 | JSON-RPC 2.0 Basics | Request/Response format, jsonrpc field | ⏳ Todo |
| 05 | JSON-RPC Methods | initialize, ping, error codes | ⏳ Todo |
| 06 | JSON-RPC Notifications | No id field, one-way messages | ⏳ Todo |
| 07 | JSON-RPC Batch | Multiple requests in one | ⏳ Todo |

### Phase 3: MCP Core

| Lesson | Title | Topics | Status |
|--------|-------|--------|--------|
| 08 | MCP Introduction | What is MCP, why use it, architecture | ⏳ Todo |
| 09 | MCP Initialize | Handshake flow, capabilities exchange | ⏳ Todo |
| 10 | MCP Tools | Tool definition, tools/list, tools/call | ⏳ Todo |
| 11 | MCP Resources | Resource URIs, resources/list, resources/read | ⏳ Todo |
| 12 | MCP Prompts | Prompt templates, prompts/list, prompts/get | ⏳ Todo |

### Phase 4: MCP Transport

| Lesson | Title | Topics | Status |
|--------|-------|--------|--------|
| 13 | stdio Transport | Line-delimited JSON, subprocess, pipe | ⏳ Todo |
| 14 | SSE Transport | HTTP + SSE, remote access, bidirectional | ⏳ Todo |
| 15 | Transport Comparison | When to use which, pros/cons | ⏳ Todo |

### Phase 5: Build MCP Server

| Lesson | Title | Topics | Status |
|--------|-------|--------|--------|
| 16 | Project Setup | Structure, dependencies, config | ⏳ Todo |
| 17 | Implement Tools | Hello, calculate, time tools | ⏳ Todo |
| 18 | Implement Resources | File system, database resources | ⏳ Todo |
| 19 | Error Handling | Protocol errors, tool errors, validation | ⏳ Todo |
| 20 | Testing & Debug | Unit tests, integration tests, debugging | ⏳ Todo |

---

## 🎨 UI/UX Design

### Page Structure

```
┌─────────────────────────────────────┐
│          Header (Title)             │
├─────────────────────────────────────┤
│  [Theory] [Demo] [Exercise] [Quiz] │  ← Tabs
├─────────────────────────────────────┤
│                                     │
│          Tab Content                │
│                                     │
│  - Theory boxes                     │
│  - Code editor (editable)           │
│  - Test input area                  │
│  - Run/Check buttons                │
│  - Terminal output                  │
│  - Quiz questions                   │
│                                     │
├─────────────────────────────────────┤
│     [← Prev]      [Next →]          │  ← Navigation
└─────────────────────────────────────┘
```

### Color Scheme (Dark Theme)

```css
Background: #1e1e1e
Container: #252526
Header: #333
Accent: #007acc (blue)
Success: #4ec9b0 (teal)
Warning: #ffc107 (yellow)
Error: #f44336 (red)
Text: #d4d4d4
```

### Interactive Elements

1. **Code Editor**
   - Syntax highlighting (basic)
   - Copy button
   - Reset button
   - Run/Check button

2. **Terminal**
   - macOS-style dots (red, yellow, green)
   - Command/Output differentiation
   - Error highlighting

3. **Quiz**
   - Click to select option
   - Instant feedback (correct/incorrect)
   - Score counter
   - Explanation display

---

## 📝 File Structure

```
learning/mcp-basics/
├── PLAN.md                          # This file
├── 00-process.html                  # ✅ Done
├── 01-stdio.html                    # 🔄 In Progress
├── 02-stderr.html                   # ⏳
├── 03-file-descriptors.html         # ⏳
├── 04-jsonrpc-basics.html           # ⏳
├── 05-jsonrpc-methods.html          # ⏳
├── 06-jsonrpc-notifications.html    # ⏳
├── 07-jsonrpc-batch.html            # ⏳
├── 08-mcp-intro.html                # ⏳
├── 09-mcp-initialize.html           # ⏳
├── 10-mcp-tools.html                # ⏳
├── 11-mcp-resources.html            # ⏳
├── 12-mcp-prompts.html              # ⏳
├── 13-stdio-transport.html          # ⏳
├── 14-sse-transport.html            # ⏳
├── 15-transport-comparison.html     # ⏳
├── 16-project-setup.html            # ⏳
├── 17-implement-tools.html          # ⏳
├── 18-implement-resources.html      # ⏳
├── 19-error-handling.html           # ⏳
├── 20-testing-debugging.html        # ⏳
└── index.html                       # Landing page
```

---

## 🔧 Technical Implementation

### HTML Structure

```html
- Container
  - Header
  - Tabs (Theory, Demo, Exercise, Quiz)
  - Content Sections (display: none/block)
    - Theory: explanation boxes, diagrams
    - Demo: read-only code + terminal output
    - Exercise: editable code + test input + run button
    - Quiz: multiple choice questions
  - Navigation (Prev/Next)
```

### JavaScript Features

```javascript
- Tab switching
- Code copy to clipboard
- Code reset
- Simulated code execution (basic validation)
- Quiz answer checking
- Score tracking
```

### Code Validation Strategy

**Phase 1-2 (Foundation):**
- Check for keywords (e.g., `subprocess`, `readline`, `flush`)
- Simulate output based on input

**Phase 3-5 (MCP):**
- Validate JSON structure
- Check required fields
- Simulate MCP protocol flow

---

## 📊 Progress Tracking

### Current Status

- ✅ Lesson 00: Process — Done
- 🔄 Lesson 01: stdin/stdout — In Progress
- ⏳ Lessons 02-20: Todo

### Next Steps

1. ✅ Complete Lesson 01 (stdin/stdout)
2. ⏳ Create Lesson 02 (stderr)
3. ⏳ Create Lesson 03 (File Descriptors)
4. ⏳ Create Phase 2 (JSON-RPC)
5. ⏳ Create Phase 3 (MCP Core)
6. ⏳ Create Phase 4 (Transport)
7. ⏳ Create Phase 5 (Build Server)

---

## 🎯 Success Criteria

### For Each Lesson

- ✅ Theory clear and concise
- ✅ Demo shows practical usage
- ✅ Exercise has working code validation
- ✅ Quiz has 5 relevant questions
- ✅ Navigation works correctly

### For Complete Module

- ✅ User can go from zero to building MCP server
- ✅ Each concept builds on previous
- ✅ Interactive elements work smoothly
- ✅ Dark theme consistent throughout
- ✅ Vietnamese language throughout

---

## 📚 Reference Materials

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)
- [Python subprocess docs](https://docs.python.org/3/library/subprocess.html)
- [Unix stdio reference](https://en.wikipedia.org/wiki/Standard_streams)

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-05-08 | Initial plan, Lesson 00 done, Lesson 01 in progress |
