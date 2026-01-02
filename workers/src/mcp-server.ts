/**
 * MCP Server Implementation
 * Handles MCP protocol requests after OAuth authorization
 */

import { Context } from 'hono';
import { verifyToken, extractBearerToken, AuthClaims } from './auth';

interface MCPRequest {
	jsonrpc: '2.0';
	id: string | number;
	method: string;
	params?: any;
}

interface MCPResponse {
	jsonrpc: '2.0';
	id: string | number;
	result?: any;
	error?: {
		code: number;
		message: string;
	};
}

/**
 * Handle MCP protocol requests
 */
export async function handleMCP(c: Context): Promise<Response> {
	// Verify OAuth token
	const authHeader = c.req.header('Authorization');
	const token = extractBearerToken(authHeader || null);

	if (!token) {
		return c.json({
			jsonrpc: '2.0',
			id: null,
			error: {
				code: -32001,
				message: 'Unauthorized: No token provided'
			}
		}, 401);
	}

	const claims = await verifyToken(token, c.env.USER_CACHE);
	if (!claims) {
		return c.json({
			jsonrpc: '2.0',
			id: null,
			error: {
				code: -32001,
				message: 'Unauthorized: Invalid token'
			}
		}, 401);
	}

	// Parse MCP request
	const request = await c.req.json<MCPRequest>();

	// Handle different MCP methods
	switch (request.method) {
		case 'initialize':
			return handleInitialize(c, request, claims);
		
		case 'tools/list':
			return handleToolsList(c, request, claims);
		
		case 'tools/call':
			return handleToolsCall(c, request, claims);
		
		case 'resources/list':
			return handleResourcesList(c, request, claims);
		
		case 'resources/read':
			return handleResourcesRead(c, request, claims);
		
		case 'prompts/list':
			return handlePromptsList(c, request, claims);
		
		default:
			return c.json({
				jsonrpc: '2.0',
				id: request.id,
				error: {
					code: -32601,
					message: `Method not found: ${request.method}`
				}
			});
	}
}

async function handleInitialize(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result: {
			protocolVersion: '2024-11-05',
			capabilities: {
				tools: {},
				resources: {},
				prompts: {}
			},
			serverInfo: {
				name: 'rememberly-mcp',
				version: '0.1.0'
			}
		}
	});
}

async function handleToolsList(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	// Forward to AWS API to get user's available tools
	const awsResponse = await fetch(`${c.env.AWS_API_ENDPOINT}/mcp/tools`, {
		headers: {
			'X-User-Id': claims.sub
		}
	});

	const tools = await awsResponse.json();

	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result: { tools }
	});
}

async function handleToolsCall(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	// Forward tool execution to AWS API
	const awsResponse = await fetch(`${c.env.AWS_API_ENDPOINT}/mcp/tools/call`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-User-Id': claims.sub
		},
		body: JSON.stringify(request.params)
	});

	const result = await awsResponse.json();

	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result
	});
}

async function handleResourcesList(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	const awsResponse = await fetch(`${c.env.AWS_API_ENDPOINT}/mcp/resources`, {
		headers: {
			'X-User-Id': claims.sub
		}
	});

	const resources = await awsResponse.json();

	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result: { resources }
	});
}

async function handleResourcesRead(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	const awsResponse = await fetch(`${c.env.AWS_API_ENDPOINT}/mcp/resources/read`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-User-Id': claims.sub
		},
		body: JSON.stringify(request.params)
	});

	const result = await awsResponse.json();

	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result
	});
}

async function handlePromptsList(c: Context, request: MCPRequest, claims: AuthClaims): Promise<Response> {
	const awsResponse = await fetch(`${c.env.AWS_API_ENDPOINT}/mcp/prompts`, {
		headers: {
			'X-User-Id': claims.sub
		}
	});

	const prompts = await awsResponse.json();

	return c.json({
		jsonrpc: '2.0',
		id: request.id,
		result: { prompts }
	});
}
