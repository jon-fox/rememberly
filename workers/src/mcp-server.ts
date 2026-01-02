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
 * Proxies entire JSON-RPC request to AWS Lambda MCP server
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

	// Parse MCP request body
	const body = await c.req.text();

	// Forward entire JSON-RPC request to AWS Lambda with user ID in header
	const awsResponse = await fetch(c.env.AWS_API_ENDPOINT, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-User-Id': claims.sub
		},
		body: body
	});

	// Return AWS response directly
	return new Response(awsResponse.body, {
		status: awsResponse.status,
		headers: {
			'Content-Type': 'application/json'
		}
	});
}
