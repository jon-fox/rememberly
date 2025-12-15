// Create user in DynamoDB via API - defined globally so it can be used before DOM loads
async function createUserInDatabase(user, accessToken, username = null) {
    console.log('>>>>> createUserInDatabase CALLED <<<<<');
    console.log('User parameter:', user);
    console.log('Access token (first 20 chars):', accessToken?.substring(0, 20) + '...');
    console.log('Username parameter:', username);
    
    try {
        const apiEndpoint = 'https://mcp.rememberly.app/users';
        const payload = {
            user_id: user.id,
            email: user.email,
            username: username || user.user_metadata?.full_name || user.email.split('@')[0]
        };
        
        console.log('API Endpoint:', apiEndpoint);
        console.log('Payload:', JSON.stringify(payload, null, 2));
        console.log('Authorization header present:', !!accessToken);
        
        console.log('Sending fetch request...');
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(payload)
        });
        
        console.log('Fetch completed!');
        console.log('Response status:', response.status);
        console.log('Response statusText:', response.statusText);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('SUCCESS: User created/updated in DynamoDB:', responseData);
            return true;
        } else {
            const errorText = await response.text();
            console.error('FAILED: Status:', response.status, 'Response:', errorText);
            return false;
        }
    } catch (error) {
        console.error('EXCEPTION in createUserInDatabase:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        return false;
    }
}

