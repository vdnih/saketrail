# AIラベル認識機能設計ドキュメント

## 1. 概要

- ユーザーが日本酒、ワイン、ビール、ウイスキー等、さまざまなお酒のラベル画像をアップロード
- S3に保存 → S3イベントでLambda起動 → LambdaがOpenAI API（gpt-4.1 Vision）で画像認識
- 結果（銘柄名・種類・スペック等）をDynamoDBに格納
- クライアントはジョブIDで結果をポーリング取得
- お酒の種類はAIが自動判別し、必要に応じてユーザーが修正可能

## 2. アーキテクチャ概要

- 画像アップロードAPI（API Gateway or Presigned URL）でS3に画像保存
- S3イベントでLambda起動
- LambdaがOpenAI API（gpt-4.1 Vision）を呼び出し、認識結果（銘柄名・種類・スペック等）をDynamoDBに保存
- クライアントはジョブIDで結果取得APIをポーリング
- お酒の種類ごとに記録・検索・履歴機能でフィルタ可能

## 3. シーケンス図（テキスト）

1. クライアント → API Gateway: 画像アップロードリクエスト
2. API Gateway → S3: Presigned URL払い出し
3. クライアント → S3: 画像アップロード
4. S3 → Lambda: S3イベントでLambda起動
5. Lambda → OpenAI API: 画像認識リクエスト
6. Lambda → DynamoDB: 結果保存
7. クライアント → API Gateway: 結果取得リクエスト
8. API Gateway → DynamoDB: 結果取得

## 4. API設計

| API名                | メソッド | パス                     | 概要                     | ステータス |
|----------------------|----------|--------------------------|--------------------------|------------|
| 画像アップロード      | POST     | /ai/recognize-label      | S3に画像をアップロードし、ジョブIDを返す | 未実装     |
| 判別結果取得         | GET      | /ai/recognize-label/{job_id} | ジョブIDでDynamoDBから判別結果を取得 | 未実装     |

- 画像アップロードAPIはPresigned URL方式も可
- 判別結果には「お酒の種類（type）」フィールドを含める

## 5. Lambda処理フロー

- S3に画像がアップロードされる
- S3イベントでLambdaが起動
- Lambdaが画像を取得し、OpenAI API（gpt-4.1 Vision）にリクエスト
- OpenAIのレスポンス（銘柄名・種類・スペック・信頼度など）をパース
- DynamoDBに「ジョブID」「種類（type）」「結果」「ステータス（完了/失敗）」を保存

## 6. DynamoDB設計（例）

| job_id (PK) | status   | type     | result         | created_at         | updated_at         |
|-------------|----------|----------|---------------|--------------------|--------------------|
| uuid        | running  | null     | null          | 2024-06-01T12:00Z  | 2024-06-01T12:00Z  |
| uuid        | success  | sake     | {json result} | 2024-06-01T12:00Z  | 2024-06-01T12:01Z  |
| uuid        | success  | wine     | {json result} | 2024-06-01T12:00Z  | 2024-06-01T12:01Z  |
| uuid        | success  | beer     | {json result} | 2024-06-01T12:00Z  | 2024-06-01T12:01Z  |
| uuid        | failed   | null     | {error}       | 2024-06-01T12:00Z  | 2024-06-01T12:01Z  |

- type: sake, wine, beer, whisky, etc.
- result: 銘柄名、蔵元/メーカー、スペック、画像URL、AI信頼度など

## 7. UI/UX設計

- 画像アップロード後は「判別中...」の進捗表示
- 判別完了時に「お酒の種類」「銘柄名」「スペック」等を表示
- 必要に応じてユーザーが「種類」や「銘柄名」を修正可能
- 再試行・手動入力への導線も用意
- 検索・履歴画面で「お酒の種類」ごとにフィルタ可能

## 8. 今後の拡張性

- 新しいお酒カテゴリ（リキュール、焼酎等）の追加も容易
- AIモデルのバージョン管理・精度向上
- モバイル対応（カメラ連携強化）
- WebSocket等によるリアルタイム通知
- 他サービス（酒データベース等）との連携

## 9. ジョブIDの管理

- ジョブIDはUUID（Universally Unique Identifier）を利用し、Presigned URL払い出しAPIリクエスト時にサーバー側で生成する。
- ジョブIDはS3オブジェクトキー（例: uploads/{job_id}.jpg）に含めて保存し、S3イベントでLambdaが起動した際にオブジェクトキーからジョブIDを特定できるようにする。
- DynamoDBではジョブIDをパーティションキー（PK）として、ステータス・種類・結果・タイムスタンプ等を管理する。
- クライアントは画像アップロード後、払い出されたジョブIDを保持し、結果取得API（/ai/recognize-label/{job_id}）で非同期に結果を取得する。 