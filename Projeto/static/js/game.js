let localBananas = 0;
let bps = 0; 
let clickPower = 1;
let lastSaveTime = Date.now();
let bpsInterval;
let syncInterval;


function initGame(initialBananas, initialBps, initialClickPower) {
    localBananas = parseInt(initialBananas);
    bps = parseInt(initialBps);
    clickPower = parseInt(initialClickPower);
    updateDisplay();
    
   
    if (bpsInterval) clearInterval(bpsInterval);
    
   
    bpsInterval = setInterval(() => {
        if (bps > 0) {
            localBananas += bps / 10;
            updateDisplay();
        }
    }, 100);

    
    if (syncInterval) clearInterval(syncInterval);
    syncInterval = setInterval(syncScore, 5000);
}

function clickBanana(event) {
    localBananas += clickPower;
    updateDisplay();
    
    
    showClickFeedback(event, clickPower);
    
    
}

function updateDisplay() {
    const displayElement = document.getElementById('bananas-count');
    if (displayElement) {
        displayElement.innerText = Math.floor(localBananas);
    }
    

    const syncInput = document.getElementById('sync-bananas-input');
    if (syncInput) {
        syncInput.value = Math.floor(localBananas);
    }
}

function syncScore() {
    
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


