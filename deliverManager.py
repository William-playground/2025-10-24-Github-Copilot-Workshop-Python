import time
import random
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from database import Database


class EventArgs:
    """イベント引数の基底クラス"""
    pass


class Event:
    """C#のeventに相当するクラス"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """イベントハンドラーを追加"""
        if handler not in self._handlers:
            self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """イベントハンドラーを削除"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def invoke(self, sender, args: EventArgs = None):
        """イベントを発火"""
        for handler in self._handlers:
            handler(sender, args or EventArgs())


@dataclass
class KitchenObjectSO:
    """キッチンオブジェクトのデータクラス"""
    name: str
    object_id: int


@dataclass
class RecipeSO:
    """レシピのデータクラス"""
    name: str
    kitchen_object_so_list: List[KitchenObjectSO] = field(default_factory=list)


@dataclass
class RecipeListSO:
    """レシピリストのデータクラス"""
    recipe_so_list: List[RecipeSO] = field(default_factory=list)


class PlateKitchenObject:
    """皿のキッチンオブジェクト"""
    
    def __init__(self):
        self._kitchen_object_so_list: List[KitchenObjectSO] = []
    
    def add_kitchen_object(self, kitchen_object: KitchenObjectSO):
        """キッチンオブジェクトを追加"""
        self._kitchen_object_so_list.append(kitchen_object)
    
    def get_kitchen_object_so_list(self) -> List[KitchenObjectSO]:
        """キッチンオブジェクトリストを取得"""
        return self._kitchen_object_so_list.copy()


class KitchenGameManager:
    """キッチンゲームマネージャー（Singleton）"""
    
    _instance: Optional['KitchenGameManager'] = None
    
    def __init__(self):
        self._is_game_playing = False
    
    @classmethod
    def get_instance(cls) -> 'KitchenGameManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_game_playing(self) -> bool:
        """ゲームが進行中かどうか"""
        return self._is_game_playing
    
    def start_game(self):
        """ゲーム開始"""
        self._is_game_playing = True
    
    def stop_game(self):
        """ゲーム停止"""
        self._is_game_playing = False


