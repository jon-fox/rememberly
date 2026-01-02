/**
 * Database utilities for D1
 * Auth only - data stays in AWS
 */

export interface User {
	id: string;
	email: string;
	password_hash: string;
	created_at: number;
	updated_at: number;
	last_login?: number;
}

export interface OAuthToken {
	id: number;
	user_id: string;
	access_token: string;
	refresh_token?: string;
	expires_at: number;
	created_at: number;
	scopes?: string;
}

export class AuthDatabase {
	constructor(private db: D1Database) {}

	async getUserByEmail(email: string): Promise<User | null> {
		const result = await this.db
			.prepare('SELECT * FROM users WHERE email = ?')
			.bind(email)
			.first<User>();
		return result;
	}

	async getUserById(userId: string): Promise<User | null> {
		const result = await this.db
			.prepare('SELECT * FROM users WHERE id = ?')
			.bind(userId)
			.first<User>();
		return result;
	}

	async createUser(email: string, passwordHash: string): Promise<User> {
		const id = crypto.randomUUID();
		const now = Math.floor(Date.now() / 1000);
		
		await this.db
			.prepare('INSERT INTO users (id, email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)')
			.bind(id, email, passwordHash, now, now)
			.run();
		
		return { id, email, password_hash: passwordHash, created_at: now, updated_at: now };
	}

	async updateLastLogin(userId: string): Promise<void> {
		const now = Math.floor(Date.now() / 1000);
		await this.db
			.prepare('UPDATE users SET last_login = ? WHERE id = ?')
			.bind(now, userId)
			.run();
	}

	async storeToken(userId: string, accessToken: string, expiresAt: number, refreshToken?: string, scopes?: string[]): Promise<OAuthToken> {
		const now = Math.floor(Date.now() / 1000);
		const scopesJson = scopes ? JSON.stringify(scopes) : null;
		
		const result = await this.db
			.prepare('INSERT INTO oauth_tokens (user_id, access_token, refresh_token, expires_at, created_at, scopes) VALUES (?, ?, ?, ?, ?, ?)')
			.bind(userId, accessToken, refreshToken || null, expiresAt, now, scopesJson)
			.run();
		
		return {
			id: result.meta.last_row_id as number,
			user_id: userId,
			access_token: accessToken,
			refresh_token: refreshToken,
			expires_at: expiresAt,
			created_at: now,
			scopes: scopesJson || undefined,
		};
	}

	async getTokenByAccessToken(accessToken: string): Promise<OAuthToken | null> {
		const result = await this.db
			.prepare('SELECT * FROM oauth_tokens WHERE access_token = ?')
			.bind(accessToken)
			.first<OAuthToken>();
		return result;
	}

	async revokeToken(accessToken: string): Promise<boolean> {
		const result = await this.db
			.prepare('DELETE FROM oauth_tokens WHERE access_token = ?')
			.bind(accessToken)
			.run();
		return result.success;
	}

	async cleanupExpiredTokens(): Promise<void> {
		const now = Math.floor(Date.now() / 1000);
		await this.db
			.prepare('DELETE FROM oauth_tokens WHERE expires_at < ?')
			.bind(now)
			.run();
	}
}
