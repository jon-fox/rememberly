// OAuth Consent Page Logic
// Purpose: After Google OAuth, auto-approve MCP connection and redirect back to client

let approvalInProgress = false;

async function loadAuthorizationRequest() {
    if (approvalInProgress) return;
    
    try {
        const params = new URLSearchParams(window.location.search);
        
        // Get params from Google OAuth callback
        const userId = params.get('user_id');
        const clientId = params.get('client_id');
        const redirectUri = params.get('redirect_uri');
        const codeChallenge = params.get('code_challenge');
        const state = params.get('state');
        
        if (!userId || !clientId || !redirectUri || !codeChallenge) {
            showError('Invalid authorization request - missing parameters');
            return;
        }
        
        // Auto-approve and get redirect URL
        approvalInProgress = true;
        const consentResponse = await fetch(`${API_BASE_URL}/consent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userId: userId,
                clientId: clientId,
                redirectUri: redirectUri,
                codeChallenge: codeChallenge,
                scopes: ['mcp'],
                state: state,
                approved: true
            })
        });
        
        if (!consentResponse.ok) {
            throw new Error('Failed to approve authorization');
        }
        
        const { redirect_url } = await consentResponse.json();
        
        // Redirect back to MCP client
        window.location.href = redirect_url;
        
    } catch (err) {
        console.error('[CONSENT] Error:', err);
        showError('Authorization failed: ' + err.message);
        approvalInProgress = false;
    }
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

// Start the flow when page loads
document.addEventListener('DOMContentLoaded', loadAuthorizationRequest);
