from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import time
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# タイマーの状態を管理
timer_state = {
    'is_running': False,
    'remaining_time': 25 * 60,  # 25分（秒単位）
    'total_time': 25 * 60,
    'start_time': None,
    'sessions_completed': 0,
    'progress_history': []
}

PROGRESS_FILE = 'progress.json'


def load_progress():
    """進捗データをファイルから読み込む"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_progress():
    """進捗データをファイルに保存"""
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(timer_state['progress_history'], f, indent=2)
    except IOError as e:
        print(f"Error saving progress: {e}")
    except Exception as e:
        print(f"Unexpected error saving progress: {e}")


@app.route('/')
def index():
    """フロントエンドのHTMLを返す"""
    return send_from_directory('static', 'index.html')


@app.route('/api/start', methods=['POST'])
def start_timer():
    """タイマーを開始"""
    if not timer_state['is_running']:
        timer_state['is_running'] = True
        timer_state['start_time'] = time.time()
        return jsonify({
            'status': 'started',
            'remaining_time': timer_state['remaining_time'],
            'total_time': timer_state['total_time']
        })
    return jsonify({
        'status': 'already_running',
        'remaining_time': timer_state['remaining_time']
    })


@app.route('/api/pause', methods=['POST'])
def pause_timer():
    """タイマーを一時停止"""
    if timer_state['is_running']:
        elapsed = time.time() - timer_state['start_time']
        timer_state['remaining_time'] = max(0, timer_state['remaining_time'] - elapsed)
        timer_state['is_running'] = False
        timer_state['start_time'] = None
        return jsonify({
            'status': 'paused',
            'remaining_time': timer_state['remaining_time']
        })
    return jsonify({
        'status': 'not_running',
        'remaining_time': timer_state['remaining_time']
    })


@app.route('/api/reset', methods=['POST'])
def reset_timer():
    """タイマーをリセット"""
    timer_state['is_running'] = False
    timer_state['remaining_time'] = timer_state['total_time']
    timer_state['start_time'] = None
    return jsonify({
        'status': 'reset',
        'remaining_time': timer_state['remaining_time'],
        'total_time': timer_state['total_time']
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """現在のタイマー状態を取得"""
    if timer_state['is_running'] and timer_state['start_time']:
        elapsed = time.time() - timer_state['start_time']
        remaining = max(0, timer_state['remaining_time'] - elapsed)
        
        # タイマーが完了した場合
        if remaining == 0:
            timer_state['is_running'] = False
            timer_state['remaining_time'] = 0
    else:
        remaining = timer_state['remaining_time']
    
    return jsonify({
        'is_running': timer_state['is_running'],
        'remaining_time': remaining,
        'total_time': timer_state['total_time'],
        'sessions_completed': timer_state['sessions_completed']
    })


@app.route('/api/complete', methods=['POST'])
def complete_session():
    """セッション完了を記録"""
    timer_state['sessions_completed'] += 1
    timer_state['is_running'] = False
    timer_state['remaining_time'] = timer_state['total_time']
    timer_state['start_time'] = None
    
    # 完了記録を保存
    session_record = {
        'timestamp': datetime.now().isoformat(),
        'duration': timer_state['total_time'],
        'session_number': timer_state['sessions_completed']
    }
    timer_state['progress_history'].append(session_record)
    save_progress()
    
    return jsonify({
        'status': 'completed',
        'sessions_completed': timer_state['sessions_completed'],
        'record': session_record
    })


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """進捗履歴を取得"""
    return jsonify({
        'sessions_completed': timer_state['sessions_completed'],
        'history': timer_state['progress_history']
    })


@app.route('/api/set_duration', methods=['POST'])
def set_duration():
    """タイマーの時間を設定（分単位）"""
    data = request.get_json()
    minutes = data.get('minutes', 25)
    
    if not timer_state['is_running']:
        timer_state['total_time'] = minutes * 60
        timer_state['remaining_time'] = minutes * 60
        return jsonify({
            'status': 'duration_set',
            'total_time': timer_state['total_time']
        })
    return jsonify({
        'status': 'error',
        'message': 'Cannot set duration while timer is running'
    })


if __name__ == '__main__':
    # 起動時に進捗履歴を読み込む
    timer_state['progress_history'] = load_progress()
    timer_state['sessions_completed'] = len(timer_state['progress_history'])
    
    print("Pomodoro Timer API starting...")
    print("Access the application at: http://localhost:5000")
    print("WARNING: This is a development server. Do not use in production!")
    print("For production, use a WSGI server like Gunicorn and set debug=False")
    app.run(debug=True, host='0.0.0.0', port=5000)
