# ポモドーロタイマーWebアプリケーション アーキテクチャ案

## 1. 構成概要
- **バックエンド**：Flask（Python）
  - タイマー状態管理
  - 今日の進捗データ保存・取得
  - APIエンドポイント提供
- **フロントエンド**：HTML/CSS/JavaScript
  - UI表示（添付画像のデザイン再現）
  - タイマーのカウントダウン・円グラフアニメーション
  - ボタン操作（開始・リセット）
  - 進捗表示（完了数・集中時間）

## 2. ディレクトリ構成例
```
/workspaces/2025-10-24-Github-Copilot-Workshop-Python/
├── app.py                # Flaskアプリ本体
├── templates/
│   └── index.html        # メイン画面
├── static/
│   ├── css/
│   │   └── style.css     # デザイン
│   └── js/
│       └── timer.js      # タイマー・API連携
├── deliverManager.py     # 進捗管理ロジック
├── point.py              # 必要ならポイント管理
├── tests/                # ユニットテスト
│   ├── test_deliverManager.py
│   └── test_api.py
└── README.md
```

## 3. 主な機能設計
- タイマー機能：JavaScriptで実装、状態は必要に応じてFlask側と同期
- 進捗管理：Flaskで記録（ファイル/DB/セッション）、API経由で取得
- UI：円グラフはSVGやCanvasで実装、ボタン・進捗表示はHTML/CSS
- API設計例：
  - `/start`（POST）：タイマー開始
  - `/reset`（POST）：タイマーリセット
  - `/progress`（GET）：今日の進捗取得
  - `/complete`（POST）：1セッション完了時に記録

## 4. ユニットテスト容易化のための工夫
- ロジック層（タイマー・進捗管理）はFlaskやJSから独立したPythonモジュールに分離
- APIは個別にテスト可能な関数として分割
- データ保存は抽象化し、テスト時はモックやインメモリ実装に差し替え可能
- Flaskアプリはファクトリ関数（`create_app()`）で生成
- `/tests/`ディレクトリで各モジュールごとにテストファイル分離
- JSも関数分割し、Jest等で単体テスト可能な設計

## 5. 実装の流れ
1. Flaskアプリの雛形作成
2. HTML/CSS/JSでUIモックを再現
3. タイマー機能のJS実装
4. Flask APIの設計・実装
5. 進捗管理ロジックの実装
6. APIとフロントの連携

## 6. 技術ポイント
- タイマーは基本フロントで動かし、進捗のみサーバーに記録
- 状態管理はセッション or ユーザーID（ログイン不要ならセッションのみ）
- UIはモダンデザインをCSSで再現
- 必要に応じてAjax（fetch API）で非同期通信

---
このアーキテクチャを基に、拡張性・保守性・テスト容易性の高いWebアプリを開発します。