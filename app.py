"""
Flask web application for Kitchen Game
Provides a responsive web UI for the game
"""
from flask import Flask, render_template, jsonify, request
from deliverManager import (
    DeliveryManager, KitchenGameManager, RecipeListSO, RecipeSO,
    KitchenObjectSO, PlateKitchenObject
)
from database import Database
import threading
import time

app = Flask(__name__)

# Game state
game_manager = None
delivery_manager = None
game_thread = None
game_running = False

def init_game():
    """Initialize game with sample data"""
    global game_manager, delivery_manager
    
    # Initialize database
    db = Database("kitchen_game.db")
    db.add_kitchen_object("Tomato", 1)
    db.add_kitchen_object("Lettuce", 2)
    db.add_kitchen_object("Bread", 3)
    db.add_kitchen_object("Cheese", 4)
    db.add_kitchen_object("Meat", 5)
    db.add_recipe("Sandwich", ["Bread", "Lettuce", "Tomato"])
    db.add_recipe("Salad", ["Lettuce", "Tomato"])
    db.add_recipe("Cheese Sandwich", ["Bread", "Cheese"])
    db.add_recipe("Burger", ["Bread", "Meat", "Lettuce"])
    
    # Create recipe objects for game
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    cheese = KitchenObjectSO("Cheese", 4)
    meat = KitchenObjectSO("Meat", 5)
    
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    cheese_sandwich_recipe = RecipeSO("Cheese Sandwich", [bread, cheese])
    burger_recipe = RecipeSO("Burger", [bread, meat, lettuce])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe, cheese_sandwich_recipe, burger_recipe])
    
    # Initialize managers
    game_manager = KitchenGameManager.get_instance()
    delivery_manager = DeliveryManager.get_instance(recipe_list, use_database=True)

def game_loop():
    """Background game loop for recipe spawning"""
    global game_running
    while game_running:
        if delivery_manager:
            delivery_manager.update()
        time.sleep(0.1)

@app.route('/')
def index():
    """Render main game page"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game session"""
    global game_running, game_thread, game_manager, delivery_manager
    
    if not game_manager or not delivery_manager:
        init_game()
    
    game_manager.start_game()
    delivery_manager.start_session()
    
    if not game_running:
        game_running = True
        game_thread = threading.Thread(target=game_loop, daemon=True)
        game_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Game started'})

@app.route('/api/stop', methods=['POST'])
def stop_game():
    """Stop the current game session"""
    global game_running, game_manager, delivery_manager
    
    if game_manager:
        game_manager.stop_game()
    
    if delivery_manager:
        delivery_manager.end_session()
    
    game_running = False
    
    return jsonify({'status': 'success', 'message': 'Game stopped'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current game status"""
    if not delivery_manager or not game_manager:
        return jsonify({
            'game_active': False,
            'waiting_recipes': [],
            'statistics': {}
        })
    
    waiting_recipes = []
    for recipe in delivery_manager.get_waiting_recipe_so_list():
        waiting_recipes.append({
            'name': recipe.name,
            'ingredients': [obj.name for obj in recipe.kitchen_object_so_list]
        })
    
    return jsonify({
        'game_active': game_manager.is_game_playing(),
        'waiting_recipes': waiting_recipes,
        'statistics': delivery_manager.get_statistics()
    })

@app.route('/api/deliver', methods=['POST'])
def deliver():
    """Deliver a recipe"""
    data = request.json
    if not data or not isinstance(data.get('ingredients'), list):
        return jsonify({'status': 'error', 'message': 'Invalid request data'}), 400
    ingredients = data.get('ingredients', [])
    
    if not delivery_manager:
        return jsonify({'status': 'error', 'message': 'Game not initialized'}), 400
    
    # Create a plate with the ingredients
    plate = PlateKitchenObject()
    
    # Map ingredient names to objects
    ingredient_map = {
        'Tomato': KitchenObjectSO("Tomato", 1),
        'Lettuce': KitchenObjectSO("Lettuce", 2),
        'Bread': KitchenObjectSO("Bread", 3),
        'Cheese': KitchenObjectSO("Cheese", 4),
        'Meat': KitchenObjectSO("Meat", 5)
    }
    
    for ingredient_name in ingredients:
        if ingredient_name in ingredient_map:
            plate.add_kitchen_object(ingredient_map[ingredient_name])
    
    # Track successful recipes before delivery
    prev_successful = delivery_manager.get_successful_recipes_amount()
    
    # Deliver the recipe
    delivery_manager.deliver_recipe(plate)
    
    # Check if delivery was successful
    success = delivery_manager.get_successful_recipes_amount() > prev_successful
    
    return jsonify({
        'status': 'success' if success else 'failed',
        'statistics': delivery_manager.get_statistics()
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get player statistics from database"""
    db = Database()
    stats = db.get_player_statistics()
    
    if not stats:
        stats = {
            'total_games': 0,
            'total_successful_deliveries': 0,
            'total_failed_deliveries': 0,
            'total_points': 0,
            'best_streak': 0
        }
    
    return jsonify(stats)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get recent game sessions"""
    db = Database()
    sessions = db.get_recent_sessions(10)
    return jsonify(sessions)

if __name__ == '__main__':
    import os
    init_game()
    # Debug mode should be disabled in production
    # Use environment variable to control debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
