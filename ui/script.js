// Simple memory storage demo
let memories = [];

const memoryInput = document.getElementById('memoryInput');
const saveButton = document.getElementById('saveButton');
const memoryList = document.getElementById('memoryList');

// Load memories from localStorage
function loadMemories() {
    const stored = localStorage.getItem('rememberly_memories');
    if (stored) {
        memories = JSON.parse(stored);
        renderMemories();
    }
}

// Save memories to localStorage
function saveMemories() {
    localStorage.setItem('rememberly_memories', JSON.stringify(memories));
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

// Event listeners
saveButton.addEventListener('click', addMemory);

memoryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addMemory();
    }
});

// Initialize
loadMemories();
