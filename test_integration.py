#!/usr/bin/env python
"""
統合テスト - APIとフロントエンドの連携をテスト
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api_status():
    """タイマー状態取得のテスト"""
    print("Testing /api/status...")
    response = requests.get(f"{BASE_URL}/api/status")
    assert response.status_code == 200
    data = response.json()
    assert 'is_running' in data
    assert 'remaining_time' in data
    assert 'total_time' in data
    assert 'sessions_completed' in data
    print("✓ Status endpoint works correctly")
    return data

def test_api_start():
    """タイマー開始のテスト"""
    print("\nTesting /api/start...")
    response = requests.post(f"{BASE_URL}/api/start")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['started', 'already_running']
    print("✓ Start endpoint works correctly")
    return data

def test_api_pause():
    """タイマー一時停止のテスト"""
    print("\nTesting /api/pause...")
    response = requests.post(f"{BASE_URL}/api/pause")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['paused', 'not_running']
    print("✓ Pause endpoint works correctly")
    return data

def test_api_reset():
    """タイマーリセットのテスト"""
    print("\nTesting /api/reset...")
    response = requests.post(f"{BASE_URL}/api/reset")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'reset'
    assert data['remaining_time'] == data['total_time']
    print("✓ Reset endpoint works correctly")
    return data

def test_api_progress():
    """進捗取得のテスト"""
    print("\nTesting /api/progress...")
    response = requests.get(f"{BASE_URL}/api/progress")
    assert response.status_code == 200
    data = response.json()
    assert 'sessions_completed' in data
    assert 'history' in data
    assert isinstance(data['history'], list)
    print("✓ Progress endpoint works correctly")
    return data

def test_timer_countdown():
    """タイマーのカウントダウンをテスト"""
    print("\nTesting timer countdown...")
    
    # リセット
    requests.post(f"{BASE_URL}/api/reset")
    
    # 開始
    requests.post(f"{BASE_URL}/api/start")
    time.sleep(1)
    
    # 状態確認
    status = requests.get(f"{BASE_URL}/api/status").json()
    assert status['is_running'] == True
    initial_time = status['remaining_time']
    
    # 2秒待つ
    time.sleep(2)
    
    # 再度状態確認
    status = requests.get(f"{BASE_URL}/api/status").json()
    final_time = status['remaining_time']
    
    # 時間が減っていることを確認
    time_diff = initial_time - final_time
    assert 1.5 < time_diff < 2.5, f"Expected time difference ~2s, got {time_diff}s"
    
    print(f"✓ Timer is counting down correctly (decreased by {time_diff:.2f}s)")
    
    # 一時停止
    requests.post(f"{BASE_URL}/api/pause")

def test_frontend_accessible():
    """フロントエンドにアクセスできることをテスト"""
    print("\nTesting frontend accessibility...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert 'ポモドーロタイマー' in response.text
    print("✓ Frontend is accessible")

def test_complete_workflow():
    """完全なワークフローのテスト"""
    print("\n" + "="*50)
    print("Running complete workflow test...")
    print("="*50)
    
    # 1. リセット
    print("\n1. Resetting timer...")
    reset_data = test_api_reset()
    assert reset_data['remaining_time'] == 1500  # 25分
    
    # 2. 開始
    print("\n2. Starting timer...")
    start_data = test_api_start()
    
    # 3. 少し待つ
    print("\n3. Waiting 2 seconds...")
    time.sleep(2)
    
    # 4. 状態確認
    print("\n4. Checking status...")
    status_data = test_api_status()
    assert status_data['is_running'] == True
    assert status_data['remaining_time'] < 1500
    
    # 5. 一時停止
    print("\n5. Pausing timer...")
    pause_data = test_api_pause()
    
    # 6. 状態確認（停止していることを確認）
    print("\n6. Verifying pause...")
    status_data = test_api_status()
    assert status_data['is_running'] == False
    
    # 7. 進捗確認
    print("\n7. Checking progress...")
    progress_data = test_api_progress()
    
    print("\n" + "="*50)
    print("✅ All workflow tests passed!")
    print("="*50)

if __name__ == "__main__":
    try:
        print("="*50)
        print("API Integration Test Suite")
        print("="*50)
        print(f"Testing server at: {BASE_URL}")
        print()
        
        # 個別テスト
        test_frontend_accessible()
        test_api_status()
        test_api_reset()
        test_api_start()
        test_timer_countdown()
        test_api_pause()
        test_api_progress()
        
        # 完全なワークフローテスト
        test_complete_workflow()
        
        print("\n" + "="*50)
        print("🎉 All tests passed successfully!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to server at {BASE_URL}")
        print("Please make sure the Flask server is running:")
        print("  python app.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
