// --- Global UI Elements & State ---
const ui = {
    introScreen: document.getElementById('intro-screen'),
    mainGameScreen: document.getElementById('main-game-screen'),
    gameOverScreen: document.getElementById('game-over-screen'),
    reportArea: document.getElementById('report-area'),
    actionArea: document.getElementById('action-area'),
    actionTitle: document.getElementById('action-title'),
    actionButtons: document.getElementById('action-buttons'),
    turnCounter: document.getElementById('turn-counter'),
    crewStatusCards: document.getElementById('crew-status-cards'),
    aiThinkingIndicator: document.getElementById('ai-thinking-indicator'),
    gameOverTitle: document.getElementById('game-over-title'),
    gameOverSubtitle: document.getElementById('game-over-subtitle'),
};

// --- API Communication ---
async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

// --- UI Rendering Functions ---
function setActiveScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function logMessage(logEntry) {
    const bubble = document.createElement('div');
    const iconMap = {
        player: '🧑‍🚀', sabotage: '🚨', detective: '🔎', vote: '🗳️', system: '⚙️', normal: '💬'
    };
    bubble.className = `message-bubble type-${logEntry.type}`;
    bubble.innerHTML = `<span class="icon">${iconMap[logEntry.type] || ''}</span> <span>${logEntry.message.replace(/\n/g, '<br>')}</span>`;
    ui.reportArea.appendChild(bubble);
    ui.reportArea.scrollTop = ui.reportArea.scrollHeight;
}

function renderGameState(state) {
    ui.turnCounter.textContent = state.turn;
    
    // Render Crew Cards
    ui.crewStatusCards.innerHTML = '';
    state.pets.forEach(pet => {
        const card = document.createElement('div');
        card.className = `crew-card ${pet.is_alive ? '' : 'ejected'}`;
        card.innerHTML = `
            <div class="avatar">${pet.avatar}</div>
            <div class="name">${pet.name}</div>
        `;
        ui.crewStatusCards.appendChild(card);
    });

    // Render Log
    ui.reportArea.innerHTML = '';
    state.log.forEach(logMessage);

    // Handle Game Over
    if (state.game_over) {
        endGame(state);
        return;
    }

    // Determine current phase and render action buttons
    const lastLogType = state.log[state.log.length - 1].type;
    if (lastLogType === 'detective') {
        renderVotingButtons(state.pets);
    } else {
        renderNightActionButtons(state.locations);
    }
}

function renderNightActionButtons(locations) {
    ui.actionArea.classList.remove('hidden');
    ui.actionTitle.textContent = `Turn ${document.getElementById('turn-counter').textContent}: Where will you perform your task?`;
    ui.actionButtons.innerHTML = '';
    locations.forEach(loc => {
        const button = document.createElement('button');
        button.textContent = loc;
        button.onclick = () => takeAction({ type: 'night_action', location: loc });
        ui.actionButtons.appendChild(button);
    });
}

function renderVotingButtons(pets) {
    ui.actionArea.classList.remove('hidden');
    ui.actionTitle.textContent = 'Who do you vote to eject?';
    ui.actionButtons.innerHTML = '';
    
    pets.filter(p => p.is_alive).forEach(pet => {
        const button = document.createElement('button');
        button.textContent = pet.name;
        button.className = 'vote-btn';
        button.onclick = () => takeAction({ type: 'vote', vote: pet.name });
        ui.actionButtons.appendChild(button);
    });
    
    const skipButton = document.createElement('button');
    skipButton.textContent = "Skip Vote";
    skipButton.className = 'skip-btn';
    skipButton.onclick = () => takeAction({ type: 'vote', vote: null });
    ui.actionButtons.appendChild(skipButton);
}

function endGame(state) {
    setActiveScreen('game-over-screen');
    ui.gameOverTitle.textContent = `The ${state.winner} Win!`;
    if (state.winner === 'Pawsmonauts') {
        const impostor = state.pets.find(p => p.is_impostor);
        ui.gameOverSubtitle.textContent = `You successfully identified ${impostor.name} as the Im-paw-ster!`;
        ui.gameOverTitle.style.color = '#22d3ee';
    } else {
        const impostor = state.pets.find(p => p.is_impostor);
        ui.gameOverSubtitle.textContent = `The Im-paw-ster, ${impostor.name}, has won the day!`;
        ui.gameOverTitle.style.color = '#ef4444';
    }
}

// --- Game Flow & Event Handlers ---
async function takeAction(actionData) {
    // Disable buttons and show thinking indicator
    ui.actionButtons.querySelectorAll('button').forEach(b => b.disabled = true);
    ui.aiThinkingIndicator.classList.remove('hidden');

    try {
        const newState = await postData('/api/action', actionData);
        renderGameState(newState);
    } catch (error) {
        console.error("Error taking action:", error);
        alert("A server error occurred. Please try restarting the game.");
    } finally {
        ui.aiThinkingIndicator.classList.add('hidden');
    }
}

async function startGame() {
    const playerName = document.getElementById('player-name').value.trim();
    if (!playerName) {
        alert("Please enter a name for your pet!");
        return;
    }
    
    setActiveScreen('main-game-screen');
    ui.aiThinkingIndicator.classList.remove('hidden');

    try {
        const initialState = await postData('/api/start', { player_name: playerName });
        renderGameState(initialState);
    } catch (error) {
        console.error("Error starting game:", error);
        alert("Could not start the game. Is the Python server running?");
        setActiveScreen('intro-screen');
    } finally {
        ui.aiThinkingIndicator.classList.add('hidden');
    }
}

// --- Initializer ---
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('start-game-btn').addEventListener('click', startGame);
    document.getElementById('play-again-btn').addEventListener('click', () => {
        setActiveScreen('intro-screen');
    });
});
