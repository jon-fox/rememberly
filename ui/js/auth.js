// Cloudflare Workers Authentication Module
// Replaces Supabase with custom JWT-based auth

// Auth client state
let authClient = null;
let authInitialized = false;

// Get configuration
function getAuthConfig() {
    // Try to get from config.js if available
    if (typeof CONFIG !== 'undefined' && CONFIG.api) {
        console.log('Using CONFIG from config.js:', CONFIG.api.baseUrl);
        return CONFIG.api;
    }
    
    // Fallback to direct configuration
    console.warn('CONFIG not found, using fallback configuration');
    const config = {
        baseUrl: 'https://mcp.rememberly.xyz',
        apiUrl: 'https://mcp.rememberly.xyz/api'
    };
    
    return config;
}

// Initialize auth client
function initAuth() {
    if (authInitialized) {
        return authClient;
    }
    
    const config = getAuthConfig();
    
    authClient = {
        baseUrl: config.baseUrl,
        apiUrl: config.apiUrl,
        storageKey: 'rememberly-auth-token'
    };
    
    authInitialized = true;
    console.log('Auth client initialized');
    return authClient;
}

// Get current user session
async function getCurrentSession() {
    if (!authClient) {
        console.error('Auth client not initialized');
        return null;
    }
    
    const token = localStorage.getItem(authClient.storageKey);
    if (!token) {
        return null;
    }
    
    try {
        // Verify token with backend
        const response = await fetch(`${authClient.apiUrl}/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            localStorage.removeItem(authClient.storageKey);
            return null;
        }
        
        const data = await response.json();
        return { user: data.user, token };
    } catch (error) {
        console.error('Error verifying session:', error.message);
        return null;
    }
}

// Get current user
async function getCurrentUser() {
    const session = await getCurrentSession();
    return session?.user || null;
}

// Sign up with email and password
async function signUp(email, password, userData = {}) {
    if (!authClient) {
        throw new Error('Auth client not initialized');
    }
    
    const response = await fetch(`${authClient.apiUrl}/auth/signup`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email,
            password,
            userData
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Signup failed');
    }
    
    const data = await response.json();
    if (data.token) {
        localStorage.setItem(authClient.storageKey, data.token);
    }
    
    return data;
}

// Sign in with email and password
async function signIn(email, password) {
    if (!authClient) {
        throw new Error('Auth client not initialized');
    }
    
    const response = await fetch(`${authClient.apiUrl}/auth/signin`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email,
            password
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Signin failed');
    }
    
    const data = await response.json();
    if (data.token) {
        localStorage.setItem(authClient.storageKey, data.token);
    }
    
    return data;
}

// Sign out
async function signOut() {
    if (!authClient) {
        throw new Error('Auth client not initialized');
    }
    
    localStorage.removeItem(authClient.storageKey);
    
    // Optional: notify backend
    const token = localStorage.getItem(authClient.storageKey);
    if (token) {
        try {
            await fetch(`${authClient.apiUrl}/auth/signout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Error signing out from backend:', error);
        }
    }
}

// Listen to auth state changes (simplified for custom auth)
function onAuthStateChange(callback) {
    if (!authClient) {
        console.error('Auth client not initialized');
        return null;
    }
    
    // Check for session changes periodically
    const interval = setInterval(async () => {
        const session = await getCurrentSession();
        callback(session ? 'SIGNED_IN' : 'SIGNED_OUT', session);
    }, 5000); // Check every 5 seconds
    
    return {
        unsubscribe: () => clearInterval(interval)
    };
}

// Update user metadata
async function updateUserMetadata(metadata) {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized');
    }
    
    const { data, error } = await supabaseClient.auth.updateUser({
        data: metadata
    });
    
    if (error) {
        throw error;
    }
    
    return data;
}

// Check if user is authenticated
async function isAuthenticated() {
    // Ensure client is initialized
    if (!supabaseClient && typeof initSupabase === 'function') {
        initSupabase();
    }
    
    const session = await getCurrentSession();
    return session !== null;
}

// Get access token for API calls
async function getAccessToken() {
    const session = await getCurrentSession();
    return session?.access_token || null;
}

// Redirect to login page if not authenticated
async function requireAuth(redirectUrl = 'login.html') {
    const authenticated = await isAuthenticated();
    if (!authenticated) {
        window.location.href = redirectUrl;
        return false;
    }
    return true;
}

// Sign in with OAuth provider (Google, GitHub, etc.)
async function signInWithOAuth(provider, redirectTo = null) {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized');
    }
    
    const options = redirectTo ? { redirectTo } : {};
    
    const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: provider,
        options: options
    });
    
    if (error) {
        throw error;
    }
    
    return data;
}

// Create or update user in DynamoDB
async function ensureUserInDatabase(user, accessToken, username = null) {
    if (!user || !accessToken) {
        console.error('User or access token missing');
        return false;
    }
    
    try {
        const apiEndpoint = 'https://api.rememberly.xyz/users';
        const payload = {
            user_id: user.id,
            email: user.email,
            username: username || user.user_metadata?.full_name || user.user_metadata?.name || user.email.split('@')[0]
        };
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            console.log('User created/updated in DynamoDB successfully');
            return true;
        } else {
            console.warn('Failed to create user in DynamoDB:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error creating user in DynamoDB:', error);
        return false;
    }
}

