# コーディング規約

## 概要

本ドキュメントでは、SakeTrailプロジェクトにおけるコーディング規約を定義します。
フロントエンド（Flutter/Dart）とバックエンド（Python）それぞれの規約に従い、一貫性のある可読性の高いコードを維持します。

## 共通ガイドライン

### 1. 基本原則

- DRY (Don't Repeat Yourself) - コードの重複を避ける
- KISS (Keep It Simple, Stupid) - シンプルで理解しやすい実装を心がける
- YAGNI (You Aren't Gonna Need It) - 必要になるまで機能を追加しない

### 2. コードスタイル

- インデントは一貫して使用する
- 1行の長さは120文字以内に収める
- 適切な空行を入れてコードブロックを分ける
- コメントは必要な場合のみ追加し、コードの「なぜ」を説明する

### 3. 命名規則

- 意図が明確に伝わる名前を使用する
- 略語は一般的なもの以外は使用しない
- 一時的な変数名（i, j, k等）は最小限に抑える

## Flutter/Dartコーディング規約

### 1. ファイル構成

```dart
// ライブラリのインポート
import 'dart:async';
import 'dart:io';

// パッケージのインポート
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

// プロジェクト内のインポート
import 'package:saketrail/core/utils.dart';
```

### 2. 命名規則

- **クラス名**: UpperCamelCase
  ```dart
  class SakeDetailPage extends StatelessWidget { ... }
  ```

- **変数名、メソッド名**: lowerCamelCase
  ```dart
  final String sakeName;
  void updateSakeDetails() { ... }
  ```

- **定数**: lowerCamelCase
  ```dart
  const double defaultPadding = 16.0;
  ```

### 3. Widgetの構成

- **StatelessWidget/StatefulWidget**:
  ```dart
  class SakeCard extends StatelessWidget {
    const SakeCard({
      Key? key,
      required this.sake,
      this.onTap,
    }) : super(key: key);

    final Sake sake;
    final VoidCallback? onTap;

    @override
    Widget build(BuildContext context) {
      return Card(
        // Widget implementation
      );
    }
  }
  ```

- **メソッドの分割**:
  ```dart
  class SakeListPage extends StatelessWidget {
    Widget _buildSakeList() { ... }
    Widget _buildEmptyState() { ... }
    Widget _buildErrorState(String message) { ... }
  }
  ```

### 4. 非同期処理

```dart
Future<void> loadSakeDetails() async {
  try {
    final result = await sakeRepository.getSakeDetails(id);
    // Handle result
  } catch (e) {
    // Error handling
  }
}
```

## Pythonコーディング規約

### 1. コードスタイル

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)に準拠
- [black](https://github.com/psf/black)フォーマッターを使用

### 2. 命名規則

- **モジュール名**: スネークケース
  ```python
  from sake_service import get_sake_details
  ```

- **クラス名**: UpperCamelCase
  ```python
  class SakeRepository:
      pass
  ```

- **関数名、変数名**: スネークケース
  ```python
  def get_sake_by_id(sake_id: str) -> Dict[str, Any]:
      pass
  ```

- **定数**: 大文字のスネークケース
  ```python
  MAX_RETRY_COUNT = 3
  DEFAULT_TIMEOUT = 30
  ```

### 3. 型ヒント

```python
from typing import Dict, List, Optional

def get_sake_recommendations(
    user_id: str,
    limit: Optional[int] = 10
) -> List[Dict[str, Any]]:
    pass
```

### 4. クラス定義

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SakeReview:
    id: str
    sake_id: str
    user_id: str
    rating: int
    comment: str
    created_at: datetime
```

### 5. 例外処理

```python
class SakeNotFoundError(Exception):
    pass

def get_sake(sake_id: str) -> Dict[str, Any]:
    try:
        return sake_table.get_item(Key={"id": sake_id})
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise SakeNotFoundError(f"Sake with id {sake_id} not found")
        raise
```

## コードレビュー基準

### 1. 機能面

- 仕様書の要件を満たしているか
- エッジケースが適切に処理されているか
- パフォーマンスに問題はないか

### 2. 品質面

- テストは十分か
- エラー処理は適切か
- ログ出力は適切か

### 3. 保守性

- コードは理解しやすいか
- 適切にモジュール化されているか
- 将来の変更に対応しやすいか

### 4. セキュリティ

- 認証・認可は適切か
- 機密情報の扱いは適切か
- 入力値の検証は十分か

## ツール

### Flutter/Dart

- dart format - コードフォーマット
- dart analyze - 静的解析
- flutter_lints - リントルール

### Python

- black - コードフォーマット
- isort - importの整理
- flake8 - リント
- mypy - 型チェック

## CI/CDでの検証

上記のツールはすべてCI/CDパイプラインで実行され、以下の基準を満たす必要があります：

- すべてのテストが成功
- コードカバレッジが80%以上
- フォーマットチェックに違反がない
- リントエラーがない
- 型チェックエラーがない 