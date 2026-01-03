/**
 * Rememberly MCP Server on Cloudflare Workers
 * Authentication proxy - data stays in AWS
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { AuthDatabase } from './database';
import { generateSessionToken, storeSession, verifyToken, extractBearerToken } from './auth';

type Bindings = {
	DB: D1Database;
	USER_CACHE: KVNamespace;
	GOOGLE_CLIENT_ID: string;
	GOOGLE_CLIENT_SECRET: string;
	GITHUB_CLIENT_ID?: string;
	GITHUB_CLIENT_SECRET?: string;
	ENVIRONMENT: string;
	MCP_BASE_URL: string;
	AWS_API_ENDPOINT: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// CORS middleware
app.use('*', cors({
	origin: ['https://rememberly.xyz', 'http://localhost:3000'],
	credentials: true,
}));

// Health check
app.get('/health', (c) => {
	return c.json({ status: 'healthy', service: 'rememberly-auth' });
});

// Auth endpoints
app.post('/api/auth/signup', async (c) => {
	const { email, password } = await c.req.json();
	const db = new AuthDatabase(c.env.DB);
	
	// Check if user exists
	const existing = await db.getUserByEmail(email);
	if (existing) {
		return c.json({ error: 'User already exists' }, 400);
	}
	
	// Hash password (in production, use bcrypt or similar)
	const passwordHash = await crypto.subtle.digest(
		'SHA-256',
		new TextEncoder().encode(password)
	).then(buf => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join(''));
	
	const user = await db.createUser(email, passwordHash);
	const token = generateSessionToken();
	await storeSession(token, user.id, user.email, c.env.USER_CACHE);
	
	return c.json({ user: { id: user.id, email: user.email }, token });
});

app.post('/api/auth/signin', async (c) => {
	const { email, password } = await c.req.json();
	const db = new AuthDatabase(c.env.DB);
	
	const user = await db.getUserByEmail(email);
	if (!user) {
		return c.json({ error: 'Invalid credentials' }, 401);
	}
	
	// Verify password
	const passwordHash = await crypto.subtle.digest(
		'SHA-256',
		new TextEncoder().encode(password)
	).then(buf => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join(''));
	
	if (passwordHash !== user.password_hash) {
		return c.json({ error: 'Invalid credentials' }, 401);
	}
	
	await db.updateLastLogin(user.id);
	const token = generateSessionToken();
	await storeSession(token, user.id, user.email, c.env.USER_CACHE);
	
	return c.json({ user: { id: user.id, email: user.email }, token });
});

app.post('/api/auth/verify', async (c) => {
	const authHeader = c.req.header('Authorization');
	const token = extractBearerToken(authHeader || null);
	
	if (!token) {
		return c.json({ error: 'No token provided' }, 401);
	}
	
	const claims = await verifyToken(token, c.env.USER_CACHE);
	if (!claims) {
		return c.json({ error: 'Invalid token' }, 401);
	}
	
	return c.json({ user: { id: claims.sub, email: claims.email } });
});

app.post('/api/auth/signout', async (c) => {
	// Just acknowledge - client removes token
	return c.json({ success: true });
});

// Get current user info from token
app.get('/api/auth/user', async (c) => {
	const authHeader = c.req.header('Authorization');
	if (!authHeader?.startsWith('Bearer ')) {
		return c.json({ error: 'Unauthorized' }, 401);
	}
	
	const token = authHeader.replace('Bearer ', '');
	const session = await c.env.USER_CACHE.get(token);
	
	if (!session) {
		return c.json({ error: 'Invalid or expired token' }, 401);
	}
	
	const sessionData = JSON.parse(session);
	const db = new AuthDatabase(c.env.DB);
	const user = await db.getUserById(sessionData.userId);
	
	if (!user) {
		return c.json({ error: 'User not found' }, 404);
	}
	
	return c.json({
		id: user.id,
		email: user.email,
		created_at: user.created_at
	});
});

// MCP OAuth endpoints (for MCP clients)
import { handleAuthorize, handleConsent, handleToken, handleRegister } from './mcp-oauth';
import { handleMCP } from './mcp-server';
import { handleGoogleLogin, handleGoogleCallback, handleGitHubLogin, handleGitHubCallback } from './google-oauth';

// Google OAuth (users sign in with Google first)
app.get('/auth/google', handleGoogleLogin);
app.get('/auth/google/callback', handleGoogleCallback);

// GitHub OAuth (alternative)
app.get('/auth/github', handleGitHubLogin);
app.get('/auth/github/callback', handleGitHubCallback);

// MCP OAuth endpoints
app.get('/authorize', handleAuthorize);
app.get('/consent', async (c) => {
	// Redirect to the actual consent page on the main domain with all query params
	const params = c.req.query();
	const queryString = new URLSearchParams(params).toString();
	const consentUrl = `https://rememberly.xyz/oauth/consent.html${queryString ? '?' + queryString : ''}`;
	
	return c.redirect(consentUrl);
});
app.post('/consent', handleConsent);
app.post('/token', handleToken);
app.post('/register', handleRegister);

// MCP protocol endpoint
app.post('/mcp', handleMCP);

// Proxy to AWS API with auth
app.all('/api/*', async (c) => {
	const authHeader = c.req.header('Authorization');
	const token = extractBearerToken(authHeader || null);
	
	if (!token) {
		return c.json({ error: 'Unauthorized' }, 401);
	}
	
	const claims = await verifyToken(token, c.env.USER_CACHE);
	if (!claims) {
		return c.json({ error: 'Invalid token' }, 401);
	}
	
	// Forward to AWS API with user ID
	const url = new URL(c.req.url);
	const awsUrl = `${c.env.AWS_API_ENDPOINT}${url.pathname}${url.search}`;
	
	const response = await fetch(awsUrl, {
		method: c.req.method,
		headers: {
			'Content-Type': 'application/json',
			'X-User-Id': claims.sub,
		},
		body: c.req.method !== 'GET' ? await c.req.text() : undefined,
	});
	
	return new Response(response.body, {
		status: response.status,
		headers: response.headers,
	});
});

export default {
	async fetch(request: Request, env: Bindings, ctx: ExecutionContext): Promise<Response> {
		return app.fetch(request, env, ctx);
	},
} satisfies ExportedHandler<Bindings>;
