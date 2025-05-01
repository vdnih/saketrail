# インフラストラクチャ構成

## AWS CDKプロジェクト構成

### 1. プロジェクトファイル構成

```text
infra/
├── cdk.json           # CDKアプリケーションの設定ファイル
├── pyproject.toml     # Poetryによる依存関係管理
├── app.py            # CDKアプリケーションのエントリーポイント
└── saketrail_cdk/    # CDKスタック定義
    └── stacks/       # 各種スタック
        ├── storage_stack.py   # ストレージ関連（S3, DynamoDB）
        ├── auth_stack.py      # 認証関連（Cognito）
        └── api_stack.py       # API関連（API Gateway, Lambda）
```

### 2. 主要設定ファイル

#### cdk.json
CDKアプリケーションの主要な設定ファイルで、以下の設定を含みます：
- アプリケーションのエントリーポイント（`app.py`）
- ウォッチ対象のファイル
- CDKのコンテキスト設定

```json
{
  "app": "python app.py",
  "watch": {
    "include": ["**"],
    "exclude": [
      "README.md",
      "cdk*.json",
      "requirements*.txt",
      "source.bat",
      "**/__init__.py",
      "python/__pycache__/**",
      "tests",
      "*.pyc"
    ]
  },
  "context": {
    // CDKの各種設定
  }
}
```

### 3. デプロイメント環境

プロジェクトは以下の環境を持ちます：
- Development (dev)
- Staging (staging)
- Production (prod)

各環境は独立したAWSアカウントにデプロイされ、環境固有の設定を持ちます。

### 4. スタック構成と作成リソース

#### Storage Stack
ユーザーデータ、お酒の情報、レビュー、画像などを管理するためのストレージリソースを提供します。

**作成リソース：**
- **S3バケット**
  - 画像ストレージ用バケット
    - ボトル画像の保存
    - ユーザーアップロード画像の保存
  - フロントエンドアプリケーション配信用バケット
    - Flutterアプリケーションのウェブビルド成果物の配信

- **DynamoDBテーブル**
  - ユーザーテーブル
    - ユーザープロファイル情報の管理
    - 好みの設定やカスタマイズ情報の保存
  - お酒テーブル
    - お酒の基本情報（名前、種類、製造元など）
    - AI解析結果の保存
  - レビューテーブル
    - ユーザーによるレビュー情報
    - 評価点数、コメント、画像参照などの保存

#### Auth Stack
ユーザー認証、認可、およびセキュリティ管理のためのリソースを提供します。

**作成リソース：**
- **Amazon Cognito**
  - User Pool
    - ユーザー登録・認証の管理
    - パスワードポリシーの設定
    - MFAの設定
  - Identity Pool
    - AWSリソースへのアクセス権限管理
    - S3バケットへの直接アクセス権限
  - User Pool Client
    - モバイルアプリケーション用の認証クライアント設定

- **Lambda関数（認証トリガー）**
  - カスタム認証フロー処理
  - サインアップ時の追加バリデーション
  - ユーザー属性の自動設定

### 認証認可設計詳細

#### 1. 認証フロー
- **サインアップ**: メールアドレス・パスワードで新規登録。メール認証による有効化。
- **ログイン**: メールアドレス・パスワードで認証。Cognito User PoolでJWTトークン発行。
- **セッション管理**: アクセストークン/リフレッシュトークンによるセッション維持。
- **パスワードリセット**: メールによるリセットリンク送信。
- **ログアウト**: トークンの無効化。

#### 2. ユーザー属性設計
- 必須属性: メールアドレス、パスワード
- 任意属性: 表示名、プロフィール画像URL、登録日
- 拡張性: Lambdaトリガーでカスタム属性追加可能

#### 3. 権限設計
- **一般ユーザーのみ**: すべてのユーザーは同じ権限でアプリの標準機能を利用
- ロールや管理者権限の区別は設けない

