// タイマーの状態管理
class PomodoroTimer {
    constructor() {
        // デフォルトは25分（1500秒）
        this.totalSeconds = 25 * 60;
        this.remainingSeconds = this.totalSeconds;
        this.isRunning = false;
        this.intervalId = null;
        
        // DOM要素の取得
        this.timerText = document.getElementById('timer-text');
        this.startBtn = document.getElementById('start-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.progressCircle = document.querySelector('.progress-ring-circle');
        
        // 円グラフの設定
        this.setupProgressCircle();
        
        // イベントリスナーの設定
        this.setupEventListeners();
        
        // 初期表示を更新
        this.updateDisplay();
    }
    
    setupProgressCircle() {
        // 円の周長を計算
        const radius = this.progressCircle.r.baseVal.value;
        this.circumference = radius * 2 * Math.PI;
        
        // stroke-dasharray と stroke-dashoffset を設定
        this.progressCircle.style.strokeDasharray = `${this.circumference} ${this.circumference}`;
        this.progressCircle.style.strokeDashoffset = 0;
    }
    
    setupEventListeners() {
        this.startBtn.addEventListener('click', () => {
            if (this.isRunning) {
                this.pause();
            } else {
                this.start();
            }
        });
        
        this.resetBtn.addEventListener('click', () => {
            this.reset();
        });
    }
    
    start() {
        this.isRunning = true;
        this.startBtn.textContent = '一時停止';
        this.startBtn.classList.add('paused');
        
        this.intervalId = setInterval(() => {
            this.tick();
        }, 1000);
    }
    
    pause() {
        this.isRunning = false;
        this.startBtn.textContent = '再開';
        this.startBtn.classList.remove('paused');
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    reset() {
        this.pause();
        this.remainingSeconds = this.totalSeconds;
        this.startBtn.textContent = '開始';
        this.updateDisplay();
    }
    
    tick() {
        if (this.remainingSeconds > 0) {
            this.remainingSeconds--;
            this.updateDisplay();
        } else {
            // タイマー終了
            this.pause();
            this.onTimerComplete();
        }
    }
    
    updateDisplay() {
        // 時間表示を更新
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        this.timerText.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        
        // 円グラフのアニメーション更新
        this.updateProgressCircle();
    }
    
    updateProgressCircle() {
        // 進捗率を計算（0〜1）
        const progress = this.remainingSeconds / this.totalSeconds;
        
        // stroke-dashoffsetを更新（逆方向に進むように）
        const offset = this.circumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
        
        // 色を変更（残り時間によって）
        if (progress > 0.5) {
            this.progressCircle.style.stroke = '#4CAF50'; // 緑
        } else if (progress > 0.25) {
            this.progressCircle.style.stroke = '#FF9800'; // オレンジ
        } else {
            this.progressCircle.style.stroke = '#F44336'; // 赤
        }
    }
    
    onTimerComplete() {
        // タイマー完了時の処理
        alert('ポモドーロタイマーが完了しました！休憩時間です。');
        this.reset();
    }
}

// ページ読み込み時にタイマーを初期化
document.addEventListener('DOMContentLoaded', () => {
    const timer = new PomodoroTimer();
});
