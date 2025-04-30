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
  - クロスプラットフォーム対応（iOS/Android）
  - Material Design
  - カメラ統合とAI画像認識

### バックエンド
- AWS サーバーレス構成
  - Amazon API Gateway
  - AWS Lambda (Python)
  - Amazon DynamoDB
  - Amazon S3（画像ストレージ）
- AI/ML
  - OpenAI API (GPT-4 Vision)
  - 画像認識と商品情報の抽出
  - パーソナライズド推薦エンジン

### インフラストラクチャ
- AWS CDK (Python)
  - Infrastructure as Code
  - 環境分離（開発/ステージング/本番）
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
flutter run
```

## トラブルシューティング

よくある問題と解決方法については[トラブルシューティングガイド](./docs/troubleshooting.md)を参照してください。

## プロジェクト構造

```text
saketrail/
├── frontend/          # Flutterモバイルアプリケーション
│   ├── lib/          # Dartソースコード
│   ├── assets/       # 画像等の静的ファイル
│   └── test/         # テストコード
├── infra/            # AWS CDKによるインフラ定義
│   ├── pyproject.toml    # Poetry依存関係定義（CDK用）
│   ├── poetry.lock      # Poetry依存関係ロックファイル
│   ├── lib/          # CDKスタック定義
│   │   ├── storage/  # ストレージ関連（DynamoDB, S3）
│   │   ├── auth/     # 認証関連（Cognito）
│   │   ├── api/      # API関連（API Gateway, Lambda）
│   │   └── ai/       # AI関連（OpenAI統合）
│   ├── bin/          # CDKアプリケーションエントリーポイント
│   └── tests/        # CDKのテストコード
├── lambda/           # Lambda関数のソースコード
│   ├── pyproject.toml    # Poetry依存関係定義（Lambda用）
│   ├── poetry.lock      # Poetry依存関係ロックファイル
│   ├── src/         # Lambda関数の実装
│   │   ├── auth/    # 認証関連の関数
│   │   ├── sake/    # 日本酒関連の関数
│   │   └── ai/      # AI関連の関数
│   └── tests/       # Lambdaのテストコード
├── docs/             # プロジェクトドキュメント
│   ├── architecture/ # アーキテクチャ設計書
│   ├── api/         # API仕様書
│   └── guides/      # 各種ガイドライン
└── README.md         # プロジェクト概要
```

## ドキュメント

- [アーキテクチャ設計](./docs/architecture/README.md)
- [API仕様書](./docs/api/README.md)
- [開発ガイドライン](./docs/guides/development.md)
- [デプロイガイド](./docs/guides/deployment.md)
- [トラブルシューティング](./docs/guides/troubleshooting.md)

## ライセンス

MIT License