#### 4. セキュリティ要件
- パスワードポリシー（長さ・複雑性）
- メール認証必須
- 多要素認証（MFA）対応
- アカウントロック（一定回数失敗時）
- HTTPS通信必須
- トークンの安全な保存（Secure Storage推奨）

#### 5. 外部認証（ソーシャルログイン）
- Google, Apple, LINE等のIdP連携拡張性あり
- 必要に応じてCognito User PoolのFederation機能を利用

#### API Stack
アプリケーションのバックエンドAPIとフロントエンド配信のためのリソースを提供します。

**作成リソース：**
- **API Gateway**
  - REST API
    - お酒情報の取得・登録・更新API
    - レビュー投稿・取得API
    - ユーザー情報管理API
  - WebSocket API
    - リアルタイム通知機能
    - チャット機能（将来実装予定）

- **Lambda関数**
  - API処理用関数
    - 各APIエンドポイントのビジネスロジック実装
  - AI処理用関数
    - OpenAI APIとの連携
    - 画像解析処理
  - バッチ処理用関数
    - 定期的なデータ集計
    - レコメンデーション計算

- **CloudFront**
  - フロントエンドアプリケーション配信
    - S3バケットのコンテンツ配信
    - SSL/TLS対応
    - カスタムドメイン設定

- **Route 53**
  - DNSレコード管理
  - ドメインルーティング設定

- **ACM（AWS Certificate Manager）**
  - SSL/TLS証明書の管理
  - カスタムドメインのセキュア化

### 5. セキュリティ設定

- S3バケットの暗号化設定
  - サーバーサイド暗号化（SSE-S3）
  - パブリックアクセスのブロック
- APIエンドポイントの認証
  - Cognitoとの統合
  - APIキーの管理
- クロスオリジンリソース共有（CORS）設定
- SSL/TLS証明書管理

### 6. モニタリングとロギング

- CloudWatch Logs
  - Lambda関数のログ
  - APIアクセスログ
  - アプリケーションログ
- CloudWatch Metrics
  - APIレイテンシー
  - エラーレート
  - リソース使用率
- X-Ray トレース
  - 分散トレーシング
  - パフォーマンス分析
- アラーム設定
  - エラー率の監視
  - レイテンシーの監視
  - コスト超過の監視

### 7. 設定管理

#### 7.1 設定ファイルの構成

プロジェクトの設定は以下の階層構造で管理します：

```text
saketrail/
├── config/
│   ├── common/           # 環境共通の設定
│   │   ├── dev.yml
│   │   ├── staging.yml
│   │   └── prod.yml
│   └── secrets/         # 機密情報（Git管理外）
├── frontend/
│   └── config/         # フロントエンド固有の設定
├── lambda/
│   └── config/         # バックエンド固有の設定
└── infra/
    └── config/         # インフラ固有の設定
        ├── dev/
        │   ├── frontend.yml
        │   └── backend.yml
        ├── staging/
        └── prod/
```

#### 7.2 設定ファイルの種類と役割

1. **共通設定（`config/common/*.yml`）**
   ```yaml
   # 開発環境共通設定（dev.yml）
   environment: dev
   domain: dev.saketrail.com
   aws:
     region: ap-northeast-1
     account_id: "${AWS_ACCOUNT_ID}"  # 環境変数から取得
   
   # 共通タグ
   tags:
     Environment: dev
     Project: saketrail
     ManagedBy: cdk
   ```
   - 環境固有の基本設定
   - AWSアカウント情報
   - ドメイン設定
   - 共通タグ

2. **インフラ設定（`infra/config/*/*.yml`）**
   ```yaml
   # フロントエンドインフラ設定（frontend.yml）
   s3:
     frontend_bucket:
       name: dev-saketrail-frontend
       error_document: index.html
       index_document: index.html
   
   cloudfront:
     price_class: PRICE_CLASS_200
     minimum_protocol_version: TLSv1.2_2021
   ```
   - AWSリソース固有の設定
   - インフラストラクチャのパラメータ
   - リソース命名規則