class DeliveryManager:
    """配達管理クラス（Python版）"""
    
    def get_recipe_by_name(self, user_input):
        """
        SQL injection safe method to get recipe by name
        Uses parameterized queries through database layer
        """
        db = Database()
        recipe = db.get_recipe_by_name(user_input)
        if recipe:
            print(f"レシピが見つかりました: {recipe['name']}")
        else:
            print(f"レシピが見つかりませんでした: {user_input}")
        return recipe
    
    _instance: Optional['DeliveryManager'] = None
    
    def __init__(self, recipe_list_so: RecipeListSO, use_database: bool = True):
        # イベント定義
        self.on_recipe_spawned = Event()
        self.on_recipe_completed = Event()
        self.on_recipe_success = Event()
        self.on_recipe_failed = Event()
        
        # プライベート変数
        self._recipe_list_so = recipe_list_so
        self._waiting_recipe_so_list: List[RecipeSO] = []
        self._spawn_recipe_timer = 0.0
        self._spawn_recipe_timer_max = 4.0
        self._waiting_recipes_max = 4
        self._successful_recipes_amount = 0
        self._failed_recipes_amount = 0
        self._last_update_time = time.time()
        
        # Database support
        self._use_database = use_database
        self._db = Database() if use_database else None
        self._session_id = None
        
        # Enhanced point system
        self._current_points = 0
        self._combo_multiplier = 1.0
        self._current_streak = 0
        self._best_streak = 0
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None, use_database: bool = True) -> 'DeliveryManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            if recipe_list_so is None:
                raise ValueError("初回作成時にはrecipe_list_soが必要です")
            cls._instance = cls(recipe_list_so, use_database)
        return cls._instance
    
    def start_session(self):
        """Start a new game session"""
        if self._use_database:
            self._session_id = self._db.create_game_session()
            print(f"新しいゲームセッション開始: {self._session_id}")
        self._current_points = 0
        self._current_streak = 0
        self._successful_recipes_amount = 0
        self._failed_recipes_amount = 0
    
    def end_session(self):
        """End the current game session"""
        if self._use_database and self._session_id:
            self._db.end_game_session(
                self._session_id,
                self._successful_recipes_amount,
                self._failed_recipes_amount,
                self._current_points
            )
            self._db.update_player_statistics(
                self._successful_recipes_amount,
                self._failed_recipes_amount,
                self._current_points,
                self._best_streak
            )
            print(f"ゲームセッション終了: {self._session_id}")
            self._session_id = None
    
    def _calculate_points(self, recipe: RecipeSO) -> int:
        """Calculate points for a successful delivery with combo multiplier"""
        base_points = len(recipe.kitchen_object_so_list) * 50
        return int(base_points * self._combo_multiplier)
    
    def update(self):
        """フレーム更新処理（UnityのUpdate相当）"""
        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time
        
        self._spawn_recipe_timer -= delta_time
        
        if self._spawn_recipe_timer <= 0.0:
            self._spawn_recipe_timer = self._spawn_recipe_timer_max
            
            kitchen_game_manager = KitchenGameManager.get_instance()
            if (kitchen_game_manager.is_game_playing() and 
                len(self._waiting_recipe_so_list) < self._waiting_recipes_max):
                
                # ランダムにレシピを選択
                waiting_recipe_so = random.choice(self._recipe_list_so.recipe_so_list)
                self._waiting_recipe_so_list.append(waiting_recipe_so)
                
                # イベント発火
                self.on_recipe_spawned.invoke(self)
    
    def deliver_recipe(self, plate_kitchen_object: PlateKitchenObject):
        """レシピの材料と皿の材料が一致しているかどうかを確認する"""
        
        for i, waiting_recipe_so in enumerate(self._waiting_recipe_so_list):
            plate_ingredients = plate_kitchen_object.get_kitchen_object_so_list()
            
            # 材料数が一致するかチェック
            if len(waiting_recipe_so.kitchen_object_so_list) == len(plate_ingredients):
                plate_contents_matches_recipe = True
                
                # レシピの各材料をチェック
                for recipe_kitchen_object_so in waiting_recipe_so.kitchen_object_so_list:
                    ingredient_found = False
                    
                    # 皿の材料と照合
                    for plate_kitchen_object_so in plate_ingredients:
                        if plate_kitchen_object_so == recipe_kitchen_object_so:
                            ingredient_found = True
                            break
                    
                    if not ingredient_found:
                        plate_contents_matches_recipe = False
                        break
                
                # 材料が完全に一致した場合
                if plate_contents_matches_recipe:
                    self._successful_recipes_amount += 1
                    self._current_streak += 1
                    self._best_streak = max(self._best_streak, self._current_streak)
                    
                    # Calculate points with combo multiplier
                    points_earned = self._calculate_points(waiting_recipe_so)
                    self._current_points += points_earned
                    
                    # Increase combo multiplier on streak
                    if self._current_streak >= 3:
                        self._combo_multiplier = 1.5
                    if self._current_streak >= 5:
                        self._combo_multiplier = 2.0
                    
                    # Remove delivered recipe
                    self._waiting_recipe_so_list.pop(i)
                    
                    # Record to database if enabled
                    if self._use_database and self._session_id:
                        # Find recipe id in database
                        recipe_data = self._db.get_recipe_by_name(waiting_recipe_so.name)
                        if recipe_data:
                            self._db.add_delivery(self._session_id, recipe_data['id'], True, points_earned)
                    
                    print(f"配達成功! ポイント: +{points_earned} (コンボ: x{self._combo_multiplier}, ストリーク: {self._current_streak})")
                    
                    # 成功イベント発火
                    self.on_recipe_completed.invoke(self)
                    self.on_recipe_success.invoke(self)
                    return
        
        # 一致するレシピが見つからなかった場合
        self._failed_recipes_amount += 1
        self._current_streak = 0
        self._combo_multiplier = 1.0
        
        # Record failed delivery to database if enabled
        if self._use_database and self._session_id:
            self._db.add_delivery(self._session_id, 0, False, 0)
        
        print(f"配達失敗... ストリークリセット")
        self.on_recipe_failed.invoke(self)
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """待機中のレシピリストを取得"""
        return self._waiting_recipe_so_list.copy()
    
    def get_successful_recipes_amount(self) -> int:
        """成功したレシピ数を取得"""
        return self._successful_recipes_amount
    
    def get_current_points(self) -> int:
        """現在のポイントを取得"""
        return self._current_points
    
    def get_current_streak(self) -> int:
        """現在のストリークを取得"""
        return self._current_streak
    
    def get_combo_multiplier(self) -> float:
        """現在のコンボ倍率を取得"""
        return self._combo_multiplier
    
    def get_statistics(self) -> dict:
        """Get game statistics"""
        return {
            'successful_deliveries': self._successful_recipes_amount,
            'failed_deliveries': self._failed_recipes_amount,
            'current_points': self._current_points,
            'current_streak': self._current_streak,
            'best_streak': self._best_streak,
            'combo_multiplier': self._combo_multiplier
        }


