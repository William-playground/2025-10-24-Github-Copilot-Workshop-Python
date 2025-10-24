// API Base URL
const API_BASE_URL = window.location.origin;

// DOM要素
const timerDisplay = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const resetBtn = document.getElementById('reset-btn');
const sessionsCompleted = document.getElementById('sessions-completed');
const historyList = document.getElementById('history-list');
const progressCircle = document.getElementById('progress-circle');

// タイマーの状態
let updateInterval = null;
let totalTime = 25 * 60; // 25分（秒単位）

// 円グラフの設定
const radius = progressCircle.r.baseVal.value;
const circumference = radius * 2 * Math.PI;
progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
progressCircle.style.strokeDashoffset = circumference;

/**
 * 時間を MM:SS フォーマットに変換
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * 円グラフの進捗を更新
 */
function updateProgress(remaining, total) {
    const percent = remaining / total;
    const offset = circumference - percent * circumference;
    progressCircle.style.strokeDashoffset = offset;
}

/**
 * APIリクエストを送信
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(`${API_BASE_URL}/api/${endpoint}`, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

/**
 * タイマー状態を取得してUIを更新
 */
async function updateTimerDisplay() {
    const status = await apiRequest('status');
    if (status) {
        const remaining = Math.max(0, status.remaining_time);
        timerDisplay.textContent = formatTime(remaining);
        updateProgress(remaining, status.total_time);
        sessionsCompleted.textContent = status.sessions_completed;
        
        // タイマーが完了したら自動的に記録
        if (status.is_running && remaining === 0) {
            await completeSession();
            stopUpdateInterval();
        }
    }
}

/**
 * 進捗履歴を取得してUIを更新
 */
async function updateProgressHistory() {
    const progress = await apiRequest('progress');
    if (progress && progress.history) {
        historyList.innerHTML = '';
        
        // 最新の履歴を上に表示（逆順）
        const reversedHistory = [...progress.history].reverse();
        reversedHistory.forEach(record => {
            const item = document.createElement('div');
            item.className = 'history-item';
            
            const timestamp = new Date(record.timestamp);
            const timeStr = timestamp.toLocaleString('ja-JP', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            item.innerHTML = `
                <span class="history-time">${timeStr}</span>
                <span class="history-session">セッション #${record.session_number}</span>
            `;
            historyList.appendChild(item);
        });
    }
}

/**
 * 定期更新を開始
 */
function startUpdateInterval() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    updateInterval = setInterval(updateTimerDisplay, 100); // 100msごとに更新
}

/**
 * 定期更新を停止
 */
function stopUpdateInterval() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

/**
 * セッション完了を記録
 */
async function completeSession() {
    const result = await apiRequest('complete', 'POST');
    if (result && result.status === 'completed') {
        await updateProgressHistory();
        alert('🎉 ポモドーロセッションが完了しました！');
    }
}

/**
 * 開始ボタンのクリックハンドラ
 */
startBtn.addEventListener('click', async () => {
    const result = await apiRequest('start', 'POST');
    if (result) {
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        startUpdateInterval();
    }
});

/**
 * 一時停止ボタンのクリックハンドラ
 */
pauseBtn.addEventListener('click', async () => {
    const result = await apiRequest('pause', 'POST');
    if (result) {
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        stopUpdateInterval();
        await updateTimerDisplay();
    }
});

/**
 * リセットボタンのクリックハンドラ
 */
resetBtn.addEventListener('click', async () => {
    const result = await apiRequest('reset', 'POST');
    if (result) {
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        stopUpdateInterval();
        await updateTimerDisplay();
    }
});

/**
 * 初期化
 */
async function init() {
    // 初期状態を取得
    await updateTimerDisplay();
    await updateProgressHistory();
    
    // ボタンの初期状態を設定
    const status = await apiRequest('status');
    if (status) {
        if (status.is_running) {
            startBtn.disabled = true;
            pauseBtn.disabled = false;
            startUpdateInterval();
        } else {
            startBtn.disabled = false;
            pauseBtn.disabled = true;
        }
        totalTime = status.total_time;
    }
}

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', init);

// ページを離れる前に確認（タイマー実行中の場合）
window.addEventListener('beforeunload', (e) => {
    if (updateInterval) {
        e.preventDefault();
        e.returnValue = '';
    }
});
