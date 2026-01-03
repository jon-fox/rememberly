/**
 * Google OAuth integration
 * Users sign in with Google, then authorize MCP clients
 */

import { Context } from 'hono';
import { AuthDatabase } from './database';
import { generateSessionToken, storeSession } from './auth';

interface GoogleTokenResponse {
	access_token: string;
	expires_in: number;
	token_type: string;
	scope: string;
	refresh_token?: string;
}

interface GoogleUserInfo {
	id: string;
	email: string;
	verified_email: boolean;
	name: string;
	picture: string;
}

/**
 * Step 1: Redirect user to Google OAuth
 */
export async function handleGoogleLogin(c: Context) {
	const clientId = c.env.GOOGLE_CLIENT_ID;
	const redirectUri = `${c.env.MCP_BASE_URL}/auth/google/callback`;
	
	// Preserve MCP OAuth params if this is part of MCP flow
	const state = JSON.stringify({
		mcp_client_id: c.req.query('client_id'),
		mcp_redirect_uri: c.req.query('redirect_uri'),
		mcp_code_challenge: c.req.query('code_challenge'),
		mcp_state: c.req.query('state'),
		random: crypto.randomUUID() // CSRF protection
	});

	const params = new URLSearchParams({
		client_id: clientId,
		redirect_uri: redirectUri,
		response_type: 'code',
		scope: 'openid email profile',
		access_type: 'offline',
		prompt: 'consent',
		state: state
	});

	const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
	return c.redirect(googleAuthUrl);
}

/**
 * Step 2: Google redirects back with auth code
 */
export async function handleGoogleCallback(c: Context) {
	const code = c.req.query('code');
	const state = c.req.query('state');
	
	if (!code) {
		return c.json({ error: 'No authorization code received' }, 400);
	}

	// Parse state to get MCP OAuth params
	const stateData = JSON.parse(state || '{}');

	// Exchange code for Google access token
	const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({
			code,
			client_id: c.env.GOOGLE_CLIENT_ID,
			client_secret: c.env.GOOGLE_CLIENT_SECRET,
			redirect_uri: `${c.env.MCP_BASE_URL}/auth/google/callback`,
			grant_type: 'authorization_code'
		})
	});

	if (!tokenResponse.ok) {
		return c.json({ error: 'Failed to exchange code for token' }, 400);
	}

	const tokens: GoogleTokenResponse = await tokenResponse.json();

	// Get user info from Google
	const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
		headers: { Authorization: `Bearer ${tokens.access_token}` }
	});

	if (!userInfoResponse.ok) {
		return c.json({ error: 'Failed to get user info' }, 400);
	}

	const userInfo: GoogleUserInfo = await userInfoResponse.json();

	// Create or update user in Cloudflare D1
	const db = new AuthDatabase(c.env.DB);
	let user = await db.getUserByEmail(userInfo.email);

	if (!user) {
		// Create new user (no password for OAuth users)
		user = await db.createUser(userInfo.email, ''); // Empty password for OAuth users
	}

	// Generate session token
	const accessToken = generateSessionToken();
	await storeSession(accessToken, user.id, user.email, c.env.USER_CACHE);

	// Create/update user in AWS backend (DynamoDB + S3)
	// Match the format used by ui/js/auth.js
	try {
		const userServiceUrl = c.env.AWS_API_ENDPOINT.replace('/mcp', '/users');
		const response = await fetch(userServiceUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${accessToken}`
			},
			body: JSON.stringify({
				user_id: user.id,
				email: userInfo.email,
				username: userInfo.name || userInfo.email.split('@')[0]
			})
		});

		if (response.ok) {
			console.log('User created/updated in AWS backend successfully');
		} else {
			console.warn('Failed to create user in AWS backend:', response.status);
			// Don't fail the auth flow - user still exists in Cloudflare D1
		}
	} catch (error) {
		console.error('Error creating user in AWS backend:', error);
		// Don't fail the auth flow - user still exists in Cloudflare D1
	}

	// If this is part of MCP OAuth flow, redirect to consent page
	if (stateData.mcp_client_id) {
		const consentParams = new URLSearchParams({
			user_id: user.id,
			client_id: stateData.mcp_client_id,
			redirect_uri: stateData.mcp_redirect_uri,
			code_challenge: stateData.mcp_code_challenge,
			state: stateData.mcp_state || ''
		});

		return c.redirect(`/consent?${consentParams.toString()}`);
	}

	// Otherwise, this is a direct login - redirect to app with token
	return c.redirect(`https://rememberly.xyz/?token=${accessToken}`);
}

/**
 * Alternative: GitHub OAuth (similar pattern)
 */
export async function handleGitHubLogin(c: Context) {
	const clientId = c.env.GITHUB_CLIENT_ID;
	const redirectUri = `${c.env.MCP_BASE_URL}/auth/github/callback`;
	
	const state = JSON.stringify({
		mcp_client_id: c.req.query('client_id'),
		mcp_redirect_uri: c.req.query('redirect_uri'),
		mcp_code_challenge: c.req.query('code_challenge'),
		mcp_state: c.req.query('state'),
		random: crypto.randomUUID()
	});

	const params = new URLSearchParams({
		client_id: clientId,
		redirect_uri: redirectUri,
		scope: 'user:email',
		state: state
	});

	const githubAuthUrl = `https://github.com/login/oauth/authorize?${params.toString()}`;
	return c.redirect(githubAuthUrl);
}

export async function handleGitHubCallback(c: Context) {
	const code = c.req.query('code');
	const state = c.req.query('state');
	
	if (!code) {
		return c.json({ error: 'No authorization code received' }, 400);
	}

	const stateData = JSON.parse(state || '{}');

	// Exchange code for access token
	const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		},
		body: JSON.stringify({
			client_id: c.env.GITHUB_CLIENT_ID,
			client_secret: c.env.GITHUB_CLIENT_SECRET,
			code
		})
	});

	const tokens: any = await tokenResponse.json();

	// Get user info
	const userResponse = await fetch('https://api.github.com/user', {
		headers: {
			'Authorization': `Bearer ${tokens.access_token}`,
			'Accept': 'application/json'
		}
	});

	const githubUser: any = await userResponse.json();

	// Get primary email
	const emailResponse = await fetch('https://api.github.com/user/emails', {
		headers: {
			'Authorization': `Bearer ${tokens.access_token}`,
			'Accept': 'application/json'
		}
	});

	const emails: any = await emailResponse.json();
	const primaryEmail = emails.find((e: any) => e.primary)?.email || githubUser.email;

	// Create or get user
	const db = new AuthDatabase(c.env.DB);
	let user = await db.getUserByEmail(primaryEmail);

	if (!user) {
		user = await db.createUser(primaryEmail, '');
	}

	const accessToken = generateSessionToken();
	await storeSession(accessToken, user.id, user.email, c.env.USER_CACHE);

	// Redirect to consent or app
	if (stateData.mcp_client_id) {
		const consentParams = new URLSearchParams({
			token: accessToken,
			client_id: stateData.mcp_client_id,
			redirect_uri: stateData.mcp_redirect_uri,
			code_challenge: stateData.mcp_code_challenge,
			state: stateData.mcp_state || ''
		});

		return c.redirect(`/consent?${consentParams.toString()}`);
	}

	return c.redirect(`https://rememberly.xyz/?token=${accessToken}`);
}
