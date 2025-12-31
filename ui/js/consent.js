// OAuth Consent Page Logic

console.log('================================');
console.log('PAGE: /oauth/consent.html LOADED');
console.log('================================');

let oauthParams = {};

async function loadAuthorizationRequest() {
    console.log('[CONSENT] loadAuthorizationRequest() called');
    try {
        // Initialize Supabase (from auth.js)
        if (!supabaseClient) {
            initSupabase();
        }
        
        // Listen for auth state changes
        console.log('[CONSENT] Setting up auth state listener...');
        supabaseClient.auth.onAuthStateChange((event, session) => {
            console.log('[CONSENT] Auth state change:', event);
            if (session) {
                console.log('[CONSENT] Session user:', session.user.email);
                console.log('[CONSENT] Reloading page after auth state change...');
                window.location.reload();
            }
        });
        
        // Wait for session initialization (especially after OAuth redirect)
        console.log('[CONSENT] Waiting 3 seconds for session to initialize...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        console.log('[CONSENT] Done waiting, checking session now...');

        // Parse OAuth parameters from URL
        const params = new URLSearchParams(window.location.search);
        const authorizationId = params.get('authorization_id');
        const clientName = params.get('client_name') || 'An application';
        
        oauthParams = { authorization_id: authorizationId };
        
        console.log('[CONSENT] OAuth params:', oauthParams);
        console.log('[CONSENT] Client name:', clientName);
        
        document.getElementById('client-name').textContent = clientName;
        document.getElementById('consent-client-name').textContent = clientName;

        // Check authentication status
        const session = await getCurrentSession();
        console.log('[CONSENT] Session check result:', session ? 'SESSION EXISTS' : 'NO SESSION');
        if (session?.user) {
            console.log('[CONSENT] User email:', session.user.email);
        }
        
        if (session?.user) {
            // User is authenticated - auto-approve for first-party MCP connections
            console.log('[CONSENT] User authenticated:', session.user.email);
            console.log('[CONSENT] Client name for check:', clientName);
            
            // Check if this is the first-party MCP server (auto-approve)
            if (clientName.toLowerCase().includes('rememberly') || clientName === 'An application') {
                console.log('[CONSENT] First-party app detected - will auto-approve');
                try {
                    await autoApproveAuthorization(session, authorizationId);
                } catch (err) {
                    console.error('[CONSENT] Auto-approve failed, falling back to manual consent');
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
    const consentUrl = window.location.href.split('?')[0];
    const params = new URLSearchParams(window.location.search);
    
    const googleBtn = document.getElementById('googleSignIn');
    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            try {
                sessionStorage.setItem('oauth_params', JSON.stringify(Object.fromEntries(params)));
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
                sessionStorage.setItem('oauth_params', JSON.stringify(Object.fromEntries(params)));
                await signInWithOAuth('github', consentUrl);
            } catch (error) {
                console.error('GitHub OAuth error:', error);
                showError('Failed to sign in with GitHub');
            }
        });
    }

    // Restore OAuth params from session storage
    const storedParams = sessionStorage.getItem('oauth_params');
    if (storedParams && !window.location.search) {
        const restoredParams = new URLSearchParams(JSON.parse(storedParams));
        window.location.search = restoredParams.toString();
    }

    loadAuthorizationRequest();
});

// Button handlers that call auth.js functions
window.handleApproveClick = async function() {
    try {
        const session = await getCurrentSession();
        await approveAuthorization(oauthParams.authorization_id, session);
    } catch (err) {
        showError(err.message || 'Failed to approve authorization');
    }
};

window.handleDenyClick = async function() {
    try {
        await denyAuthorization(oauthParams.authorization_id);
    } catch (err) {
        showError(err.message || 'Failed to deny authorization');
    }
};