3. **アプリケーション設定（`frontend/config/*.yml`, `lambda/config/*.yml`）**
   - アプリケーション固有のパラメータ
   - 機能フラグ
   - UI設定
   - APIエンドポイント設定

4. **機密情報（`config/secrets/*.yml`）**
   - APIキー
   - シークレットキー
   - 認証情報
   - ※ Git管理外で、AWS Systems Manager Parameter Storeで管理

#### 7.3 設定の優先順位

設定値の解決は以下の優先順位で行われます：

1. 環境変数（最優先）
2. シークレット設定（`config/secrets/*.yml`）
3. アプリケーション設定（`frontend/config/*.yml`, `lambda/config/*.yml`）
4. インフラ設定（`infra/config/*/*.yml`）
5. 共通設定（`config/common/*.yml`）
6. コード内のデフォルト値（最低優先）

#### 7.4 設定値の参照方法

CDKスタック内での設定値の参照例：

```python
def _load_config(self, env_name: str) -> Dict:
    """
    共通設定とインフラ設定を読み込んで結合します
    """
    # 共通設定の読み込み
    common_config_path = os.path.join('config', 'common', f'{env_name}.yml')
    with open(common_config_path, 'r') as f:
        common_config = yaml.safe_load(f)

    # インフラ設定の読み込み
    infra_config_path = os.path.join('infra', 'config', env_name, 'frontend.yml')
    with open(infra_config_path, 'r') as f:
        infra_config = yaml.safe_load(f)

    return {
        'common': common_config,
        'infra': infra_config
    }
```

#### 7.5 設定管理のベストプラクティス

1. **環境分離**
   - 環境ごとに明確に分離された設定ファイル
   - 環境固有の値は共通設定で一元管理

2. **セキュリティ**
   - 機密情報は必ずParameter Storeで管理
   - 環境変数による上書きを許可

3. **命名規則**
   - 環境名をプレフィックスとして使用
   - リソース種別を含む明確な名前付け
   - キャメルケースまたはスネークケースの一貫した使用

4. **バージョン管理**
   - 設定変更の履歴を追跡可能に
   - レビュープロセスの適用
   - 変更の影響範囲を文書化

### 8. デプロイメントプロセス

1. 環境変数の設定
2. CDKブートストラップ（初回のみ）
3. スタックの合成（`cdk synth`）
4. スタックのデプロイ（`cdk deploy`）

### 9. ロールバック手順

1. 前バージョンの特定
2. `cdk deploy`による特定バージョンへのロールバック
3. 必要に応じたデータの復元

### CloudFront・ACM・Route53の管理方針

- **CloudFront**  
  - CDKで管理し、S3バケットの静的サイトを配信
  - カスタムドメイン・SSL/TLS証明書を利用

- **ACM（AWS Certificate Manager）**  
  - CloudFrontで利用する証明書（us-east-1リージョン）は「手動で作成」し、ARNを設定ファイルで管理
  - 証明書のDNS検証用CNAMEレコードは、Route53管理アカウントで手動追加

- **Route53**  
  - DNS管理は別AWSアカウントで実施
  - Aレコード（ALIAS）やCNAMEレコードの追加は手動で行う

- **CDKで管理する範囲**  
  - S3バケット、CloudFrontディストリビューションはCDKで管理
  - 証明書ARNやドメイン名は `config/dev/frontend.yml` などの設定ファイルで管理し、CDKで参照

### 設定ファイル例

```yaml
# config/dev/frontend.yml
domain: dev.saketrail.vdnih.link
certificate_arn: arn:aws:acm:us-east-1:xxxxxxxxxxxx:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
s3:
  frontend_bucket:
    name: dev-saketrail-frontend
cloudfront:
  price_class: PRICE_CLASS_200
```

### 運用フロー例

1. us-east-1でACM証明書を手動作成し、DNS検証用CNAMEをRoute53管理アカウントで追加
2. 証明書ARNを `config/dev/frontend.yml` に記載
3. CDKでS3/CloudFrontをデプロイ
4. CloudFrontのドメイン名をRoute53のAレコード(ALIAS)に手動で登録 