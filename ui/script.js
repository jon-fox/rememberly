// Simple memory storage demo with authentication
let memories = [];
let currentUser = null;

// DOM elements - will be initialized after DOM loads
let memoryInput, saveButton, memoryList, userMenu, userEmail, signOutBtn, signInBtn;

// Create user in DynamoDB via API - ensures user exists in database
async function ensureUserInDatabase(user, accessToken) {
    console.log('>>>>> ensureUserInDatabase CALLED <<<<<');
    console.log('User:', user);
    console.log('Has token:', !!accessToken);
    
    try {
        const apiEndpoint = 'https://mcp.rememberly.app/users';
        const payload = {
            user_id: user.id,
            email: user.email,
            username: user.user_metadata?.full_name || user.user_metadata?.name || user.email.split('@')[0]
        };
        
        console.log('API Endpoint:', apiEndpoint);
        console.log('Payload:', JSON.stringify(payload, null, 2));
        console.log('Sending fetch request to create user...');
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(payload)
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('SUCCESS: User created/updated in DynamoDB:', responseData);
            return true;
        } else {
            const errorText = await response.text();
            console.error('FAILED: Failed to create user. Status:', response.status, 'Response:', errorText);
            return false;
        }
    } catch (error) {
        console.error('EXCEPTION: Exception creating user:', error);
        return false;
    }
}

// Initialize authentication state
async function initAuth() {
    console.log('=== INDEX PAGE: initAuth called ===');
    
    // Ensure Supabase is initialized
    if (!supabaseClient) {
        initSupabase();
    }
    
    // Wait a moment for session to stabilize
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check if user is authenticated (optional, no redirect)
    const authenticated = await isAuthenticated();
    console.log('Is authenticated:', authenticated);
    
    if (authenticated) {
        // Get current user
        currentUser = await getCurrentUser();
        const session = await getCurrentSession();
        
        console.log('Current user:', currentUser);
        console.log('Has session:', !!session);
        console.log('Has token:', !!session?.access_token);
        
        if (currentUser) {
            // Show user menu, hide sign in button
            userMenu.style.display = 'flex';
            signInBtn.style.display = 'none';
            userEmail.textContent = currentUser.email;
            
            // Ensure user exists in database (for OAuth users especially)
            if (session?.access_token) {
                console.log('===== CALLING ensureUserInDatabase =====');
                await ensureUserInDatabase(currentUser, session.access_token);
            } else {
                console.warn('No access token available');
            }
            
            // Load user-specific memories
            loadMemories();
        }
    } else {
        // Show sign in button, hide user menu
        signInBtn.style.display = 'block';
        userMenu.style.display = 'none';
    }
}

// Load memories from localStorage (user-specific)
function loadMemories() {
    if (!currentUser) return;
    
    const storageKey = `rememberly_memories_${currentUser.id}`;
    const stored = localStorage.getItem(storageKey);
    if (stored) {
        memories = JSON.parse(stored);
        renderMemories();
    }
}

// Save memories to localStorage (user-specific)
function saveMemories() {
    if (!currentUser) return;
    
    const storageKey = `rememberly_memories_${currentUser.id}`;
    localStorage.setItem(storageKey, JSON.stringify(memories));
}

// Render memories to the page
function renderMemories() {
    memoryList.innerHTML = '';
    
    if (memories.length === 0) {
        memoryList.innerHTML = '<p style="text-align: center; color: #999;">No memories yet. Create your first one above!</p>';
        return;
    }

    memories.forEach((memory, index) => {
        const memoryItem = document.createElement('div');
        memoryItem.className = 'memory-item';
        
        memoryItem.innerHTML = `
            <div class="memory-text">${memory.text}</div>
            <div class="memory-time">${new Date(memory.timestamp).toLocaleString()}</div>
        `;
        
        memoryList.appendChild(memoryItem);
    });
}

// Add a new memory
function addMemory() {
    // Check if user is signed in
    if (!currentUser) {
        alert('Please sign in to save memories!');
        window.location.href = 'login.html';
        return;
    }
    
    const text = memoryInput.value.trim();
    
    if (text === '') {
        alert('Please enter a memory!');
        return;
    }

    const memory = {
        text: text,
        timestamp: new Date().toISOString()
    };

    memories.unshift(memory); // Add to beginning
    saveMemories();
    renderMemories();
    
    memoryInput.value = '';
    memoryInput.focus();
}

// Handle sign out
async function handleSignOut() {
    try {
        await signOut();
        // Redirect to login page
        window.location.href = 'login.html';
    } catch (error) {
        console.error('Sign out error:', error);
        alert('Failed to sign out. Please try again.');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize DOM elements
    memoryInput = document.getElementById('memoryInput');
    saveButton = document.getElementById('saveButton');
    memoryList = document.getElementById('memoryList');
    userMenu = document.getElementById('userMenu');
    userEmail = document.getElementById('userEmail');
    signOutBtn = document.getElementById('signOutBtn');
    signInBtn = document.getElementById('signInBtn');
    
    // Event listeners
    saveButton.addEventListener('click', addMemory);

    memoryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addMemory();
        }
    });

    signOutBtn.addEventListener('click', handleSignOut);

    signInBtn.addEventListener('click', () => {
        window.location.href = 'login.html';
    });

    const subscribeBtn = document.getElementById('subscribeBtn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', () => {
            window.location.href = 'subscribe.html';
        });
    }
    
    // Listen for auth state changes (after DOM elements are initialized)
    onAuthStateChange((event, session) => {
        console.log('Auth state changed:', event);
        
        // Only redirect on explicit sign out, not on initial load
        if (event === 'SIGNED_OUT' && currentUser !== null) {
            window.location.href = 'login.html';
        } else if (event === 'SIGNED_IN') {
            currentUser = session?.user;
            if (currentUser && userMenu && signInBtn && userEmail) {
                userMenu.style.display = 'flex';
                signInBtn.style.display = 'none';
                userEmail.textContent = currentUser.email;
                loadMemories();
            }
        }
    });
    
    // Initialize authentication
    initAuth();
});
