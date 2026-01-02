/**
 * Authentication utilities for Cloudflare Workers
 * Uses session tokens instead of JWT - simpler and no secret management
 */

export interface AuthClaims {
	sub: string; // user ID
	email: string;
	iat: number;
	exp: number;
}

/**
 * Generate a secure session token (just a random UUID)
 * Store the session data in KV instead of encoding it in the token
 */
export function generateSessionToken(): string {
	return crypto.randomUUID();
}

/**
 * Verify token by looking it up in KV
 */
export async function verifyToken(
	token: string,
	kv: KVNamespace
): Promise<AuthClaims | null> {
	try {
		const sessionData = await kv.get(`session:${token}`, 'json');
		if (!sessionData) {
			return null;
		}

		const claims = sessionData as AuthClaims;
		const now = Math.floor(Date.now() / 1000);

		if (claims.exp < now) {
			await kv.delete(`session:${token}`);
			return null;
		}

		return claims;
	} catch (error) {
		console.error('Token verification failed:', error);
		return null;
	}
}

/**
 * Store session in KV
 */
export async function storeSession(
	token: string,
	userId: string,
	email: string,
	kv: KVNamespace,
	ttl: number = 86400 // 24 hours
): Promise<void> {
	const now = Math.floor(Date.now() / 1000);
	const session: AuthClaims = {
		sub: userId,
		email,
		iat: now,
		exp: now + ttl
	};

	await kv.put(`session:${token}`, JSON.stringify(session), {
		expirationTtl: ttl
	});
}

/**
 * Revoke session
 */
export async function revokeSession(token: string, kv: KVNamespace): Promise<void> {
	await kv.delete(`session:${token}`);
}

export function extractBearerToken(authHeader: string | null): string | null {
	if (!authHeader || !authHeader.startsWith('Bearer ')) {
		return null;
	}
	return authHeader.substring(7);
}
