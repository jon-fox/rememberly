// Simple memory storage demo with authentication
let memories = [];
let currentUser = null;

const memoryInput = document.getElementById('memoryInput');
const saveButton = document.getElementById('saveButton');
const memoryList = document.getElementById('memoryList');
const userMenu = document.getElementById('userMenu');
const userEmail = document.getElementById('userEmail');
const signOutBtn = document.getElementById('signOutBtn');

// Initialize authentication state
async function initAuth() {
    // Check if user is authenticated
    const authenticated = await requireAuth();
    
    if (!authenticated) {
        return; // Will redirect to login
    }
    
    // Get current user
    currentUser = await getCurrentUser();
    
    if (currentUser) {
        // Show user menu
        userMenu.style.display = 'flex';
        userEmail.textContent = currentUser.email;
        
        // Load user-specific memories
        loadMemories();
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

// Listen for auth state changes
onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event);
    
    if (event === 'SIGNED_OUT') {
        window.location.href = 'login.html';
    } else if (event === 'SIGNED_IN') {
        currentUser = session?.user;
        if (currentUser) {
            userMenu.style.display = 'flex';
            userEmail.textContent = currentUser.email;
            loadMemories();
        }
    }
});

// Event listeners
saveButton.addEventListener('click', addMemory);

memoryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addMemory();
    }
});

signOutBtn.addEventListener('click', handleSignOut);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
});
