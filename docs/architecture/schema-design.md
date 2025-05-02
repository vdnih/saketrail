# スキーマ設計ドキュメント

このドキュメントでは、SakeTrailアプリケーションのDynamoDBスキーマ設計・マスタ設計・エンティティ設計について記載します。

---

## 前提・設計方針

- **第一階層カテゴリ**は厳密にDB管理
- **第二階層以降（タグ等）は柔軟運用**
- **DynamoDBを利用し、生成AIも活用**
- 拡張性・クエリ効率・AI連携を重視

---

## 全体像：エンティティ構成

| エンティティ         | 用途                                             |
|----------------------|--------------------------------------------------|
| Category             | 第一階層カテゴリ（日本酒・ワイン等）のマスタ      |
| SakeItem             | お酒そのもののデータ（個別銘柄）                 |
| UserSakeEntry        | ユーザーの飲酒記録・レビュー                     |
| Tag                  | タグ情報（柔軟運用、AI/ユーザー両対応）          |
| GSI（例）            | category_id-index, user_id-index, tag-index など |

---

## 1. Category（カテゴリマスタ）

```json
{
  "PK": "Category#001",
  "SK": "Meta",
  "category_id": "Category#001",
  "name_ja": "日本酒",
  "name_en": "Sake",
  "icon_url": "/icons/sake.svg",
  "sort_order": 1,
  "field_schema": {
    "suggested_tags": ["辛口", "山田錦", "純米吟醸", "精米歩合50%"],
    "input_fields": ["精米歩合", "酒米", "日本酒度", "酸度"]
  }
}
```

**ポイント**
- `field_schema` でカテゴリごとの入力項目・タグ候補を定義（UI制御用）
- マスタで固定管理（ユーザー追加不可）

---

## 2. SakeItem（お酒情報）

```json
{
  "PK": "Sake#Dassai001",
  "SK": "Meta",
  "sake_id": "Dassai001",
  "name": "獺祭 純米大吟醸 45",
  "category_id": "Category#001",
  "category_name": "日本酒",
  "maker": "旭酒造",
  "origin": "山口県",
  "tags": ["純米大吟醸", "山田錦", "フルーティー"],
  "ai_generated_tags": [
    { "tag": "フルーティー", "confidence": 0.92 }
  ],
  "image_url": "/images/dassai.jpg"
}
```

**ポイント**
- タグは自由形式（後述のTagエンティティと連携）
- `ai_generated_tags` には信頼度スコアを持たせ、LLMと連携可能に

---

## 3. UserSakeEntry（ユーザー投稿・レビュー）

```json
{
  "PK": "User#123",
  "SK": "Sake#Dassai001",
  "user_id": "User#123",
  "sake_id": "Dassai001",
  "rating": 4.5,
  "review": "フルーティーで飲みやすかった。冷やがおすすめ。",
  "drink_date": "2025-04-30",
  "user_tags": ["冷や", "甘口", "初心者向け"]
}
```

**ポイント**
- パーティションキーがユーザー、ソートキーがお酒 → 「そのユーザーの飲んだ酒」を簡単に一覧取得
- `user_tags` は完全自由入力、AIで正規化しても良い

---

## 4. Tag（インデックス用、GSIで利用）

```json
{
  "PK": "Tag#フルーティー",
  "SK": "Sake#Dassai001",
  "tag": "フルーティー",
  "sake_id": "Dassai001",
  "category_id": "Category#001",
  "source": "ai",  // "user" or "ai"
  "confidence": 0.91
}
```

**ポイント**
- GSIで「tag-index」を定義し、タグ→酒を検索できるように
- `source`がuser/aiで分かるので信頼度に応じた絞り込みが可能

---

## 5. GSI（グローバルセカンダリインデックス）の設計例

| インデックス名        | PK           | SK         | 用途                         |
|----------------------|--------------|------------|------------------------------|
| category_id-index    | category_id  | sake_id    | カテゴリごとに酒を一覧取得   |
| user_id-index        | user_id      | drink_date | ユーザーの飲酒履歴（時系列） |
| tag-index            | tag          | sake_id    | タグから酒を逆引き検索       |

---

## 6. Job（ジョブ管理：AIラベル認識等）

AIラベル認識など非同期処理の進捗・結果管理のためのジョブ管理エンティティです。

```json
{
  "PK": "Job#123e4567-e89b-12d3-a456-426614174000",
  "SK": "Meta",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "running", // running, success, failed
  "type": "sake", // sake, wine, beer, whisky など
  "request": {
    "image_url": "/uploads/jobid.jpg"
  },
  "result": {
    "name": "獺祭 純米大吟醸 45",
    "category_id": "Category#001",
    "confidence": 0.98
  },
  "error": null,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:01:00Z"
}
```

**ポイント**
- `job_id`はUUIDで払い出し、PKに利用
- `status`で進捗管理（running, success, failed）
- `type`でお酒カテゴリを明示
- `request`に入力情報、`result`にAI判別結果を格納
- `error`には失敗時のエラー内容を格納
- `created_at`/`updated_at`で時系列管理

---

### ジョブ管理用GSI設計例

| インデックス名   | PK      | SK        | 用途                         |
|------------------|---------|-----------|------------------------------|
| status-index     | status  | created_at| ステータスごとにジョブ一覧   |
| type-index       | type    | created_at| お酒カテゴリごとにジョブ一覧 |
| user_id-index    | user_id | created_at| ユーザーごとのジョブ履歴     |

---

## まとめ

| 構成       | 内容                                                                 |
|------------|----------------------------------------------------------------------|
| カテゴリ   | 厳密にDBで管理。入力UIも制御できるようスキーマ持たせる               |
| お酒情報   | タグ付き・カテゴリ付きで保存。AIタグ・画像など拡張性重視             |
| ユーザー記録 | 一意に管理し、GSIで履歴や分析も容易                                 |
| タグ       | 柔軟入力を許しつつ、GSIやAIで整理可能に                              |


