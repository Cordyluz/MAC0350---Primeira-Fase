let localBananas = 0;
let bps = 0; // Bananas per second (calculated roughly on frontend for smoothness, synced exactly with backend)
let clickPower = 1;
let lastSaveTime = Date.now();
let bpsInterval;
let syncInterval;

// Start game called when HTMX loads the game partial
function initGame(initialBananas, initialBps, initialClickPower) {
    localBananas = parseInt(initialBananas);
    bps = parseInt(initialBps);
    clickPower = parseInt(initialClickPower);
    updateDisplay();
    
    // Clear previous if any
    if (bpsInterval) clearInterval(bpsInterval);
    
    // Add BPS smoothly every 100ms
    bpsInterval = setInterval(() => {
        if (bps > 0) {
            localBananas += bps / 10;
            updateDisplay();
        }
    }, 100);

    // Sync to server every 5 seconds using HTMX behind the scenes
    if (syncInterval) clearInterval(syncInterval);
    syncInterval = setInterval(syncScore, 5000);
}

function clickBanana(event) {
    localBananas += clickPower;
    updateDisplay();
    
    // Visual feedback
    showClickFeedback(event, clickPower);
    
    // Play sound optionally
    // const audio = new Audio('/static/click.mp3');
    // audio.play();
}

function updateDisplay() {
    const displayElement = document.getElementById('bananas-count');
    if (displayElement) {
        displayElement.innerText = Math.floor(localBananas);
    }
    
    // Update the hidden input that HTMX will use to sync score
    const syncInput = document.getElementById('sync-bananas-input');
    if (syncInput) {
        syncInput.value = Math.floor(localBananas);
    }
}

function syncScore() {
    // We check if HTMX is loaded and we have a form to trigger
    const syncForm = document.getElementById('sync-form');
    if (syncForm) {
        htmx.trigger(syncForm, 'submit');
    }
}

function showClickFeedback(e, amount) {
    const feedback = document.createElement('div');
    feedback.innerText = '+' + amount;
    feedback.className = 'click-feedback';
    feedback.style.left = e.clientX + 'px';
    feedback.style.top = e.clientY + 'px';
    
    document.body.appendChild(feedback);
    setTimeout(() => {
        document.body.removeChild(feedback);
    }, 800);
}

// When user buys an item via HTMX, the server re-renders the DOM, 
// so we need to be careful. HTMX swap will trigger htmx:afterSwap event if needed, but since we re-render game.html, it will re-invoke initGame via a script tag.
