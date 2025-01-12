// Initialize Lucide icons
lucide.createIcons();

// DOM Elements
const playlistForm = document.getElementById('playlist-form');
const successMessage = document.getElementById('success-message');
const loadingOverlay = document.querySelector('.loading-overlay');
const visualizationImg = document.getElementById('visualization');

// Form submission handler
playlistForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    document.querySelector('.loading-overlay').classList.add('active');
    const form = e.target;
    const successMessage = document.getElementById('success-message');
    
    form.classList.add('hidden');
    
    try {
        // Simulate analysis time (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Show success message
        successMessage.classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        form.classList.remove('hidden');
        // Optional: Add error handling UI here
    } finally {
        loadingOverlay.classList.remove('active');
    }
});

// Add event listener for "Add another playlist" button
document.getElementById('add-another').addEventListener('click', () => {
    document.getElementById('success-message').classList.add('hidden');
    document.getElementById('playlist-form').classList.remove('hidden');
    document.getElementById('playlist-url').value = '';
});

// Utility Functions
async function loadVisualization() {
    try {
        const response = await fetch('/api/visualization');
        if (!response.ok) throw new Error('Failed to load visualization');
        const base64Data = await response.text();
        visualizationImg.src = `data:image/png;base64,${base64Data}`;
    } catch (error) {
        console.error('Error loading visualization:', error);
        throw error;
    }
}

function isValidSpotifyUrl(url) {
    return url.includes('spotify.com/playlist/');
}

async function processPlaylist(url) {
    // Simulate processing time - replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 3000));
}

// Load visualization on page load
window.addEventListener('load', loadVisualization);
