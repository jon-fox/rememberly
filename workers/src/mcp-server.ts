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
	// Include all MCP-required headers from the original request
	const forwardHeaders: Record<string, string> = {
		'Content-Type': c.req.header('Content-Type') || 'application/json',
		'X-User-Id': claims.sub
	};
	
	// Forward MCP protocol headers (required by MCP spec)
	const acceptHeader = c.req.header('Accept');
	if (acceptHeader) {
		forwardHeaders['Accept'] = acceptHeader;
	}
	
	const protocolVersion = c.req.header('MCP-Protocol-Version');
	if (protocolVersion) {
		forwardHeaders['MCP-Protocol-Version'] = protocolVersion;
	}
	
	const sessionId = c.req.header('MCP-Session-Id');
	if (sessionId) {
		forwardHeaders['MCP-Session-Id'] = sessionId;
	}

	const awsResponse = await fetch(c.env.AWS_API_ENDPOINT, {
		method: 'POST',
		headers: forwardHeaders,
		body: body
	});

	// Return AWS response directly, preserving all important headers
	const responseHeaders = new Headers();
	const contentType = awsResponse.headers.get('Content-Type');
	if (contentType) {
		responseHeaders.set('Content-Type', contentType);
	}
	
	// Forward CORS headers
	responseHeaders.set('Access-Control-Allow-Origin', '*');
	responseHeaders.set('Access-Control-Allow-Credentials', 'true');

	return new Response(awsResponse.body, {
		status: awsResponse.status,
		headers: responseHeaders
	});
}
