# API仕様書

## 概要

SakeTrail APIは、AIラベル認識のためのPresigned URL払い出しAPIを提供しています。

- 認証: 必須（Cognito Hosted UIでログインし、Bearerトークン（JWT）を付与）
- レスポンス形式: JSON

---

## 認証設計

- AWS Cognito Hosted UIによるユーザー認証・Bearerトークン（JWT）方式を採用しています。
- すべてのAPIリクエスト時に、HTTPヘッダー `Authorization: Bearer <token>` を付与してください。
- API側でJWTの検証を行い、不正・期限切れの場合は401 Unauthorizedを返却します。
- 必要に応じて、Cognitoグループやカスタムクレームによるロール・権限制御も拡張可能です。

---

## 基本情報

- Base URL: `https://api.saketrail.com/v1`
- 認証: Bearer Token（ユーザー認証はCognito Hosted UIを利用、独自認証APIは未実装）
- レスポンス形式: JSON

## エンドポイント一覧

### 認証系API

> **注意**: 現在の実装ではCognito Hosted UIによる認証のみを採用しており、/auth/login, /auth/register等の独自APIは利用していません。ユーザー登録・ログインはCognitoの画面で行われます。
> 下記エンドポイントは将来の拡張用であり、現時点では未実装です。

#### ユーザー登録（未実装）
```
POST /auth/register
```

#### ログイン（未実装）
```
POST /auth/login
```

---

### お酒API

#### お酒一覧取得
未実装

#### お酒詳細取得
未実装

---

### レビューAPI

#### レビュー投稿
未実装

---

### AIラベル認識API

#### 画像アップロード用Presigned URL取得（認証必須）
```
POST /ai/recognize-label/presigned-url
```
- 画像アップロード用のS3 Presigned URLを払い出します。
- リクエスト時、必ず `Authorization: Bearer <JWT>` ヘッダーを付与してください。

**リクエスト例**
```http
POST /ai/recognize-label/presigned-url HTTP/1.1
Authorization: Bearer eyJraWQiOiJr...
Content-Type: application/json

{
  "content_type": "image/jpeg"
}
```

- `content_type`（必須）: アップロードする画像のMIMEタイプ（例: image/jpeg, image/png）
- 許可されるMIMEタイプ: image/jpeg, image/png, image/webp, image/gif
- 上記以外のMIMEタイプの場合は400エラー
- bodyが空、またはcontent_typeが無い場合も400エラー

**レスポンス**
```json
{
  "upload_url": "https://s3.amazonaws.com/bucket/uploads/jobid.jpg",
  "job_id": "string"
}
```

**認証エラー時のレスポンス例**
```json
{
  "error": {
    "code": "401",
    "message": "Unauthorized"
  }
}
```

#### 2. 画像アップロード（クライアント→S3, API外）
- 上記 `upload_url` に対してクライアントが直接PUTリクエストで画像をアップロードします。
- アップロード後、S3イベントでAIラベル認識ジョブが自動的に開始されます。

#### 3. 判別結果取得
```
GET /ai/recognize-label/{job_id}
```
- ジョブIDでラベル認識結果を取得します。

**レスポンス**
```json
{
  "job_id": "string",
  "status": "success", // running, success, failed
  "type": "sake", // sake, wine, beer, whisky など
  "result": {
    "name": "string",
    "brewery": "string",
    "specs": {
      "alcohol_percentage": 15.5
    },
    "image_url": "string",
    "confidence": 0.98
  },
  "created_at": "string",
  "updated_at": "string"
}
```

---

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

---

## 多様なお酒への対応・拡張性

- 本APIは日本酒だけでなく、ワイン・ビール・ウイスキー・リキュール・焼酎など多様なお酒に対応しています。
- すべてのエンドポイント・レスポンスで「type」フィールドを考慮し、今後のカテゴリ追加も容易です。
- AIラベル認識APIも多様なお酒の自動判別に対応しています。
- 今後も新しいお酒カテゴリや属性の追加、AIモデルの精度向上に柔軟に対応していきます。 