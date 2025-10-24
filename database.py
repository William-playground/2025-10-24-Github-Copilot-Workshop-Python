"""
Database module for kitchen game
Provides SQLite database support for persistent storage
"""
import sqlite3
import json
from typing import List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager


class Database:
    """Database access layer for kitchen game"""
    
    def __init__(self, db_path: str = "kitchen_game.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Kitchen objects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kitchen_objects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    object_id INTEGER NOT NULL
                )
            """)
            
            # Recipes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Recipe ingredients table (many-to-many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    recipe_id INTEGER,
                    kitchen_object_id INTEGER,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                    FOREIGN KEY (kitchen_object_id) REFERENCES kitchen_objects(id),
                    PRIMARY KEY (recipe_id, kitchen_object_id)
                )
            """)
            
            # Game sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    successful_deliveries INTEGER DEFAULT 0,
                    failed_deliveries INTEGER DEFAULT 0,
                    total_points INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Delivery history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delivery_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    recipe_id INTEGER,
                    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    points_earned INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                )
            """)
            
            # Player statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_games INTEGER DEFAULT 0,
                    total_successful_deliveries INTEGER DEFAULT 0,
                    total_failed_deliveries INTEGER DEFAULT 0,
                    total_points INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def add_kitchen_object(self, name: str, object_id: int):
        """Add or update a kitchen object"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO kitchen_objects (name, object_id)
                VALUES (?, ?)
            """, (name, object_id))
    
    def get_kitchen_object(self, name: str) -> Optional[Tuple[int, str, int]]:
        """Get kitchen object by name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, object_id FROM kitchen_objects WHERE name = ?
            """, (name,))
            return cursor.fetchone()
    
    def add_recipe(self, name: str, ingredient_names: List[str]) -> int:
        """Add a recipe with ingredients"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert recipe
            cursor.execute("""
                INSERT OR IGNORE INTO recipes (name) VALUES (?)
            """, (name,))
            
            # Get recipe id
            cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
            recipe_id = cursor.fetchone()[0]
            
            # Clear existing ingredients
            cursor.execute("""
                DELETE FROM recipe_ingredients WHERE recipe_id = ?
            """, (recipe_id,))
            
            # Add ingredients
            for ingredient_name in ingredient_names:
                cursor.execute("""
                    SELECT id FROM kitchen_objects WHERE name = ?
                """, (ingredient_name,))
                result = cursor.fetchone()
                if result:
                    kitchen_object_id = result[0]
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, kitchen_object_id)
                        VALUES (?, ?)
                    """, (recipe_id, kitchen_object_id))
            
            return recipe_id
    
    def get_recipe_by_name(self, name: str) -> Optional[dict]:
        """Get recipe by name (SQL injection safe)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.name, r.created_at
                FROM recipes r
                WHERE r.name = ?
            """, (name,))
            
            recipe_row = cursor.fetchone()
            if not recipe_row:
                return None
            
            # Get ingredients
            cursor.execute("""
                SELECT ko.name, ko.object_id
                FROM recipe_ingredients ri
                JOIN kitchen_objects ko ON ri.kitchen_object_id = ko.id
                WHERE ri.recipe_id = ?
            """, (recipe_row['id'],))
            
            ingredients = [dict(row) for row in cursor.fetchall()]
            
            return {
                'id': recipe_row['id'],
                'name': recipe_row['name'],
                'created_at': recipe_row['created_at'],
                'ingredients': ingredients
            }
    
    def get_all_recipes(self) -> List[dict]:
        """Get all recipes with their ingredients"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, created_at FROM recipes
            """)
            recipes = []
            for row in cursor.fetchall():
                recipe_id = row['id']
                
                # Get ingredients for this recipe
                cursor.execute("""
                    SELECT ko.name, ko.object_id
                    FROM recipe_ingredients ri
                    JOIN kitchen_objects ko ON ri.kitchen_object_id = ko.id
                    WHERE ri.recipe_id = ?
                """, (recipe_id,))
                
                ingredients = [dict(ing_row) for ing_row in cursor.fetchall()]
                
                recipes.append({
                    'id': row['id'],
                    'name': row['name'],
                    'created_at': row['created_at'],
                    'ingredients': ingredients
                })
            
            return recipes
    
    def create_game_session(self) -> int:
        """Create a new game session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO game_sessions (start_time, is_active)
                VALUES (?, 1)
            """, (datetime.now(),))
            return cursor.lastrowid
    
    def end_game_session(self, session_id: int, successful_deliveries: int, 
                         failed_deliveries: int, total_points: int):
        """End a game session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE game_sessions
                SET end_time = ?,
                    successful_deliveries = ?,
                    failed_deliveries = ?,
                    total_points = ?,
                    is_active = 0
                WHERE id = ?
            """, (datetime.now(), successful_deliveries, failed_deliveries, 
                  total_points, session_id))
    
    def get_active_session(self) -> Optional[dict]:
        """Get the active game session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM game_sessions WHERE is_active = 1
                ORDER BY start_time DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_delivery(self, session_id: int, recipe_id: int, success: bool, points: int):
        """Record a delivery attempt"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO delivery_history 
                (session_id, recipe_id, success, points_earned)
                VALUES (?, ?, ?, ?)
            """, (session_id, recipe_id, success, points))
    
    def get_session_history(self, session_id: int) -> List[dict]:
        """Get delivery history for a session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dh.*, r.name as recipe_name
                FROM delivery_history dh
                JOIN recipes r ON dh.recipe_id = r.id
                WHERE dh.session_id = ?
                ORDER BY dh.delivered_at DESC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_player_statistics(self, successful_deliveries: int, 
                                 failed_deliveries: int, points: int, streak: int):
        """Update player statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if statistics exist
            cursor.execute("SELECT id FROM player_statistics LIMIT 1")
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("""
                    UPDATE player_statistics
                    SET total_games = total_games + 1,
                        total_successful_deliveries = total_successful_deliveries + ?,
                        total_failed_deliveries = total_failed_deliveries + ?,
                        total_points = total_points + ?,
                        best_streak = MAX(best_streak, ?),
                        last_updated = ?
                """, (successful_deliveries, failed_deliveries, points, streak, datetime.now()))
            else:
                cursor.execute("""
                    INSERT INTO player_statistics 
                    (total_games, total_successful_deliveries, total_failed_deliveries, 
                     total_points, best_streak, last_updated)
                    VALUES (1, ?, ?, ?, ?, ?)
                """, (successful_deliveries, failed_deliveries, points, streak, datetime.now()))
    
    def get_player_statistics(self) -> Optional[dict]:
        """Get player statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_statistics LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_recent_sessions(self, limit: int = 10) -> List[dict]:
        """Get recent game sessions"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM game_sessions
                WHERE is_active = 0
                ORDER BY end_time DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]


