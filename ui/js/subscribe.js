// Subscribe page logic
async function initSubscribePage() {
    // Check if user is authenticated
    const authenticated = await isAuthenticated();
    
    if (!authenticated) {
        // Redirect to login with return URL
        window.location.href = 'login.html?redirect=subscribe.html';
        return;
    }
    
    // User is authenticated, show the subscription page
    console.log('User authenticated, showing subscription options');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    initSubscribePage();
});
