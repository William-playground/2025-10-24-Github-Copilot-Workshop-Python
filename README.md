# Kitchen Game - レシピ配達ゲーム

このプロジェクトは、GitHub Copilot ワークショップの一環として作成された、キッチンゲームのレシピ配達管理システムです。

## 📋 プロジェクト概要

プレイヤーは待機中のレシピに合わせて材料を選択し、正しい組み合わせで配達することでポイントを獲得します。連続して成功するとコンボ倍率が上がり、より多くのポイントを獲得できます。

## ✨ 機能

### ステージ8で実装された機能

1. **データベース対応**
   - SQLite データベースによる永続的なデータ保存
   - レシピ、ゲームセッション、配達履歴の管理
   - プレイヤー統計の記録
   - SQL インジェクション脆弱性の修正（パラメータ化クエリ使用）

2. **レスポンシブ Web UI**
   - Flask ベースの Web アプリケーション
   - モバイルフレンドリーなレスポンシブデザイン
   - リアルタイムでのゲーム状態更新
   - 直感的な材料選択と配達システム

3. **拡張ポイント管理**
   - 基本ポイント: レシピの材料数 × 50
   - コンボシステム: 連続成功でポイント倍率アップ
     - 3連続成功: 1.5倍
     - 5連続成功: 2.0倍
   - ストリーク記録: 現在のストリークと最高記録を追跡

4. **セッション管理**
   - ゲームセッションの開始・終了
   - セッションごとの統計記録
   - プレイヤー全体の累積統計

## 🚀 セットアップと実行

### 必要な環境
- Python 3.11+
- pip

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/William-playground/2025-10-24-Github-Copilot-Workshop-Python.git
cd 2025-10-24-Github-Copilot-Workshop-Python
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. データベースモジュールのテスト（オプション）
```bash
python database.py
```

4. Web アプリケーションの起動
```bash
python app.py
```

5. ブラウザで http://localhost:5000 にアクセス

### コマンドライン版の実行

```bash
python deliverManager.py
```

## 🎮 使い方

### Web UI
1. **ゲーム開始**: 「ゲーム開始」ボタンをクリック
2. **材料選択**: 待機中のレシピを確認し、該当する材料をクリックして選択
3. **配達**: 「配達する」ボタンをクリックして配達
4. **ゲーム終了**: 「ゲーム終了」ボタンでセッションを終了し、統計を保存

### レシピ例
- **Sandwich**: パン、レタス、トマト
- **Salad**: レタス、トマト
- **Cheese Sandwich**: パン、チーズ
- **Burger**: パン、肉、レタス

## 🔒 セキュリティ

### 修正された脆弱性
- **SQL インジェクション**: `deliverManager.py` の `get_recipe_by_name` メソッドで、文字列連結ではなくパラメータ化クエリを使用するように修正

### セキュアな実装
- すべてのデータベースクエリでパラメータ化クエリを使用
- SQLite の `Row` オブジェクトを使用した安全なデータ取得
- コンテキストマネージャーによる適切なトランザクション管理

## 📁 プロジェクト構造

```
.
├── app.py              # Flask Web アプリケーション
├── database.py         # データベースアクセス層
├── deliverManager.py   # ゲームロジックと配達管理
├── point.py            # 2D ポイントクラス
├── requirements.txt    # Python 依存関係
├── templates/
│   └── index.html      # Web UI テンプレート
└── static/
    ├── css/
    │   └── style.css   # レスポンシブスタイルシート
    └── js/
        └── game.js     # フロントエンド JavaScript
```

## 🧪 API エンドポイント

- `POST /api/start` - ゲームセッションを開始
- `POST /api/stop` - ゲームセッションを終了
- `GET /api/status` - 現在のゲーム状態を取得
- `POST /api/deliver` - レシピを配達
- `GET /api/statistics` - プレイヤー統計を取得
- `GET /api/history` - ゲーム履歴を取得

## 📱 レスポンシブデザイン

このアプリケーションは以下のデバイスサイズに対応しています：
- デスクトップ (1400px+)
- タブレット (768px - 1399px)
- モバイル (< 768px)

## 🎓 ワークショップ情報

ワークショップの手順：https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0

## 📝 ライセンス

© 2025 Kitchen Game - GitHub Copilot Workshop