# Testing and initialization
if __name__ == "__main__":
    # Create database and add sample data
    db = Database("kitchen_game.db")
    
    # Add kitchen objects
    db.add_kitchen_object("Tomato", 1)
    db.add_kitchen_object("Lettuce", 2)
    db.add_kitchen_object("Bread", 3)
    db.add_kitchen_object("Cheese", 4)
    
    # Add recipes
    db.add_recipe("Sandwich", ["Bread", "Lettuce", "Tomato"])
    db.add_recipe("Salad", ["Lettuce", "Tomato"])
    db.add_recipe("Cheese Sandwich", ["Bread", "Cheese"])
    
    # Test retrieval (SQL injection safe)
    print("Testing safe recipe retrieval:")
    recipe = db.get_recipe_by_name("Sandwich")
    print(f"Recipe: {recipe}")
    
    # Test SQL injection protection
    print("\nTesting SQL injection protection:")
    malicious_input = "Sandwich' OR '1'='1"
    malicious_result = db.get_recipe_by_name(malicious_input)
    print(f"Result with malicious input: {malicious_result}")
    
    # List all recipes
    print("\nAll recipes:")
    for recipe_item in db.get_all_recipes():
        print(f"- {recipe_item['name']}: {[i['name'] for i in recipe_item['ingredients']]}")
    
    # Test session management
    print("\nTesting session management:")
    session_id = db.create_game_session()
    print(f"Created session: {session_id}")
    
    # Add some deliveries (check recipe is not None first)
    if recipe:
        db.add_delivery(session_id, recipe['id'], True, 100)
        db.add_delivery(session_id, recipe['id'], False, 0)
    else:
        print("Warning: Recipe was None, skipping delivery tests")
    
    # End session
    db.end_game_session(session_id, 1, 1, 100)
    
    # Update statistics
    db.update_player_statistics(1, 1, 100, 5)
    
    stats = db.get_player_statistics()
    print(f"Player statistics: {stats}")
