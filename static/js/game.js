// Kitchen Game JavaScript
let selectedIngredients = [];
let gameActive = false;
let updateInterval = null;

// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const deliverBtn = document.getElementById('deliverBtn');
const clearBtn = document.getElementById('clearBtn');
const waitingRecipes = document.getElementById('waitingRecipes');
const selectedIngredientsDiv = document.getElementById('selectedIngredients');
const ingredientButtons = document.querySelectorAll('.ingredient-btn');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    startBtn.addEventListener('click', startGame);
    stopBtn.addEventListener('click', stopGame);
    deliverBtn.addEventListener('click', deliverRecipe);
    clearBtn.addEventListener('click', clearSelection);
    
    ingredientButtons.forEach(btn => {
        btn.addEventListener('click', () => selectIngredient(btn));
    });
    
    // Load initial player statistics
    loadPlayerStatistics();
});

// Start game
async function startGame() {
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            gameActive = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
            // Start polling for game status
            updateInterval = setInterval(updateGameStatus, 500);
            
            console.log('Game started successfully');
        }
    } catch (error) {
        console.error('Error starting game:', error);
    }
}

// Stop game
async function stopGame() {
    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            gameActive = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            
            // Stop polling
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
            
            // Reload player statistics
            await loadPlayerStatistics();
            
            console.log('Game stopped successfully');
        }
    } catch (error) {
        console.error('Error stopping game:', error);
    }
}

// Update game status
async function updateGameStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update statistics
        updateStatistics(data.statistics);
        
        // Update waiting recipes
        updateWaitingRecipes(data.waiting_recipes);
        
    } catch (error) {
        console.error('Error updating game status:', error);
    }
}

// Update statistics display
function updateStatistics(stats) {
    if (!stats) return;
    
    document.getElementById('points').textContent = stats.current_points || 0;
    document.getElementById('streak').textContent = stats.current_streak || 0;
    document.getElementById('combo').textContent = `x${(stats.combo_multiplier || 1.0).toFixed(1)}`;
    document.getElementById('success').textContent = stats.successful_deliveries || 0;
    document.getElementById('failed').textContent = stats.failed_deliveries || 0;
}

// Update waiting recipes display
function updateWaitingRecipes(recipes) {
    if (!recipes || recipes.length === 0) {
        waitingRecipes.innerHTML = '<p class="no-recipes">待機中のレシピはありません</p>';
        return;
    }
    
    waitingRecipes.innerHTML = '';
    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <div class="recipe-name">${recipe.name}</div>
            <div class="recipe-ingredients">
                材料: ${recipe.ingredients.join(', ')}
            </div>
        `;
        waitingRecipes.appendChild(card);
    });
}

// Select ingredient
function selectIngredient(button) {
    const ingredient = button.dataset.ingredient;
    
    if (button.classList.contains('selected')) {
        // Deselect
        button.classList.remove('selected');
        selectedIngredients = selectedIngredients.filter(i => i !== ingredient);
    } else {
        // Select
        button.classList.add('selected');
        selectedIngredients.push(ingredient);
    }
    
    updateSelectedDisplay();
}

// Update selected ingredients display
function updateSelectedDisplay() {
    if (selectedIngredients.length === 0) {
        selectedIngredientsDiv.innerHTML = '<p style="color: #999;">材料が選択されていません</p>';
        deliverBtn.disabled = true;
    } else {
        selectedIngredientsDiv.innerHTML = '';
        selectedIngredients.forEach(ingredient => {
            const item = document.createElement('span');
            item.className = 'selected-item';
            item.textContent = getIngredientEmoji(ingredient) + ' ' + ingredient;
            selectedIngredientsDiv.appendChild(item);
        });
        deliverBtn.disabled = false;
    }
}

// Get emoji for ingredient
function getIngredientEmoji(ingredient) {
    const emojiMap = {
        'Tomato': '🍅',
        'Lettuce': '🥬',
        'Bread': '🍞',
        'Cheese': '🧀',
        'Meat': '🥩'
    };
    return emojiMap[ingredient] || '🍽️';
}

// Clear selection
function clearSelection() {
    selectedIngredients = [];
    ingredientButtons.forEach(btn => btn.classList.remove('selected'));
    updateSelectedDisplay();
}

// Deliver recipe
async function deliverRecipe() {
    if (selectedIngredients.length === 0) return;
    
    try {
        const response = await fetch('/api/deliver', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ingredients: selectedIngredients
            })
        });
        
        const data = await response.json();
        
        // Show feedback
        if (data.status === 'success') {
            showNotification('✅ 配達成功！', 'success');
        } else {
            showNotification('❌ 配達失敗...', 'error');
        }
        
        // Update statistics immediately
        updateStatistics(data.statistics);
        
        // Clear selection
        clearSelection();
        
    } catch (error) {
        console.error('Error delivering recipe:', error);
        showNotification('エラーが発生しました', 'error');
    }
}

// Load player statistics
async function loadPlayerStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        
        document.getElementById('totalGames').textContent = stats.total_games || 0;
        document.getElementById('totalSuccess').textContent = stats.total_successful_deliveries || 0;
        document.getElementById('totalFailed').textContent = stats.total_failed_deliveries || 0;
        document.getElementById('totalPoints').textContent = stats.total_points || 0;
        document.getElementById('bestStreak').textContent = stats.best_streak || 0;
        
    } catch (error) {
        console.error('Error loading player statistics:', error);
    }
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