// Auto-approve OAuth authorization for first-party apps
async function autoApproveAuthorization(session, authorizationId, oauthParams) {
    try {
        console.log('[AUTH] Auto-approve started');
        console.log('[AUTH] Session user:', session.user.email);
        console.log('[AUTH] OAuth params:', oauthParams);
        
        const user = session.user;
        
        // Create user in DynamoDB
        if (session?.access_token) {
            console.log('[AUTH] Creating user in DynamoDB...');
            await ensureUserInDatabase(user, session.access_token);
            console.log('[AUTH] User creation completed');
        }
        
        // Call our custom consent endpoint with OAuth parameters
        console.log('[AUTH] Calling custom consent endpoint...');
        const response = await fetch(`${API_BASE_URL}/consent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: user.id,
                clientId: oauthParams.client_id,
                redirectUri: oauthParams.redirect_uri,
                codeChallenge: oauthParams.code_challenge,
                scopes: oauthParams.scope ? oauthParams.scope.split(' ') : [],
                state: oauthParams.state,
                approved: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to approve authorization');
        }
        
        const data = await response.json();
        if (!data.redirect_url) {
            throw new Error('No redirect URL returned from consent endpoint');
        }
        
        console.log('[AUTH] Redirecting to client callback:', data.redirect_url);
        window.location.href = data.redirect_url;
        return true;
        
    } catch (err) {
        console.error('[AUTH] Auto-approve failed:', err);
        throw err;
    }
}

// Approve OAuth authorization (manual)
async function approveAuthorization(authorizationId, session) {
    try {
        console.log('[AUTH] Manual approve started');
        
        const user = session?.user || await getCurrentUser();
        
        if (!user) {
            throw new Error('User authentication error');
        }

        // Create user in DynamoDB
        if (session?.access_token) {
            console.log('[AUTH] Creating user in DynamoDB...');
            await ensureUserInDatabase(user, session.access_token);
        }
        
        console.log('[AUTH] Approving authorization...');
        
        // Get OAuth params from URL
        const params = new URLSearchParams(window.location.search);
        const clientId = params.get('client_id');
        const redirectUri = params.get('redirect_uri');
        const codeChallenge = params.get('code_challenge');
        const state = params.get('state');
        const scope = params.get('scope');
        
        // Call our custom consent endpoint
        const response = await fetch(`${API_BASE_URL}/consent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: user.id,
                clientId: clientId,
                redirectUri: redirectUri,
                codeChallenge: codeChallenge,
                scopes: scope ? scope.split(' ') : [],
                state: state,
                approved: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to approve authorization');
        }
        
        // The response should be a redirect, follow it
        if (response.redirected) {
            window.location.href = response.url;
            return true;
        }
        
        // If not redirected, try to get redirect URL from response
        const data = await response.json();
        const redirectUrl = data.redirect_url || data.redirect_to;
        if (redirectUrl) {
            window.location.href = redirectUrl;
            return true;
        } else {
            throw new Error('No redirect URL provided');
        }
    } catch (err) {
        console.error('[AUTH] Error approving authorization:', err);
        throw err;
    }
}

// Deny OAuth authorization
async function denyAuthorization(authorizationId) {
    try {
        // Get OAuth params from URL
        const params = new URLSearchParams(window.location.search);
        const clientId = params.get('client_id');
        const redirectUri = params.get('redirect_uri');
        const codeChallenge = params.get('code_challenge');
        const state = params.get('state');
        
        const user = await getCurrentUser();
        
        // Call our custom consent endpoint with denied flag
        const response = await fetch(`${API_BASE_URL}/consent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: user?.id,
                clientId: clientId,
                redirectUri: redirectUri,
                codeChallenge: codeChallenge,
                state: state,
                approved: false
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to deny authorization');
        }
        
        console.log('[AUTH] Authorization denied');
        sessionStorage.removeItem('oauth_params');
        
        // The response should be a redirect, follow it
        if (response.redirected) {
            window.location.href = response.url;
            return true;
        }
        
        // If not redirected, try to get redirect URL from response
        const data = await response.json();
        const redirectUrl = data.redirect_url || data.redirect_to;
        if (redirectUrl) {
            window.location.href = redirectUrl;
            return true;
        } else {
            throw new Error('No redirect URL provided');
        }
    } catch (err) {
        console.error('[AUTH] Error denying authorization:', err);
        throw err;
    }
}

// Initialize Supabase when needed (called by pages that need it)
// Don't auto-initialize to avoid errors on pages that don't load Supabase library

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initSupabase,
        getCurrentSession,
        getCurrentUser,
        signUp,
        signIn,
        signOut,
        onAuthStateChange,
        updateUserMetadata,
        isAuthenticated,
        getAccessToken,
        requireAuth,
        supabaseClient
    };
}