"""Integration tests for MCP API endpoint using OAuth."""

import os
import socket
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

MCP_ENDPOINT = os.getenv("MCP_ENDPOINT", "https://mcp.rememberly.xyz/mcp")


def test_dns_resolution():
    """Test that mcp.rememberly.xyz resolves."""
    try:
        socket.gethostbyname("mcp.rememberly.xyz")
        print("[OK] DNS resolution successful")
    except socket.gaierror:
        print("[FAIL] DNS resolution failed")
        return False
    return True


async def test_oauth_and_tools_list():
    """Test OAuth authentication and listing available MCP tools."""
    print("\nConnecting with OAuth...")
    try:
        async with Client(
            MCP_ENDPOINT, auth="oauth", init_timeout=300, timeout=60
        ) as client:
            print("[OK] OAuth authentication successful")

            # List available tools
            tools = await client.list_tools()
            print(f"[OK] Retrieved {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool.name}")

            return True
    except Exception as e:
        print(f"[FAIL] OAuth or tools/list failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing MCP API endpoint...\n")

    # Basic connectivity tests
    test_dns_resolution()

    # OAuth and tools/list test
    asyncio.run(test_oauth_and_tools_list())
