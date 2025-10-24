"""
進捗管理機能のテストスクリプト
"""
import os
import json
import time
from deliverManager import (
    DeliveryManager, KitchenGameManager, 
    KitchenObjectSO, RecipeSO, RecipeListSO, PlateKitchenObject,
    ProgressData, SessionRecord
)


def test_progress_data_serialization():
    """進捗データのシリアライズ・デシリアライズのテスト"""
    print("=== Test 1: Progress Data Serialization ===")
    
    # テストデータの作成
    session1 = SessionRecord(
        timestamp="2025-10-24T10:00:00",
        successful_recipes=5,
        failed_recipes=2,
        duration_seconds=300.0
    )
    
    progress = ProgressData(
        total_sessions=1,
        total_successful_recipes=5,
        total_failed_recipes=2,
        session_history=[session1]
    )
    
    # 辞書に変換
    data_dict = progress.to_dict()
    print(f"Serialized: {json.dumps(data_dict, indent=2, ensure_ascii=False)}")
    
    # 辞書から復元
    restored_progress = ProgressData.from_dict(data_dict)
    
    # 検証
    assert restored_progress.total_sessions == 1
    assert restored_progress.total_successful_recipes == 5
    assert restored_progress.total_failed_recipes == 2
    assert len(restored_progress.session_history) == 1
    assert restored_progress.session_history[0].successful_recipes == 5
    
    print("✓ Serialization test passed!\n")


def test_file_save_load():
    """ファイル保存・読み込みのテスト"""
    print("=== Test 2: File Save/Load ===")
    
    test_file = "test_progress.json"
    
    # テストファイルを削除（存在する場合）
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    recipe_list = RecipeListSO([sandwich_recipe])
    
    # DeliveryManagerインスタンスを作成（Singletonをリセット）
    DeliveryManager.reset_instance()
    delivery_manager = DeliveryManager.get_instance(recipe_list, test_file)
    
    # セッション1を開始・完了
    delivery_manager.start_session()
    delivery_manager._successful_recipes_amount = 3
    delivery_manager._session_failed_recipes = 1
    time.sleep(0.1)
    delivery_manager.complete_session()
    
    # 保存
    assert delivery_manager.save_progress() == True
    print("✓ Progress saved successfully")
    
    # ファイルの内容を確認
    with open(test_file, 'r') as f:
        saved_data = json.load(f)
    print(f"Saved data: {json.dumps(saved_data, indent=2, ensure_ascii=False)}")
    
    # 新しいインスタンスで読み込み
    DeliveryManager.reset_instance()
    delivery_manager2 = DeliveryManager.get_instance(recipe_list, test_file)
    assert delivery_manager2.load_progress() == True
    print("✓ Progress loaded successfully")
    
    # 検証
    progress = delivery_manager2.get_progress_data()
    assert progress.total_sessions == 1
    assert progress.total_successful_recipes == 3
    assert progress.total_failed_recipes == 1
    print("✓ Loaded data matches saved data")
    
    # セッション2を追加
    delivery_manager2.start_session()
    delivery_manager2._successful_recipes_amount = 5
    delivery_manager2._session_failed_recipes = 0
    time.sleep(0.1)
    delivery_manager2.complete_session()
    delivery_manager2.save_progress()
    
    # 再読み込みして累積を確認
    DeliveryManager.reset_instance()
    delivery_manager3 = DeliveryManager.get_instance(recipe_list, test_file)
    delivery_manager3.load_progress()
    progress3 = delivery_manager3.get_progress_data()
    
    assert progress3.total_sessions == 2
    assert progress3.total_successful_recipes == 8
    assert progress3.total_failed_recipes == 1
    assert len(progress3.session_history) == 2
    print("✓ Progress accumulation works correctly")
    
    # テストファイルを削除
    os.remove(test_file)
    print("✓ File save/load test passed!\n")


def test_session_completion():
    """セッション完了記録のテスト"""
    print("=== Test 3: Session Completion Recording ===")
    
    test_file = "test_session.json"
    
    # テストファイルを削除（存在する場合）
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    recipe_list = RecipeListSO([sandwich_recipe])
    
    # DeliveryManagerインスタンスを作成
    DeliveryManager.reset_instance()
    delivery_manager = DeliveryManager.get_instance(recipe_list, test_file)
    
    # セッション開始
    delivery_manager.start_session()
    start_time = time.time()
    
    # 配達テスト（成功）
    plate1 = PlateKitchenObject()
    plate1.add_kitchen_object(bread)
    plate1.add_kitchen_object(lettuce)
    plate1.add_kitchen_object(tomato)
    delivery_manager._waiting_recipe_so_list.append(sandwich_recipe)
    delivery_manager.deliver_recipe(plate1)
    
    # 配達テスト（失敗）
    plate2 = PlateKitchenObject()
    plate2.add_kitchen_object(bread)
    delivery_manager.deliver_recipe(plate2)
    
    time.sleep(0.5)  # 少し待機
    
    # セッション完了
    record = delivery_manager.complete_session()
    
    # 検証
    assert record.successful_recipes == 1
    assert record.failed_recipes == 1
    assert record.duration_seconds >= 0.5
    assert record.timestamp is not None
    print(f"Session record: Success={record.successful_recipes}, Failed={record.failed_recipes}, Duration={record.duration_seconds:.2f}s")
    
    # 進捗データを確認
    progress = delivery_manager.get_progress_data()
    assert progress.total_sessions == 1
    assert progress.total_successful_recipes == 1
    assert progress.total_failed_recipes == 1
    
    print("✓ Session completion test passed!\n")
    
    # テストファイルを削除
    if os.path.exists(test_file):
        os.remove(test_file)


def test_multiple_sessions():
    """複数セッションのテスト"""
    print("=== Test 4: Multiple Sessions ===")
    
    test_file = "test_multiple.json"
    
    # テストファイルを削除（存在する場合）
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # サンプルデータ作成
    tomato = KitchenObjectSO("Tomato", 1)
    recipe = RecipeSO("Tomato Recipe", [tomato])
    recipe_list = RecipeListSO([recipe])
    
    # DeliveryManagerインスタンスを作成
    DeliveryManager.reset_instance()
    delivery_manager = DeliveryManager.get_instance(recipe_list, test_file)
    
    # 複数セッションを実行
    for i in range(3):
        delivery_manager.start_session()
        delivery_manager._successful_recipes_amount = i + 1
        delivery_manager._session_failed_recipes = i
        time.sleep(0.1)
        delivery_manager.complete_session()
    
    # 保存
    delivery_manager.save_progress()
    
    # 検証
    progress = delivery_manager.get_progress_data()
    assert progress.total_sessions == 3
    assert progress.total_successful_recipes == 1 + 2 + 3
    assert progress.total_failed_recipes == 0 + 1 + 2
    assert len(progress.session_history) == 3
    
    # 各セッションの記録を確認
    for i, record in enumerate(progress.session_history):
        assert record.successful_recipes == i + 1
        assert record.failed_recipes == i
        print(f"Session {i+1}: Success={record.successful_recipes}, Failed={record.failed_recipes}")
    
    print("✓ Multiple sessions test passed!\n")
    
    # テストファイルを削除
    os.remove(test_file)


def run_all_tests():
    """全テストを実行"""
    print("=" * 60)
    print("Progress Management Tests")
    print("=" * 60 + "\n")
    
    try:
        test_progress_data_serialization()
        test_file_save_load()
        test_session_completion()
        test_multiple_sessions()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
