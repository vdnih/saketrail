# API仕様書

## 概要

SakeTrail APIは、日本酒に関する情報を管理・提供するRESTful APIです。

## 基本情報

- Base URL: `https://api.saketrail.com/v1`
- 認証: Bearer Token
- レスポンス形式: JSON

## エンドポイント一覧

### 認証系API

#### ユーザー登録
```
POST /auth/register
```

**リクエスト**
```json
{
  "email": "string",
  "password": "string",
  "username": "string"
}
```

**レスポンス**
```json
{
  "user_id": "string",
  "email": "string",
  "username": "string",
  "created_at": "string"
}
```

#### ログイン
```
POST /auth/login
```

**リクエスト**
```json
{
  "email": "string",
  "password": "string"
}
```

**レスポンス**
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 日本酒API

#### 日本酒一覧取得
```
GET /sakes
```

**クエリパラメータ**
- `page`: ページ番号（デフォルト: 1）
- `per_page`: 1ページあたりの件数（デフォルト: 20）
- `sort`: ソート順（created_at, rating）
- `order`: 昇順/降順（asc, desc）

**レスポンス**
```json
{
  "items": [
    {
      "sake_id": "string",
      "name": "string",
      "brewery": "string",
      "type": "string",
      "rating": number,
      "image_url": "string"
    }
  ],
  "total": number,
  "page": number,
  "per_page": number
}
```

#### 日本酒詳細取得
```
GET /sakes/{sake_id}
```

**レスポンス**
```json
{
  "sake_id": "string",
  "name": "string",
  "brewery": "string",
  "type": "string",
  "description": "string",
  "ingredients": {
    "rice": "string",
    "water": "string",
    "koji": "string"
  },
  "specs": {
    "alcohol_percentage": number,
    "polishing_ratio": number,
    "sake_meter_value": number
  },
  "rating": {
    "average": number,
    "count": number
  },
  "images": [
    {
      "url": "string",
      "type": "string"
    }
  ],
  "created_at": "string",
  "updated_at": "string"
}
```

### レビューAPI

#### レビュー投稿
```
POST /sakes/{sake_id}/reviews
```

**リクエスト**
```json
{
  "rating": number,
  "comment": "string",
  "tasting_notes": {
    "aroma": "string",
    "taste": "string",
    "finish": "string"
  },
  "images": [
    {
      "data": "base64 string",
      "type": "string"
    }
  ]
}
```

**レスポンス**
```json
{
  "review_id": "string",
  "sake_id": "string",
  "user_id": "string",
  "rating": number,
  "comment": "string",
  "tasting_notes": {
    "aroma": "string",
    "taste": "string",
    "finish": "string"
  },
  "images": [
    {
      "url": "string",
      "type": "string"
    }
  ],
  "created_at": "string"
}
```

## エラーレスポンス

### エラーコード
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity
- 429: Too Many Requests
- 500: Internal Server Error

### エラーレスポンス形式
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## レート制限

- 認証なし: 60リクエスト/時間
- 認証あり: 1000リクエスト/時間

## バージョニング

APIのバージョンはURLのパスに含まれます（例: `/v1/sakes`）。
メジャーバージョンの変更時は、下位互換性のない変更が含まれる可能性があります。 