// Login page functionality
document.addEventListener('DOMContentLoaded', async () => {
    console.log('=== LOGIN PAGE LOADED ===');
    
    // Get redirect URL from query params
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get('redirect') || 'index.html';
    console.log('Redirect URL:', redirectUrl);
    
    // Check if user is already authenticated
    console.log('Checking authentication status...');
    const authenticated = await isAuthenticated();
    console.log('Is authenticated:', authenticated);
    
    if (authenticated) {
        console.log('User is authenticated, getting user details...');
        // User just logged in (possibly via OAuth), ensure they're in the database
        const user = await getCurrentUser();
        const session = await getCurrentSession();
        
        console.log('User object:', user);
        console.log('Session object:', session);
        console.log('Has access token:', !!session?.access_token);
        
        if (user && session?.access_token) {
            console.log('===== CALLING createUserInDatabase =====');
            // Try to create user in database (this is idempotent)
            const result = await createUserInDatabase(user, session.access_token);
            console.log('createUserInDatabase result:', result);
        } else {
            console.warn('Missing user or access token - user:', !!user, 'token:', !!session?.access_token);
        }
        
        console.log('Redirecting to:', redirectUrl);
        // Redirect to the intended page if already logged in
        window.location.href = redirectUrl;
        return;
    }
    
    console.log('User not authenticated, showing login forms');

    // DOM elements
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');
    const showSignUpLink = document.getElementById('showSignUp');
    const showSignInLink = document.getElementById('showSignIn');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginError = document.getElementById('loginError');
    const registerError = document.getElementById('registerError');
    const registerSuccess = document.getElementById('registerSuccess');
    const googleSignInBtn = document.getElementById('googleSignIn');
    const githubSignInBtn = document.getElementById('githubSignIn');

    // Toggle between sign in and sign up forms
    showSignUpLink.addEventListener('click', (e) => {
        e.preventDefault();
        signInForm.classList.remove('active');
        signUpForm.classList.add('active');
        clearMessages();
    });

    showSignInLink.addEventListener('click', (e) => {
        e.preventDefault();
        signUpForm.classList.remove('active');
        signInForm.classList.add('active');
        clearMessages();
    });

    // Clear all error/success messages
    function clearMessages() {
        loginError.textContent = '';
        registerError.textContent = '';
        registerSuccess.textContent = '';
    }

    // Show loading state on button
    function setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }

    // Handle sign in
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessages();

        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const submitButton = loginForm.querySelector('button[type="submit"]');

        try {
            setButtonLoading(submitButton, true);
            
            const { user, session } = await signIn(email, password);
            
            console.log('Sign in successful:', user);
            
            // Ensure user exists in DynamoDB
            if (session?.access_token) {
                await createUserInDatabase(user, session.access_token);
            }
            
            // Redirect to intended page
            window.location.href = redirectUrl;
        } catch (error) {
            console.error('Sign in error:', error);
            loginError.textContent = error.message || 'Failed to sign in. Please check your credentials.';
            setButtonLoading(submitButton, false);
        }
    });

    // Handle sign up
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessages();

        const name = document.getElementById('registerName').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const agreeTerms = document.getElementById('agreeTerms').checked;
        const submitButton = registerForm.querySelector('button[type="submit"]');

        // Validation
        if (password !== confirmPassword) {
            registerError.textContent = 'Passwords do not match.';
            return;
        }

        if (password.length < 6) {
            registerError.textContent = 'Password must be at least 6 characters long.';
            return;
        }

        if (!agreeTerms) {
            registerError.textContent = 'You must agree to the Terms of Service and Privacy Policy.';
            return;
        }

        try {
            console.log('===== SIGN UP FORM SUBMITTED =====');
            console.log('Name:', name);
            console.log('Email:', email);
            
            setButtonLoading(submitButton, true);
            
            console.log('Calling signUp function...');
            const signUpResult = await signUp(email, password, {
                full_name: name
            });
            
            console.log('SUCCESS: signUp completed!');
            console.log('Sign up result:', JSON.stringify(signUpResult, null, 2));
            
            const user = signUpResult.user;
            let session = signUpResult.session;
            
            console.log('User from result:', user);
            console.log('Session from result:', session);
            
            // If no session in the response, try to get the current session
            if (!session && user) {
                console.log('WARNING: No session in sign up response, fetching current session...');
                session = await getCurrentSession();
                console.log('Fetched session:', session);
            }
            
            console.log('Has user:', !!user);
            console.log('Has session:', !!session);
            console.log('Has access_token:', !!session?.access_token);
            
            // Create user in DynamoDB via user service API (with JWT)
            if (session?.access_token) {
                console.log('===== ATTEMPTING TO CREATE USER IN DATABASE =====');
                const created = await createUserInDatabase(user, session.access_token, name);
                console.log('===== CREATE USER RESULT:', created, '=====');
            } else {
                console.warn('WARNING: No session token available - user will be created on first login');
                console.log('Session object:', session);
            }
            
            // Check if email confirmation is required
            if (!session) {
                registerSuccess.textContent = 'Account created! Please check your email to verify your account.';
                // Don't clear the form yet, let user see the success message
                setTimeout(() => {
                    signUpForm.classList.remove('active');
                    signInForm.classList.add('active');
                    registerForm.reset();
                    clearMessages();
                }, 3000);
            } else {
                // Immediate sign-in (if email confirmation is disabled)
                registerSuccess.textContent = 'Account created successfully! Redirecting...';
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 1500);
            }
        } catch (error) {
            console.error('Sign up error:', error);
            
            let errorMessage = 'Failed to create account. Please try again.';
            
            // Handle specific error cases
            if (error.message.includes('already registered')) {
                errorMessage = 'This email is already registered. Please sign in instead.';
            } else if (error.message.includes('invalid email')) {
                errorMessage = 'Please enter a valid email address.';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            registerError.textContent = errorMessage;
            setButtonLoading(submitButton, false);
        }
    });

    // Handle Google sign in
    googleSignInBtn.addEventListener('click', async () => {
        try {
            setButtonLoading(googleSignInBtn, true);
            
            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/index.html`
                }
            });
            
            if (error) throw error;
            
            // Browser will redirect to Google OAuth
        } catch (error) {
            console.error('Google sign in error:', error);
            loginError.textContent = 'Failed to sign in with Google.';
            setButtonLoading(googleSignInBtn, false);
        }
    });

    // Handle GitHub sign in
    githubSignInBtn.addEventListener('click', async () => {
        try {
            setButtonLoading(githubSignInBtn, true);
            
            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'github',
                options: {
                    redirectTo: `${window.location.origin}/index.html`
                }
            });
            
            if (error) throw error;
            
            // Browser will redirect to GitHub OAuth
        } catch (error) {
            console.error('GitHub sign in error:', error);
            loginError.textContent = 'Failed to sign in with GitHub.';
            setButtonLoading(githubSignInBtn, false);
        }
    });

    // Handle forgot password
    const forgotPasswordLink = document.querySelector('.forgot-password');
    forgotPasswordLink.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value.trim();
        
        if (!email) {
            alert('Please enter your email address first.');
            document.getElementById('loginEmail').focus();
            return;
        }

        try {
            const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/reset-password.html`
            });
            
            if (error) throw error;
            
            alert('Password reset email sent! Please check your inbox.');
        } catch (error) {
            console.error('Password reset error:', error);
            alert('Failed to send password reset email. Please try again.');
        }
    });
});
