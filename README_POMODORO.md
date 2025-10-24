# ポモドーロタイマー - API & フロントエンド統合

このプロジェクトは、Flask バックエンドと HTML/CSS/JavaScript フロントエンドを使用したポモドーロタイマーアプリケーションです。

## 機能

### バックエンド API (Flask)
- **タイマー制御**
  - `/api/start` - タイマーを開始
  - `/api/pause` - タイマーを一時停止
  - `/api/reset` - タイマーをリセット
  - `/api/status` - 現在のタイマー状態を取得
  
- **進捗管理**
  - `/api/complete` - セッション完了を記録
  - `/api/progress` - 進捗履歴を取得
  - `/api/set_duration` - タイマーの時間を設定

### フロントエンド機能
- **リアルタイムタイマー表示**
  - MM:SS フォーマットでの残り時間表示
  - SVG を使用した円形プログレスバーアニメーション
  
- **操作ボタン**
  - 開始ボタン - タイマーをスタート
  - 一時停止ボタン - タイマーを停止
  - リセットボタン - タイマーを25分にリセット
  
- **進捗追跡**
  - 完了したセッション数の表示
  - セッション完了履歴の表示（タイムスタンプ付き）

### API統合
- **Fetch API による非同期通信**
  - 100ms ごとにサーバーから状態を取得
  - リアルタイムでUIを更新
  - タイマー完了時に自動的にセッションを記録

## セットアップ

### 必要要件
- Python 3.8+
- pip

### インストール

1. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

2. サーバーを起動:
```bash
python app.py
```

3. ブラウザで開く:
```
http://localhost:5000
```

## ファイル構成

```
.
├── app.py                  # Flask バックエンド API
├── deliverManager.py       # デリバリーマネージャー (既存コード)
├── point.py               # Point2D クラス (既存コード)
├── requirements.txt       # Python 依存関係
├── static/
│   ├── index.html        # メイン HTML
│   ├── style.css         # スタイルシート
│   └── app.js            # フロントエンド JavaScript
└── progress.json         # 進捗データ (自動生成)
```

## API エンドポイント詳細

### GET /api/status
タイマーの現在の状態を取得

**レスポンス:**
```json
{
  "is_running": false,
  "remaining_time": 1500,
  "total_time": 1500,
  "sessions_completed": 0
}
```

### POST /api/start
タイマーを開始

**レスポンス:**
```json
{
  "status": "started",
  "remaining_time": 1500,
  "total_time": 1500
}
```

### POST /api/pause
タイマーを一時停止

**レスポンス:**
```json
{
  "status": "paused",
  "remaining_time": 1450
}
```

### POST /api/reset
タイマーをリセット

**レスポンス:**
```json
{
  "status": "reset",
  "remaining_time": 1500,
  "total_time": 1500
}
```

### POST /api/complete
セッション完了を記録

**レスポンス:**
```json
{
  "status": "completed",
  "sessions_completed": 1,
  "record": {
    "timestamp": "2025-10-24T02:52:10.526666",
    "duration": 1500,
    "session_number": 1
  }
}
```

### GET /api/progress
進捗履歴を取得

**レスポンス:**
```json
{
  "sessions_completed": 1,
  "history": [
    {
      "timestamp": "2025-10-24T02:52:10.526666",
      "duration": 1500,
      "session_number": 1
    }
  ]
}
```

## 技術スタック

### バックエンド
- **Flask 3.0.0** - Web フレームワーク
- **flask-cors 4.0.0** - CORS サポート
- **Python 標準ライブラリ** - time, datetime, json

### フロントエンド
- **HTML5** - マークアップ
- **CSS3** - スタイリング (Flexbox, グラデーション, アニメーション)
- **Vanilla JavaScript** - ロジック (ES6+)
- **Fetch API** - HTTP リクエスト
- **SVG** - 円形プログレスバー

## 実装の詳細

### リアルタイム同期
- フロントエンドは 100ms ごとに `/api/status` エンドポイントをポーリング
- サーバー側でタイマーの残り時間を計算
- タイマーが実行中の場合、経過時間を考慮した残り時間を返却

### 進捗管理
- セッション完了時に `progress.json` ファイルに記録を保存
- サーバー起動時に自動的に履歴を読み込み
- タイマーが 0 になったら自動的にセッション完了を記録

### CORS サポート
- flask-cors により全てのオリジンからのアクセスを許可
- 開発環境での柔軟なテストを実現

## 使用方法

1. アプリケーションを起動
2. 「開始」ボタンをクリックしてタイマーをスタート
3. 円形プログレスバーが時間の経過を視覚的に表示
4. 「一時停止」でタイマーを停止、「リセット」で初期状態に戻す
5. タイマーが完了すると自動的にセッションが記録される
6. 進捗状況セクションで完了したセッションの履歴を確認

## セキュリティ注意事項

- このアプリケーションは開発用です
- 本番環境では以下の対策が必要:
  - HTTPS の使用
  - CORS ポリシーの制限
  - 認証・認可の実装
  - レート制限の追加
  - WSGI サーバー (Gunicorn 等) の使用
