// Configuration Management
// This file helps manage environment-specific configuration

// Configuration object
const CONFIG = {
    // Supabase Configuration
    supabase: {
        url: 'https://ijyyifghxitisjbfnoxb.supabase.co',
        anonKey: '***REMOVED***'
    },
    
    // App Configuration
    app: {
        name: 'Rememberly',
        version: '1.0.0',
        environment: 'development' // 'development' | 'staging' | 'production'
    },
    
    // Feature Flags
    features: {
        oauthGoogle: true,
        oauthGithub: true,
        emailVerification: true,
        passwordReset: true
    }
};

// Load configuration from various sources
function loadConfig() {
    // Priority: 
    // 1. Environment variables (for server-side rendering)
    // 2. LocalStorage (for development)
    // 3. Inline configuration (hardcoded)
    
    // Try to load from localStorage (useful for local development)
    const storedAnonKey = localStorage.getItem('supabase_anon_key');
    if (storedAnonKey) {
        CONFIG.supabase.anonKey = storedAnonKey;
    }
    
    // Check for environment variables (if using a bundler like Vite/Webpack)
    if (typeof process !== 'undefined' && process.env) {
        CONFIG.supabase.url = process.env.VITE_SUPABASE_URL || CONFIG.supabase.url;
        CONFIG.supabase.anonKey = process.env.VITE_SUPABASE_ANON_KEY || CONFIG.supabase.anonKey;
        CONFIG.app.environment = process.env.NODE_ENV || CONFIG.app.environment;
    }
    
    return CONFIG;
}

// Save anon key to localStorage (for development only)
function saveAnonKeyToStorage(anonKey) {
    if (CONFIG.app.environment === 'development') {
        localStorage.setItem('supabase_anon_key', anonKey);
        console.log('Anon key saved to localStorage');
    } else {
        console.warn('Cannot save anon key in production mode');
    }
}

// Clear stored configuration
function clearStoredConfig() {
    localStorage.removeItem('supabase_anon_key');
    console.log('Stored configuration cleared');
}

// Validate configuration
function validateConfig() {
    const errors = [];
    
    if (!CONFIG.supabase.url) {
        errors.push('Supabase URL is missing');
    }
    
    if (!CONFIG.supabase.anonKey) {
        errors.push('Supabase anon key is missing');
    }
    
    if (CONFIG.supabase.anonKey === 'YOUR_SUPABASE_ANON_KEY') {
        errors.push('Please replace the placeholder anon key with your actual key');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Get configuration
function getConfig() {
    return CONFIG;
}

// Development helper: Set anon key interactively
function setAnonKey(key) {
    if (!key || key.trim() === '') {
        console.error('Invalid anon key');
        return false;
    }
    
    CONFIG.supabase.anonKey = key;
    saveAnonKeyToStorage(key);
    console.log('Anon key configured successfully!');
    console.log('Reload the page for changes to take effect.');
    return true;
}

// Show configuration helper in console
function showConfigHelper() {
    console.log('%cSupabase Configuration Helper', 'font-size: 16px; font-weight: bold; color: #667eea;');
    console.log('');
    console.log('To configure your Supabase anon key, run:');
    console.log('%csetAnonKey("your-actual-anon-key-here")', 'background: #f0f0f0; padding: 4px; border-radius: 4px;');
    console.log('');
    console.log('To view current configuration:');
    console.log('%cgetConfig()', 'background: #f0f0f0; padding: 4px; border-radius: 4px;');
    console.log('');
    console.log('To validate configuration:');
    console.log('%cvalidateConfig()', 'background: #f0f0f0; padding: 4px; border-radius: 4px;');
    console.log('');
    console.log('To clear stored configuration:');
    console.log('%cclearStoredConfig()', 'background: #f0f0f0; padding: 4px; border-radius: 4px;');
}

// Initialize configuration on load
loadConfig();

// Show helper in development mode
if (CONFIG.app.environment === 'development') {
    // Check if anon key needs to be configured
    const validation = validateConfig();
    if (!validation.valid) {
        console.warn('Configuration issues detected:');
        validation.errors.forEach(error => console.warn('  -', error));
        console.log('');
        showConfigHelper();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        loadConfig,
        validateConfig,
        getConfig,
        setAnonKey,
        saveAnonKeyToStorage,
        clearStoredConfig,
        showConfigHelper
    };
}

// Make available globally for console access
if (typeof window !== 'undefined') {
    window.setAnonKey = setAnonKey;
    window.getConfig = getConfig;
    window.validateConfig = validateConfig;
    window.clearStoredConfig = clearStoredConfig;
    window.showConfigHelper = showConfigHelper;
}
