"""Test OAuth flow with Rememberly MCP server."""

import asyncio
import logging
from fastmcp import Client

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)


async def test_oauth():
    """Test OAuth authentication and tool listing."""
    print("🔐 Testing OAuth flow with Rememberly MCP server...")
    print("📍 Server: https://mcp.rememberly.xyz/mcp")
    print("⏳ Waiting for OAuth callback (this may take a moment)...")
    print()
    
    try:
        # Increase timeout to allow time for manual OAuth login and Lambda warm-up
        async with Client(
            "https://mcp.rememberly.xyz/mcp", 
            auth="oauth",
            init_timeout=300,  # 5 minutes for OAuth flow
            timeout=60  # 60 seconds for individual requests (Lambda warm-up)
        ) as client:
            print("✅ OAuth authentication successful!")
            print()
            
            # List available tools
            tools = await client.list_tools()
            print(f"🔧 Available tools ({len(tools)}):")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
            print()
            
            # List available resources
            resources = await client.list_resources()
            print(f"📦 Available resources ({len(resources)}):")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.name}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_oauth())