# 使用例
if __name__ == "__main__":
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # サンプルレシピ
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # ゲームマネージャーとデリバリーマネージャーを初期化
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    # Initialize database with sample data
    db = Database("kitchen_game.db")
    db.add_kitchen_object("Tomato", 1)
    db.add_kitchen_object("Lettuce", 2)
    db.add_kitchen_object("Bread", 3)
    db.add_recipe("Sandwich", ["Bread", "Lettuce", "Tomato"])
    db.add_recipe("Salad", ["Lettuce", "Tomato"])
    
    delivery_manager = DeliveryManager.get_instance(recipe_list, use_database=True)
    delivery_manager.start_session()
    
    # イベントハンドラーの設定
    def on_recipe_spawned(sender, args):
        print("新しいレシピが生成されました！")
    
    def on_recipe_success(sender, args):
        stats = delivery_manager.get_statistics()
        print(f"レシピ配達成功！ ポイント: {stats['current_points']}, ストリーク: {stats['current_streak']}")
    
    def on_recipe_failed(sender, args):
        print("レシピ配達失敗...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # サンプル実行
    print("ゲーム開始...")
    
    # 5秒間更新処理を実行
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # 100ms間隔で更新
    
    print(f"\n待機中のレシピ数: {len(delivery_manager.get_waiting_recipe_so_list())}")
    
    # サンプル配達テスト - 複数回配達してコンボをテスト
    for i in range(3):
        plate = PlateKitchenObject()
        plate.add_kitchen_object(bread)
        plate.add_kitchen_object(lettuce)
        plate.add_kitchen_object(tomato)
        
        print(f"\nサンドイッチを配達 #{i+1}...")
        delivery_manager.deliver_recipe(plate)
    
    stats = delivery_manager.get_statistics()
    print(f"\n=== 最終統計 ===")
    print(f"成功したレシピ数: {stats['successful_deliveries']}")
    print(f"失敗したレシピ数: {stats['failed_deliveries']}")
    print(f"総ポイント: {stats['current_points']}")
    print(f"最高ストリーク: {stats['best_streak']}")
    
    # Test SQL injection protection
    print("\n=== SQL Injection Protection Test ===")
    delivery_manager.get_recipe_by_name("Sandwich' OR '1'='1")
    
    # End session
    delivery_manager.end_session()
    
    # Display player statistics
    player_stats = db.get_player_statistics()
    if player_stats:
        print(f"\n=== プレイヤー統計 ===")
        print(f"総ゲーム数: {player_stats['total_games']}")
        print(f"総成功配達数: {player_stats['total_successful_deliveries']}")
        print(f"総ポイント: {player_stats['total_points']}")