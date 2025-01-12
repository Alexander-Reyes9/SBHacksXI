// Initialize Lucide icons
lucide.createIcons();

const playlistForm = document.getElementById('playlist-form');
const container = document.querySelector('.container');
const loadingOverlay = document.querySelector('.loading-overlay');
const successMessage = document.getElementById('success-message');

playlistForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const playlistUrl = document.getElementById('playlist-url').value;
    
    if (!playlistUrl.includes('spotify.com/playlist/')) {
        alert('Please enter a valid Spotify playlist URL');
        return;
    }

    // Add submitting class to container for color wave effect
    container.classList.add('submitting');
    
    // Show loading overlay with animations
    loadingOverlay.classList.add('active');
    
    try {
        // Simulate processing time (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Show success message
        successMessage.classList.remove('hidden');
        playlistForm.classList.add('hidden');
        
        // Optional: Add confetti effect on success
        createConfetti();
    } catch (error) {
        console.error('Error:', error);
    } finally {
        loadingOverlay.classList.remove('active');
        // Remove color wave effect after delay
        setTimeout(() => {
            container.classList.remove('submitting');
        }, 2000);
    }
});

// Optional: Add confetti effect
function createConfetti() {
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
        document.body.appendChild(confetti);
        
        // Remove confetti after animation
        setTimeout(() => confetti.remove(), 3000);
    }
}

// Reset form
document.getElementById('add-another').addEventListener('click', () => {
    successMessage.classList.add('hidden');
    playlistForm.classList.remove('hidden');
    document.getElementById('playlist-url').value = '';
});
