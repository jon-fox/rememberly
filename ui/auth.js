// Supabase Authentication Module
// Initialize Supabase client with your project credentials

// Create Supabase client
let supabaseClient = null;

// Get configuration
function getSupabaseConfig() {
    // Try to get from config.js if available
    if (typeof CONFIG !== 'undefined' && CONFIG.supabase) {
        return CONFIG.supabase;
    }
    
    // Fallback to direct configuration - should not be reached if config.js is loaded
    console.warn('CONFIG not found, using fallback configuration');
    const config = {
        url: 'https://ijyyifghxitisjbfnoxb.supabase.co',
        anonKey: localStorage.getItem('supabase_anon_key') || ''
    };
    
    return config;
}

// Initialize Supabase client
function initSupabase() {
    if (typeof supabase === 'undefined') {
        console.error('Supabase library not loaded. Please include the Supabase CDN script.');
        return null;
    }
    
    const config = getSupabaseConfig();
    
    // Validate configuration
    if (!config.anonKey) {
        console.error('Supabase anon key not configured!');
        console.log('To configure, run in console: setAnonKey("your-actual-key")');
        return null;
    }
    
    supabaseClient = supabase.createClient(config.url, config.anonKey);
    console.log('Supabase client initialized');
    return supabaseClient;
}

// Get current user session
async function getCurrentSession() {
    if (!supabaseClient) {
        console.error('Supabase client not initialized');
        return null;
    }
    
    const { data: { session }, error } = await supabaseClient.auth.getSession();
    
    if (error) {
        console.error('Error getting session:', error.message);
        return null;
    }
    
    return session;
}

// Get current user
async function getCurrentUser() {
    const session = await getCurrentSession();
    return session?.user || null;
}

// Sign up with email and password
async function signUp(email, password, userData = {}) {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized');
    }
    
    const { data, error } = await supabaseClient.auth.signUp({
        email: email,
        password: password,
        options: {
            data: userData
        }
    });
    
    if (error) {
        throw error;
    }
    
    return data;
}

// Sign in with email and password
async function signIn(email, password) {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized');
    }
    
    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email: email,
        password: password
    });
    
    if (error) {
        throw error;
    }
    
    return data;
}

// Sign out
async function signOut() {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized');
    }
    
    const { error } = await supabaseClient.auth.signOut();
    
    if (error) {
        throw error;
    }
}

// Listen to auth state changes
function onAuthStateChange(callback) {
    if (!supabaseClient) {
        console.error('Supabase client not initialized');
        return null;
    }
    
    const { data: { subscription } } = supabaseClient.auth.onAuthStateChange((event, session) => {
        console.log('Auth event:', event);
        callback(event, session);
    });
    
    return subscription;
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSupabase();
});

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