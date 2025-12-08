# Rememberly

MCP Server for managing context and chat history across conversations.

## Overview

**Rememberly** is a Model Context Protocol (MCP) server that provides memory and context management capabilities to Large Language Models. It enables:

- **Context Storage:** Persistent storage of conversation context
- **Chat History:** Long-term memory across sessions
- **Semantic Search:** Find relevant past conversations
- **User Preferences:** Track and recall user information
- **Session Management:** Maintain continuity across interactions

## Architecture

Rememberly follows a clean, modular architecture inspired by best practices:

```
mcp_server/
├── interfaces/          # Abstract base classes for tools, resources, prompts
│   ├── tool.py         # Tool interface and response models
│   ├── resource.py     # Resource interface
│   └── prompt.py       # Prompt interface
├── services/           # Service layer for managing components
│   ├── tool_service.py
│   ├── resource_service.py
│   └── prompt_service.py
├── tools/              # MCP tools implementation
│   └── example_memory/ # Placeholder memory tool
└── server.py           # FastMCP server configuration
```

### Key Components

- **Interfaces**: Abstract base classes defining contracts for tools, resources, and prompts
- **Services**: Registry and execution layer for MCP components
- **Tools**: Actual implementation of memory and context operations
- **Server**: FastMCP-based MCP server with tool registration

## Prerequisites

- **Python:** 3.12 or higher
- **Package Manager:** [uv](https://docs.astral.sh/uv/). Install if needed:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Installation

### Quick Start

```bash
# Install from source
git clone <repository-url>
cd rememberly
uv sync
```

## Local Testing

For local development and testing, use the included `chat.py` script:

```bash
# Install dev dependencies
uv sync --group dev

# Set up your API key
export OPENAI_API_KEY="your-api-key"  # or ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.

# Optional: Set custom model (defaults to openai:gpt-4o-mini)
export MODEL_IDENTIFIER="your-preferred-model"

# Run the chat interface
python chat.py
```

For available model providers and identifiers, see the [pydantic-ai documentation](https://ai.pydantic.dev/models/).

## Usage with MCP Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Rememberly": {
      "command": "uv",
      "args": ["run", "rememberly"]
    }
  }
}
```

## Development

### Project Structure

```
rememberly/
├── mcp_server/             # Main MCP server package
│   ├── __init__.py
│   ├── _version.py
│   ├── server.py          # MCP server entry point
│   ├── interfaces/        # Abstract base classes
│   ├── services/          # Service layer
│   └── tools/             # Tool implementations
├── chat.py                # Local testing script
├── pyproject.toml         # Project configuration
└── README.md
```

### Adding New Tools

1. Create a new directory under `tools/`:
   ```bash
   mkdir -p mcp_server/tools/my_tool
   ```

2. Create `models.py` with Pydantic input/output models:
   ```python
   from pydantic import BaseModel, Field
   from interfaces.tool import BaseToolInput

   class MyToolInput(BaseToolInput):
       query: str = Field(description="Query parameter")

   class MyToolOutput(BaseModel):
       result: str = Field(description="Result data")
   ```

3. Create `my_tool.py` implementing the `Tool` interface:
   ```python
   from interfaces.tool import Tool, ToolResponse
   from .models import MyToolInput, MyToolOutput

   class MyTool(Tool):
       name = "my_tool"
       description = "Description of what this tool does"
       input_model = MyToolInput
       output_model = MyToolOutput

       async def execute(self, input_data: MyToolInput) -> ToolResponse:
           # Implementation here
           output = MyToolOutput(result="...")
           return ToolResponse.from_model(output)
   ```

4. Register in `server.py`:
   ```python
   from tools.my_tool import MyTool

   tool_service.register_tools([
       MyTool(),
       # ... other tools
   ])
   ```

## Debugging

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run rememberly
```

## License

MIT License. See [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Implement actual memory storage (SQLite/PostgreSQL)
- [ ] Add semantic search capabilities
- [ ] Implement session management
- [ ] Add user preference tracking
- [ ] Create resource endpoints for memory browsing
- [ ] Add prompts for memory summarization