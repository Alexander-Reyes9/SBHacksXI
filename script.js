// Initialize Lucide icons
lucide.createIcons();

// Get DOM elements
const form = document.getElementById('playlist-form');
const input = document.getElementById('playlist-url');
const successMessage = document.getElementById('success-message');
const addAnotherBtn = document.getElementById('add-another');

// Handle form submission
form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (input.value.includes('spotify.com/playlist/')) {
        form.style.display = 'none';
        successMessage.classList.remove('hidden');
    }
});

// Handle "Add another playlist" button
addAnotherBtn.addEventListener('click', () => {
    input.value = '';
    successMessage.classList.add('hidden');
    form.style.display = 'block';
});
