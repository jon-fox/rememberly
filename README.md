# Rememberly

MCP Server for managing memory buckets and contextual data storage, deployed on AWS Lambda with Google OAuth authentication.

## Overview

**Rememberly** is a Model Context Protocol (MCP) server providing memory management capabilities via FastMCP. Features:

- **Memory Storage:** S3-backed persistent memory storage with DynamoDB metadata
- **Bucket Management:** Create, list, and delete memory buckets
- **OAuth Authentication:** Google OAuth integration for secure access
- **HTTP Transport:** RESTful API at https://mcp.rememberly.xyz
- **AWS Deployment:** Lambda-based serverless architecture

## Architecture

```
mcp_server/
├── tools/              # MCP tools (memory operations, bucket management, metrics)
├── resources/          # MCP resources (datetime, etc.)
├── services/           # Service layer
├── cache/              # User and secrets caching
├── db/                 # DynamoDB user management
├── utils/              # S3 storage utilities
└── server.py           # FastMCP server with Google OAuth
```

### Infrastructure

- **API Gateway:** HTTP API with custom domain (mcp.rememberly.xyz)
- **Lambda:** Containerized FastMCP server
- **S3:** Memory storage bucket
- **DynamoDB:** Metadata and user tracking
- **Route53/ACM:** DNS and TLS certificates

## Prerequisites

- **Python:** 3.12+
- **Package Manager:** [uv](https://docs.astral.sh/uv/)
- **AWS Account:** For Lambda deployment
- **Google OAuth:** Client ID and secret from Google Cloud Console
- **Terraform:** For infrastructure deployment

## Installation

```bash
git clone <repository-url>
cd rememberly
uv sync
```

## Configuration

### Environment Variables

**Local Development:**
```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export MCP_BASE_URL="http://localhost:8000"
```

**Production (Lambda):**
Set in `infra/terraform.tfvars`:
```terraform
google_client_id     = "your-client-id.apps.googleusercontent.com"
google_client_secret = "your-client-secret"
mcp_base_url        = "https://mcp.rememberly.xyz"
```

### Google OAuth Setup

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Add authorized redirect URI: `https://mcp.rememberly.xyz/auth/callback`
3. Configure client ID and secret in environment

## Deployment

### Build and Deploy

```bash
# Build Docker image
cd mcp_server && ./build.sh

# Deploy infrastructure
cd ../infra && terraform apply

# Or use the deploy script
cd ../infra && ./tf-apply.sh
```

### Local Testing

```Available Tools

- `store_memory` - Store memory in a bucket
- `get_memory` - Retrieve memory by ID
- `list_memories` - List memories in a bucket
- `delete_memory` - Delete a memory
- `create_bucket` - Create a new memory bucket
- `list_buckets` - List all buckets
- `delete_bucket` - Delete a bucket
- `get_metrics` - Get storage metrics

## Development

### Project Structure

```
rememberly/
├── mcp_server/
│   ├── server.py           # FastMCP server with Google OAuth
│   ├── tools/              # Memory and bucket management tools
│   ├── resources/          # MCP resources
│   ├── cache/              # User and secrets caching
│   ├── db/                 # DynamoDB operations
│   └── utils/              # S3 storage utilities
├── infra/                  # Terraform infrastructure
│   ├── api_gateway.tf      # API Gateway with OAuth routes
│   ├── mcp.tf              # Lambda function
│   ├── storage.tf          # S3 and DynamoDB
│   └── route53.tf          # DNS configuration
├── test_integration/       # Integration tests
└── ui/                     # Web interface (legacy)
```

### Testing

```bash
# Integration tests
cd test_integration
uv run python test_oauth.py
uv run python test_mcp_api.py
```

## License

MIT..")
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