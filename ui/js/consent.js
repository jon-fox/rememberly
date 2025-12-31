// OAuth Consent Page Logic

console.log('================================');
console.log('PAGE: /oauth/consent.html LOADED');
console.log('================================');

let oauthParams = {};
let approvalInProgress = false;

async function loadAuthorizationRequest() {
    console.log('[CONSENT] loadAuthorizationRequest() called');
    
    // Prevent multiple simultaneous calls
    if (approvalInProgress) {
        console.log('[CONSENT] Approval already in progress, skipping...');
        return;
    }
    
    try {
        // Initialize Supabase (from auth.js)
        if (!supabaseClient) {
            initSupabase();
        }
        
        // Parse OAuth parameters from URL first
        const params = new URLSearchParams(window.location.search);
        
        // Log everything to understand the flow
        console.log('[CONSENT] Full URL:', window.location.href);
        console.log('[CONSENT] All params:', Object.fromEntries(params.entries()));
        
        const authorizationId = params.get('authorization_id');
        const clientName = params.get('client_name') || 'An application';
        const redirectUri = params.get('redirect_uri');
        const state = params.get('state');
        const scope = params.get('scope');
        
        oauthParams = { 
            authorization_id: authorizationId,
            redirect_uri: redirectUri,
            state: state,
            scope: scope
        };
        
        console.log('[CONSENT] OAuth params:', oauthParams);
        console.log('[CONSENT] Client name:', clientName);
        
        if (!authorizationId) {
            console.error('[CONSENT] No authorization_id in URL');
            showError('Invalid authorization request');
            return;
        }
        
        document.getElementById('client-name').textContent = clientName;
        document.getElementById('consent-client-name').textContent = clientName;

        // Check if we just came back from OAuth provider (has hash fragment)
        const hasOAuthCallback = window.location.hash.includes('access_token') || window.location.hash.includes('error');
        console.log('[CONSENT] Has OAuth callback in URL?', hasOAuthCallback);
        
        // Wait for session initialization (especially after OAuth redirect)
        const waitTime = hasOAuthCallback ? 2500 : 500;
        console.log(`[CONSENT] Waiting ${waitTime}ms for session to initialize...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        console.log('[CONSENT] Done waiting, checking session now...');

        // Check authentication status
        const session = await getCurrentSession();
        console.log('[CONSENT] Session check result:', session ? 'SESSION EXISTS' : 'NO SESSION');
        if (session?.user) {
            console.log('[CONSENT] User email:', session.user.email);
            console.log('[CONSENT] User created at:', session.user.created_at);
            console.log('[CONSENT] Just came back from OAuth?', hasOAuthCallback);
        }
        
        if (session?.user) {
            // User is authenticated - auto-approve for first-party MCP connections
            console.log('[CONSENT] User authenticated:', session.user.email);
            console.log('[CONSENT] Client name for check:', clientName);
            
            // Check if this is the first-party MCP server (auto-approve)
            if (clientName.toLowerCase().includes('rememberly') || clientName === 'An application') {
                console.log('[CONSENT] First-party app detected - will auto-approve');
                approvalInProgress = true;
                try {
                    await autoApproveAuthorization(session, authorizationId, oauthParams);
                    // If we get here, approval succeeded and we're being redirected
                    // No need to do anything else
                } catch (err) {
                    approvalInProgress = false;
                    console.error('[CONSENT] Auto-approve failed:', err);
                    
                    // Check if this is an authorization not found error
                    if (err && (err.code === 'oauth_authorization_not_found' || 
                                (err.message && err.message.toLowerCase().includes('not found')))) {
                        showError('This authorization request has expired or already been used. Please try connecting again.');
                        return;
                    }
                    
                    // For other errors, show manual consent as fallback
                    console.log('[CONSENT] Showing manual consent as fallback');
                    showConsentScreen(session.user.email);
                }
            } else {
                // Third-party app - show consent screen
                console.log('[CONSENT] Third-party app - showing consent screen');
                showConsentScreen(session.user.email);
            }
        } else {
            // User is not authenticated - show login form
            console.log('[CONSENT] Not authenticated - showing login');
            sessionStorage.setItem('oauth_params', JSON.stringify(oauthParams));
            document.getElementById('loading').style.display = 'none';
            document.getElementById('auth-section').style.display = 'block';
        }

    } catch (err) {
        console.error('[CONSENT] Error:', err);
        showError('Failed to load authorization request');
    }
}

function showConsentScreen(userEmail) {
    document.getElementById('user-email').textContent = userEmail;
    document.getElementById('loading').style.display = 'none';
    document.getElementById('consent-section').style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
    const loginError = document.getElementById('loginError');
    if (loginError) {
        loginError.textContent = message;
    }
    document.getElementById('loading').style.display = 'none';
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('consent-section').style.display = 'none';
}

// Handle email/password login
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const loginError = document.getElementById('loginError');
            if (loginError) loginError.textContent = '';

            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                await signIn(email, password);
                window.location.reload();
            } catch (error) {
                console.error('Login error:', error);
                if (loginError) loginError.textContent = error.message || 'Failed to sign in';
            }
        });
    }

    // OAuth buttons - redirect back to consent page after OAuth
    const consentUrl = window.location.href.split('?')[0] + window.location.search;
    const params = new URLSearchParams(window.location.search);
    
    const googleBtn = document.getElementById('googleSignIn');
    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            try {
                // Store the authorization params so we can restore them after OAuth
                sessionStorage.setItem('oauth_authorization_id', params.get('authorization_id'));
                sessionStorage.setItem('oauth_client_name', params.get('client_name') || 'An application');
                await signInWithOAuth('google', consentUrl);
            } catch (error) {
                console.error('Google OAuth error:', error);
                showError('Failed to sign in with Google');
            }
        });
    }
    
    const githubBtn = document.getElementById('githubSignIn');
    if (githubBtn) {
        githubBtn.addEventListener('click', async () => {
            try {
                // Store the authorization params so we can restore them after OAuth
                sessionStorage.setItem('oauth_authorization_id', params.get('authorization_id'));
                sessionStorage.setItem('oauth_client_name', params.get('client_name') || 'An application');
                await signInWithOAuth('github', consentUrl);
            } catch (error) {
                console.error('GitHub OAuth error:', error);
                showError('Failed to sign in with GitHub');
            }
        });
    }

    loadAuthorizationRequest();
});

// Button handlers that call auth.js functions
window.handleApproveClick = async function() {
    if (approvalInProgress) {
        console.log('[CONSENT] Approval already in progress');
        return;
    }
    
    approvalInProgress = true;
    try {
        const session = await getCurrentSession();
        await approveAuthorization(oauthParams.authorization_id, session);
    } catch (err) {
        approvalInProgress = false;
        showError(err.message || 'Failed to approve authorization');
    }
};

window.handleDenyClick = async function() {
    if (approvalInProgress) {
        console.log('[CONSENT] Operation already in progress');
        return;
    }
    
    approvalInProgress = true;
    try {
        await denyAuthorization(oauthParams.authorization_id);
    } catch (err) {
        approvalInProgress = false;
        showError(err.message || 'Failed to deny authorization');
    }
};
