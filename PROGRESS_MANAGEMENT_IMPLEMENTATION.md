# 進捗管理ロジック実装ドキュメント

## 概要
このドキュメントは、DeliveryManagerクラスに実装された進捗管理機能について説明します。

## 実装内容

### 1. データクラス

#### SessionRecord
個別のセッション記録を保持するデータクラス。

```python
@dataclass
class SessionRecord:
    timestamp: str              # セッション完了時のタイムスタンプ
    successful_recipes: int     # 成功したレシピ数
    failed_recipes: int         # 失敗したレシピ数
    duration_seconds: float     # セッション所要時間（秒）
```

#### ProgressData
累積統計とセッション履歴を保持するデータクラス。

```python
@dataclass
class ProgressData:
    total_sessions: int                      # 総セッション数
    total_successful_recipes: int            # 総成功レシピ数
    total_failed_recipes: int                # 総失敗レシピ数
    session_history: List[SessionRecord]     # セッション履歴
```

### 2. DeliveryManagerクラスへの追加機能

#### プライベート変数
```python
self._progress_file: str                    # 進捗ファイルのパス
self._progress_data: ProgressData           # 進捗データ
self._session_start_time: Optional[float]   # セッション開始時刻
self._session_failed_recipes: int           # セッション内の失敗数
```

#### パブリックメソッド

##### start_session()
新しいセッションを開始します。
- セッション開始時刻を記録
- 成功/失敗カウンターをリセット

```python
delivery_manager.start_session()
```

##### complete_session() -> SessionRecord
セッションを完了し、記録を保存します。
- セッション記録を作成
- 進捗データを更新
- SessionRecordを返却

```python
record = delivery_manager.complete_session()
print(f"成功: {record.successful_recipes}")
```

##### save_progress(filepath: Optional[str] = None) -> bool
進捗データをJSON形式でファイルに保存します。
- デフォルトでは`progress_data.json`に保存
- カスタムパスを指定可能
- 保存成功時はTrue、失敗時はFalseを返す

```python
success = delivery_manager.save_progress()
# または
success = delivery_manager.save_progress("custom_path.json")
```

##### load_progress(filepath: Optional[str] = None) -> bool
進捗データをファイルから読み込みます。
- デフォルトでは`progress_data.json`から読み込み
- カスタムパスを指定可能
- 読み込み成功時はTrue、失敗時はFalseを返す

```python
success = delivery_manager.load_progress()
```

##### get_progress_data() -> ProgressData
現在の進捗データを取得します。

```python
progress = delivery_manager.get_progress_data()
print(f"総セッション数: {progress.total_sessions}")
```

##### get_session_history() -> List[SessionRecord]
セッション履歴のリストを取得します。

```python
history = delivery_manager.get_session_history()
for record in history:
    print(f"日時: {record.timestamp}, 成功: {record.successful_recipes}")
```

##### reset_instance() (クラスメソッド)
Singletonインスタンスをリセットします（テスト用）。

```python
DeliveryManager.reset_instance()
```

## 使用例

### 基本的な使用方法

```python
# 1. インスタンスを取得
delivery_manager = DeliveryManager.get_instance(recipe_list)

# 2. 既存の進捗データを読み込み
delivery_manager.load_progress()

# 3. セッションを開始
delivery_manager.start_session()

# 4. ゲームロジックを実行
# ... レシピの配達など ...

# 5. セッションを完了
record = delivery_manager.complete_session()
print(f"セッション結果: 成功={record.successful_recipes}, 失敗={record.failed_recipes}")

# 6. 進捗データを保存
delivery_manager.save_progress()

# 7. 統計情報を取得
progress = delivery_manager.get_progress_data()
print(f"累計: {progress.total_sessions}セッション")
```

### カスタムファイルパスの使用

```python
# カスタムファイルパスでインスタンスを作成
delivery_manager = DeliveryManager.get_instance(
    recipe_list, 
    progress_file="my_progress.json"
)

# カスタムファイルから読み込み/保存
delivery_manager.load_progress("my_progress.json")
delivery_manager.save_progress("my_progress.json")
```

## データフォーマット

### JSON形式
進捗データは以下のJSON形式で保存されます：

```json
{
  "total_sessions": 2,
  "total_successful_recipes": 8,
  "total_failed_recipes": 3,
  "session_history": [
    {
      "timestamp": "2025-10-24T10:00:00.000000",
      "successful_recipes": 5,
      "failed_recipes": 2,
      "duration_seconds": 300.5
    },
    {
      "timestamp": "2025-10-24T11:00:00.000000",
      "successful_recipes": 3,
      "failed_recipes": 1,
      "duration_seconds": 250.3
    }
  ]
}
```

## テスト

### テストスイート
`test_progress_management.py`に包括的なテストスイートが含まれています。

```bash
python3 test_progress_management.py
```

#### テスト内容
1. **Serialization Test**: データのシリアライズ/デシリアライズ
2. **File Save/Load Test**: ファイル保存と読み込み機能
3. **Session Completion Test**: セッション完了記録
4. **Multiple Sessions Test**: 複数セッションの累積

## エラーハンドリング

### save_progress()
- ファイル書き込み失敗時は`False`を返し、エラーメッセージを出力
- 例外が発生しても処理は継続

### load_progress()
- ファイルが存在しない場合は`False`を返し、メッセージを出力
- JSON解析エラー時は`False`を返し、エラーメッセージを出力

### complete_session()
- セッションが開始されていない場合は`ValueError`を送出

## セキュリティ

- CodeQLスキャン: 脆弱性0件
- SQLインジェクション対策済み（get_recipe_by_nameメソッドは参考実装）
- 安全なファイル操作

## 注意事項

1. **Singletonパターン**: DeliveryManagerはSingletonパターンを使用しています。
2. **ファイル管理**: `progress_data.json`は`.gitignore`に追加済み。
3. **エンコーディング**: JSON保存時は`ensure_ascii=False`でUTF-8対応。
4. **時刻**: タイムスタンプはISO 8601形式で保存。

## 今後の拡張可能性

- データベース対応（SQLite、PostgreSQLなど）
- クラウドストレージ対応
- 複数ユーザー対応
- より詳細な統計情報（平均時間、成功率など）
- グラフ表示用のデータエクスポート機能
