import time
import random
import json
import os
from datetime import datetime
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


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


@dataclass
class SessionRecord:
    """セッション記録のデータクラス"""
    timestamp: str
    successful_recipes: int
    failed_recipes: int
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRecord':
        """辞書形式から生成"""
        return cls(**data)


@dataclass
class ProgressData:
    """進捗データのデータクラス"""
    total_sessions: int = 0
    total_successful_recipes: int = 0
    total_failed_recipes: int = 0
    session_history: List[SessionRecord] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'total_sessions': self.total_sessions,
            'total_successful_recipes': self.total_successful_recipes,
            'total_failed_recipes': self.total_failed_recipes,
            'session_history': [record.to_dict() for record in self.session_history]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressData':
        """辞書形式から生成"""
        session_history = [SessionRecord.from_dict(record) for record in data.get('session_history', [])]
        return cls(
            total_sessions=data.get('total_sessions', 0),
            total_successful_recipes=data.get('total_successful_recipes', 0),
            total_failed_recipes=data.get('total_failed_recipes', 0),
            session_history=session_history
        )


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
    def get_recipe_by_name(self, user_input):
        query = f"SELECT * FROM recipes WHERE name = '{user_input}'"
        print(f"実行クエリ: {query}")
        return query
    
    """配達管理クラス（Python版）"""
    
    _instance: Optional['DeliveryManager'] = None
    
    def __init__(self, recipe_list_so: RecipeListSO, progress_file: str = "progress_data.json"):
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
        self._last_update_time = time.time()
        
        # 進捗管理用変数
        self._progress_file = progress_file
        self._progress_data = ProgressData()
        self._session_start_time: Optional[float] = None
        self._session_failed_recipes = 0
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None, progress_file: str = "progress_data.json") -> 'DeliveryManager':
        """Singletonインスタンスを取得"""
        if cls._instance is None:
            if recipe_list_so is None:
                raise ValueError("初回作成時にはrecipe_list_soが必要です")
            cls._instance = cls(recipe_list_so, progress_file)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Singletonインスタンスをリセット（テスト用）"""
        cls._instance = None
    
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
                    self._waiting_recipe_so_list.pop(i)
                    
                    # 成功イベント発火
                    self.on_recipe_completed.invoke(self)
                    self.on_recipe_success.invoke(self)
                    return
        
        # 一致するレシピが見つからなかった場合
        self._session_failed_recipes += 1
        self.on_recipe_failed.invoke(self)
    
    def start_session(self):
        """セッションを開始"""
        self._session_start_time = time.time()
        self._successful_recipes_amount = 0
        self._session_failed_recipes = 0
    
    def complete_session(self) -> SessionRecord:
        """セッションを完了し、記録を保存"""
        if self._session_start_time is None:
            raise ValueError("セッションが開始されていません")
        
        # セッション記録を作成
        duration = time.time() - self._session_start_time
        session_record = SessionRecord(
            timestamp=datetime.now().isoformat(),
            successful_recipes=self._successful_recipes_amount,
            failed_recipes=self._session_failed_recipes,
            duration_seconds=duration
        )
        
        # 進捗データを更新
        self._progress_data.total_sessions += 1
        self._progress_data.total_successful_recipes += self._successful_recipes_amount
        self._progress_data.total_failed_recipes += self._session_failed_recipes
        self._progress_data.session_history.append(session_record)
        
        # セッション状態をリセット
        self._session_start_time = None
        
        return session_record
    
    def save_progress(self, filepath: Optional[str] = None) -> bool:
        """進捗データをファイルに保存"""
        try:
            save_path = filepath or self._progress_file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._progress_data.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"進捗データの保存に失敗しました: {e}")
            return False
    
    def load_progress(self, filepath: Optional[str] = None) -> bool:
        """進捗データをファイルから読み込み"""
        try:
            load_path = filepath or self._progress_file
            if not os.path.exists(load_path):
                print(f"進捗ファイルが見つかりません: {load_path}")
                return False
            
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._progress_data = ProgressData.from_dict(data)
            return True
        except Exception as e:
            print(f"進捗データの読み込みに失敗しました: {e}")
            return False
    
    def get_progress_data(self) -> ProgressData:
        """進捗データを取得"""
        return self._progress_data
    
    def get_session_history(self) -> List[SessionRecord]:
        """セッション履歴を取得"""
        return self._progress_data.session_history.copy()
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """待機中のレシピリストを取得"""
        return self._waiting_recipe_so_list.copy()
    
    def get_successful_recipes_amount(self) -> int:
        """成功したレシピ数を取得"""
        return self._successful_recipes_amount


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
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # イベントハンドラーの設定
    def on_recipe_spawned(sender, args):
        print("新しいレシピが生成されました！")
    
    def on_recipe_success(sender, args):
        print("レシピ配達成功！")
    
    def on_recipe_failed(sender, args):
        print("レシピ配達失敗...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # 進捗データの読み込み試行
    print("既存の進捗データを読み込み中...")
    delivery_manager.load_progress()
    
    # サンプル実行
    print("\n=== セッション開始 ===")
    delivery_manager.start_session()
    
    # 5秒間更新処理を実行
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # 100ms間隔で更新
    
    print(f"待機中のレシピ数: {len(delivery_manager.get_waiting_recipe_so_list())}")
    
    # サンプル配達テスト（成功）
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    
    print("\nサンドイッチを配達...")
    delivery_manager.deliver_recipe(plate)
    
    # サンプル配達テスト（失敗）
    plate2 = PlateKitchenObject()
    plate2.add_kitchen_object(bread)
    
    print("パンだけを配達（失敗テスト）...")
    delivery_manager.deliver_recipe(plate2)
    
    print(f"\n成功したレシピ数: {delivery_manager.get_successful_recipes_amount()}")
    
    # セッションを完了
    print("\n=== セッション完了 ===")
    session_record = delivery_manager.complete_session()
    print(f"セッション記録:")
    print(f"  - 成功: {session_record.successful_recipes}")
    print(f"  - 失敗: {session_record.failed_recipes}")
    print(f"  - 所要時間: {session_record.duration_seconds:.2f}秒")
    
    # 進捗データを保存
    print("\n進捗データを保存中...")
    if delivery_manager.save_progress():
        print("進捗データの保存に成功しました")
    
    # 進捗統計を表示
    progress = delivery_manager.get_progress_data()
    print(f"\n=== 累計統計 ===")
    print(f"総セッション数: {progress.total_sessions}")
    print(f"総成功レシピ数: {progress.total_successful_recipes}")
    print(f"総失敗レシピ数: {progress.total_failed_recipes}")
    print(f"セッション履歴: {len(progress.session_history)}件")