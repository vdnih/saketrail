# SakeTrail

お酒をもっと楽しむためのアプリ

## 概要

SakeTrailは、お酒との素敵な出会いと思い出を記録するためのプラットフォームです。

### 主な機能

- **AIラベル認識**: ボトルのラベルを撮影するだけで、AIが自動的にお酒を判別し、データを登録
- **パーソナライズド推薦**: あなたの好みを学習し、好みに合わせたお酒を推薦
- **思い出の記録**: 飲んだお酒の記録を簡単に検索・閲覧可能

## 技術スタック

### フロントエンド
- Flutter (Dart)
  - 現状はWeb対応（将来的にiOS/Android対応予定）
  - Material Design
  - OAuth2.0/Cognito認証フロー（oauth2_client利用）
  - Web専用実装（flutter_web_auth_2利用）

### バックエンド
- AWS サーバーレス構成
  - Amazon API Gateway
  - AWS Lambda (Python)
  - Amazon DynamoDB
  - Amazon S3（画像ストレージ）
  - Amazon Cognito（認証）
- AI/ML
  - OpenAI API (GPT-4 Vision)
  - 画像認識と商品情報の抽出
  - パーソナライズド推薦エンジン

### インフラストラクチャ
- AWS CDK (Python)
  - Infrastructure as Code
  - 環境分離（開発/本番）
  - CI/CD パイプライン

## 必要要件

### 開発環境
- Python 3.10以上
- Poetry 1.7以上（Python パッケージ管理）
- Flutter 3.16.0以上
- AWS CLI v2
- Visual Studio Code (推奨)

### クラウド環境
- AWSアカウント
- OpenAI APIアカウント

## セットアップ手順

### 1. 開発環境の準備

#### Python/Poetry環境のセットアップ
```bash
# Pythonのインストール確認
python --version  # Python 3.10以上であることを確認

# Poetryのインストール
curl -sSL https://install.python-poetry.org | python3 -

# Poetryのバージョン確認
poetry --version

# Poetry設定（仮想環境をプロジェクト配下に作成）
poetry config virtualenvs.in-project true
```

#### Flutter環境のセットアップ
1. [Flutter公式サイト](https://flutter.dev/docs/get-started/install)から適切なバージョンをダウンロード
2. 環境変数のPATHにFlutterを追加
3. 依存関係の確認
```bash
flutter doctor
```

#### AWS環境のセットアップ
1. [AWS CLI のインストール](https://aws.amazon.com/cli/)
2. 認証情報の設定
```bash
aws configure
```

### 2. プロジェクトのセットアップ

#### リポジトリのクローン
```bash
git clone [repository-url]
cd saketrail
```

#### バックエンド環境の準備
```bash
cd backend
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集し、必要な環境変数を設定
# - AWS_PROFILE
# - OPENAI_API_KEY
# - その他必要な環境変数
```

#### フロントエンド環境の準備
```bash
cd frontend
flutter pub get

# 環境変数の設定
cp .env.example .env
# .envファイルを編集し、必要な環境変数を設定
# - API_ENDPOINT
# - その他必要な環境変数
```

### 3. インフラのデプロイ

#### CDKのブートストラップ（初回のみ）
```bash
cd infra
poetry install
poetry run cdk --version  # CDKのバージョン確認
```

#### 開発環境へのデプロイ
```bash
poetry run cdk deploy --all
```

### 4. アプリケーションの起動

#### バックエンドの起動（ローカル開発時）
```bash
cd backend
uvicorn main:app --reload
```

#### フロントエンドの起動
```bash
cd frontend
flutter run -d chrome --web-port=8080
```

## トラブルシューティング

よくある問題と解決方法については[トラブルシューティングガイド](./docs/troubleshooting.md)を参照してください。

## プロジェクト構造

```text
saketrail/
├── frontend/          # Flutterウェブアプリケーション
│   ├── lib/          # Dartソースコード
│   │   ├── main.dart           # アプリケーションエントリーポイント
│   │   ├── auth_service.dart   # 認証サービス実装
│   │   └── home_screen.dart    # ホーム画面
│   ├── assets/       # 画像や設定ファイル等の静的ファイル
│   │   └── config/   # 環境ごとの設定ファイル（config.json）
│   ├── web/          # Webアプリ固有のファイル（index.html, callback.html等）
│   └── test/         # テストコード
├── infra/            # AWS CDKによるインフラ定義
│   ├── pyproject.toml    # Poetry依存関係定義（CDK用）
│   ├── poetry.lock      # Poetry依存関係ロックファイル
│   ├── app.py           # CDKアプリケーションエントリーポイント
│   └── saketrail_cdk/   # CDKスタック定義
│       └── stacks/      # 各種スタック（auth_stack.py, frontend_stack.py等）
├── config/           # プロジェクト全体の設定ファイル
│   ├── dev.yml       # 開発環境の設定
│   └── prod.yml      # 本番環境の設定
├── docs/             # プロジェクトドキュメント
│   ├── architecture/ # アーキテクチャ設計書
│   ├── guides/      # 各種ガイドライン
│   │   ├── authentication-flow.md  # 認証フロー実装ガイド
│   │   ├── coding-standards.md     # コーディング規約
│   │   └── development-process.md  # 開発プロセスガイドライン
│   └── api-spec.md   # API仕様書
└── README.md         # プロジェクト概要
```

## ドキュメント

### 開発プロセス
- [開発プロセスガイドライン](./docs/guides/development-process.md) - 開発の進め方、ドキュメント管理、MVPアプローチについて
- [コーディング規約](./docs/guides/coding-standards.md) - コードの書き方、命名規則、レビュー基準
- [テストガイドライン](./docs/guides/testing.md) - テスト方針、カバレッジ要件、テストの書き方

### 設計ドキュメント
- [アーキテクチャ設計](./docs/architecture/README.md) - システム全体の設計と構成
- [API仕様書](./docs/api/README.md) - APIエンドポイントとデータモデルの定義
- [認証フロー実装ガイド](./docs/guides/authentication-flow.md) - OAuth2.0/Cognito認証の実装方法

### その他
- [デプロイガイド](./docs/guides/deployment.md) - デプロイ手順と環境設定
- [トラブルシューティング](./docs/guides/troubleshooting.md) - よくある問題と解決方法

## ライセンス

MIT License
