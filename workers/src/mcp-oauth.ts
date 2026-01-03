/**
 * MCP OAuth 2.1 Authorization Flow
 * Based on: https://developers.cloudflare.com/agents/model-context-protocol/authorization/
 */

import { Context } from 'hono';
import { AuthDatabase } from './database';
import { generateSessionToken, storeSession } from './auth';

interface AuthorizationRequest {
	response_type: 'code';
	client_id: string;
	redirect_uri: string;
	state?: string;
	code_challenge: string;
	code_challenge_method: 'S256';
	scope?: string;
}

interface TokenRequest {
	grant_type: 'authorization_code' | 'refresh_token';
	code?: string;
	refresh_token?: string;
	redirect_uri?: string;
	code_verifier?: string;
	client_id: string;
}

// In-memory store for auth codes (use KV in production)
const authCodes = new Map<string, {
	userId: string;
	clientId: string;
	redirectUri: string;
	codeChallenge: string;
	scopes: string[];
	expiresAt: number;
}>();

/**
 * Step 1: Authorization endpoint
 * MCP client redirects user here to authorize
 */
export async function handleAuthorize(c: Context) {
	const params = c.req.query() as unknown as AuthorizationRequest;
	
	// Validate OAuth parameters
	if (!params.client_id || !params.redirect_uri || !params.code_challenge) {
		return c.json({ error: 'invalid_request' }, 400);
	}

	if (params.code_challenge_method !== 'S256') {
		return c.json({ error: 'invalid_request', error_description: 'Only S256 supported' }, 400);
	}

	// Check if user is authenticated (get from session/cookie)
	const authHeader = c.req.header('Authorization');
	const token = authHeader?.replace('Bearer ', '');
	
	if (!token) {
		// Redirect to Google OAuth with MCP params preserved
		const loginUrl = `/auth/google?client_id=${params.client_id}&redirect_uri=${encodeURIComponent(params.redirect_uri)}&code_challenge=${params.code_challenge}&state=${params.state || ''}`;
		return c.redirect(loginUrl);
	}

	// User is authenticated, show consent page
	const consentUrl = `/consent?client_id=${params.client_id}&redirect_uri=${encodeURIComponent(params.redirect_uri)}&scope=${params.scope || ''}&state=${params.state || ''}`;
	return c.redirect(consentUrl);
}

/**
 * Step 2: User grants consent, generate auth code
 */
export async function handleConsent(c: Context) {
	const body = await c.req.json();
	const { userId, clientId, redirectUri, codeChallenge, scopes, approved, state } = body;

	if (!approved) {
		const errorUrl = `${redirectUri}?error=access_denied${state ? '&state=' + state : ''}`;
		return c.json({ redirect_url: errorUrl });
	}

	// Generate authorization code
	const code = crypto.randomUUID();
	const expiresAt = Date.now() + (10 * 60 * 1000); // 10 minutes

	authCodes.set(code, {
		userId,
		clientId,
		redirectUri,
		codeChallenge,
		scopes: scopes || [],
		expiresAt
	});

	// Return redirect URL for client to navigate to
	const params = new URLSearchParams({
		code,
		...(state && { state })
	});

	return c.json({ redirect_url: `${redirectUri}?${params.toString()}` });
}

/**
 * Step 3: Token endpoint
 * MCP client exchanges auth code for access token
 */
export async function handleToken(c: Context) {
	const body = await c.req.json<TokenRequest>();

	if (body.grant_type === 'authorization_code') {
		if (!body.code || !body.code_verifier || !body.redirect_uri) {
			return c.json({ error: 'invalid_request' }, 400);
		}

		const authCode = authCodes.get(body.code);
		if (!authCode) {
			return c.json({ error: 'invalid_grant' }, 400);
		}

		// Check expiration
		if (Date.now() > authCode.expiresAt) {
			authCodes.delete(body.code);
			return c.json({ error: 'invalid_grant', error_description: 'Code expired' }, 400);
		}

		// Verify PKCE challenge
		const hash = await crypto.subtle.digest(
			'SHA-256',
			new TextEncoder().encode(body.code_verifier)
		);
		const challenge = btoa(String.fromCharCode(...new Uint8Array(hash)))
			.replace(/\+/g, '-')
			.replace(/\//g, '_')
			.replace(/=/g, '');

		if (challenge !== authCode.codeChallenge) {
			return c.json({ error: 'invalid_grant', error_description: 'Invalid code_verifier' }, 400);
		}

		// Verify redirect URI matches
		if (body.redirect_uri !== authCode.redirectUri) {
			return c.json({ error: 'invalid_grant' }, 400);
		}

		// Generate access token
		const db = new AuthDatabase(c.env.DB);
		const user = await db.getUserById(authCode.userId);
		
		if (!user) {
			return c.json({ error: 'invalid_grant' }, 400);
		}

		const accessToken = generateSessionToken();
		await storeSession(accessToken, user.id, user.email, c.env.USER_CACHE);
		const refreshToken = crypto.randomUUID();
		const expiresIn = 24 * 60 * 60; // 24 hours

		// Store token in DB
		await db.storeToken(
			user.id,
			accessToken,
			Math.floor(Date.now() / 1000) + expiresIn,
			refreshToken,
			authCode.scopes
		);

		// Delete used auth code
		authCodes.delete(body.code);

		return c.json({
			access_token: accessToken,
			token_type: 'Bearer',
			expires_in: expiresIn,
			refresh_token: refreshToken,
			scope: authCode.scopes.join(' ')
		});
	}

	if (body.grant_type === 'refresh_token') {
		// Handle refresh token flow
		if (!body.refresh_token) {
			return c.json({ error: 'invalid_request' }, 400);
		}

		// TODO: Implement refresh token validation and new token generation
		return c.json({ error: 'unsupported_grant_type' }, 400);
	}

	return c.json({ error: 'unsupported_grant_type' }, 400);
}

/**
 * Client registration endpoint (optional)
 */
export async function handleRegister(c: Context) {
	const body = await c.req.json();
	
	// Generate client credentials
	const clientId = crypto.randomUUID();
	const clientSecret = crypto.randomUUID();

	// Store in KV or DB
	await c.env.USER_CACHE.put(`client:${clientId}`, JSON.stringify({
		client_id: clientId,
		client_secret: clientSecret,
		redirect_uris: body.redirect_uris || [],
		client_name: body.client_name || 'MCP Client',
		created_at: Date.now()
	}));

	return c.json({
		client_id: clientId,
		client_secret: clientSecret,
		client_name: body.client_name || 'MCP Client',
		redirect_uris: body.redirect_uris || []
	});
}
