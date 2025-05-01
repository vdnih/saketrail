# Cognito認証フロー実装ガイド

## 概要

SakeTrailアプリケーションでは、AWS Cognitoを利用したOAuth2.0認証フローを実装しています。このドキュメントでは、現状のWeb対応実装における認証フローの実装方法と主要コンポーネントについて説明します。

> **重要**: 現在の実装はWeb対応のみとなっています。将来的にはモバイル（iOS/Android）対応を予定していますが、現時点ではWebブラウザでの利用を前提とした実装となっており、oauth2_clientパッケージを使用しています。モバイル対応時には実装方法が変更になる可能性があります。

## 技術スタック

- **フロントエンド**: Flutter Web
- **認証サービス**: AWS Cognito User Pool
- **主要パッケージ**: 
  - oauth2_client: ^3.2.2
  - flutter_web_auth_2: ^2.2.0
  - shared_preferences: ^2.2.2 (トークン保存用)
  - http: ^1.1.0 (トークン交換用)

## 認証フロー

### フロー図

```
┌─────────┐    ┌────────────────┐    ┌───────────────┐    ┌─────────────┐    ┌──────────────┐
│ ユーザー │───→│ ログインボタン │───→│ Cognito      │───→│ コールバック │───→│ トークン取得 │
└─────────┘    └────────────────┘    │ Hosted UI    │    └─────────────┘    └──────────────┘
                                      └───────────────┘                             │
                                                                                    ↓
                                      ┌───────────────┐                      ┌──────────────┐
                                      │ ホーム画面    │←─────────────────────│ 認証完了     │
                                      └───────────────┘                      └──────────────┘
```

### 詳細フロー

1. **ユーザーがログインボタンをクリック**
   - アプリケーション内の「Cognitoでログイン」ボタンをクリック
   - `AuthService.signInWithOAuth2()`メソッドが呼び出される

2. **Cognito Hosted UIへのリダイレクト**
   - OAuth2Helperによって認証URLが生成される
   - 別ウィンドウでCognito Hosted UIが開く
   - ユーザーがCognitoでログイン情報を入力

3. **認可コードの受け取り**
   - 認証成功後、Cognitoから設定したリダイレクトURI（`http://localhost:8080/callback.html`）へリダイレクト
   - URLのクエリパラメータに認可コード（`code`）が含まれる

4. **コールバック処理**
   - `callback.html`がリダイレクト先として読み込まれる
   - JavaScriptコードがURLから認可コードを抽出
   - `window.opener.postMessage()`で親ウィンドウに認可コードを送信

5. **トークン交換**
   - 親ウィンドウで`handleCallback()`メソッドが実行される
   - 認可コードを使用してCognitoのトークンエンドポイントにリクエスト
   - アクセストークン、リフレッシュトークン、IDトークンを取得

6. **トークンの保存と認証完了**
   - 取得したトークンをSharedPreferencesに保存
   - 認証状態を更新
   - ホーム画面へのリダイレクト

## 主要コンポーネント

### 1. AuthService クラス

認証に関する全ての機能を提供するサービスクラスです。

```dart
// frontend/lib/auth_service.dart

class AuthService {
  late final String clientId;
  late final String redirectUrl;
  late final String authorizationEndpoint;
  late final String tokenEndpoint;
  late final OAuth2Helper _oauth2Helper;
  late final OAuth2Client _oauth2Client;

  static const List<String> scopes = ['openid', 'profile', 'email'];

  // 設定ファイルから認証情報を読み込んでサービスを初期化
  static Future<AuthService> create() async {
    // 設定の読み込み
    final configString = await rootBundle.loadString('assets/config/config.json');
    final config = json.decode(configString);
    
    // 設定値の取得
    final domain = config['user_pool_domain'];
    final clientId = config['user_pool_client_id'];
    final redirectUrl = config['user_pool_redirect_uri'];
    final authorizationEndpoint = 'https://$domain/oauth2/authorize';
    final tokenEndpoint = 'https://$domain/oauth2/token';

    // OAuth2Clientの初期化
    final client = OAuth2Client(
      authorizeUrl: authorizationEndpoint,
      tokenUrl: tokenEndpoint,
      redirectUri: redirectUrl,
      customUriScheme: 'http',
    );

    // OAuth2Helperの初期化
    final helper = OAuth2Helper(
      client,
      clientId: clientId,
      scopes: scopes,
      authCodeParams: {'response_type': 'code', 'client_id': clientId},
    );

    // サービスの初期化
    final service = AuthService._();
    service.clientId = clientId;
    service.redirectUrl = redirectUrl;
    service.authorizationEndpoint = authorizationEndpoint;
    service.tokenEndpoint = tokenEndpoint;
    service._oauth2Helper = helper;
    service._oauth2Client = client;
    return service;
  }

  // ログイン処理
  Future<bool> signInWithOAuth2() async {
    try {
      final token = await _oauth2Helper.getToken();
      if (token != null && token.accessToken != null) {
        await _saveTokens(token);
        return true;
      }
      return false;
    } catch (e) {
      print('Sign in error: $e');
      return false;
    }
  }

  // コールバック処理
  Future<bool> handleCallback(String code) async {
    try {
      // トークンエンドポイントにリクエスト
      final tokenUrl = Uri.parse(tokenEndpoint);
      final response = await http.post(
        tokenUrl,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'grant_type': 'authorization_code',
          'client_id': clientId,
          'code': code,
          'redirect_uri': redirectUrl,
        },
      );

      if (response.statusCode == 200) {
        final tokenResponse = json.decode(response.body);
        final accessToken = tokenResponse['access_token'];
        final refreshToken = tokenResponse['refresh_token'];
        final idToken = tokenResponse['id_token'];

        if (accessToken != null) {
          // トークンの保存
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('access_token', accessToken);
          if (refreshToken != null) {
            await prefs.setString('refresh_token', refreshToken);
          }
          if (idToken != null) {
            await prefs.setString('id_token', idToken);
          }
          return true;
        }
      }
      return false;
    } catch (e) {
      print('Token exchange error: $e');
      return false;
    }
  }

  // トークンの保存
  Future<void> _saveTokens(token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token.accessToken!);
    if (token.refreshToken != null) {
      await prefs.setString('refresh_token', token.refreshToken!);
    }
    if (token.idToken != null) {
      await prefs.setString('id_token', token.idToken!);
    }
  }

  // ログアウト処理
  Future<void> signOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('id_token');
    // ブラウザのセッションもクリア
    html.window.localStorage.clear();
    html.window.sessionStorage.clear();
  }

  // アクセストークンの取得
  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  // 認証状態の確認
  Future<bool> isSignedIn() async {
    final token = await getAccessToken();
    return token != null;
  }
}
```

### 2. コールバックハンドラ (callback.html)

認証コードを受け取り、親ウィンドウに転送するHTML/JavaScriptファイルです。Webアプリ特有の実装となっています。

```html
<!-- frontend/web/callback.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>OAuth2 Callback</title>
    <script>
      window.onload = function() {
        try {
          // URLからクエリパラメータを取得
          const urlParams = new URLSearchParams(window.location.search);
          const code = urlParams.get('code');
          const state = urlParams.get('state');
          const error = urlParams.get('error');
          
          if (error) {
            // エラーの場合は親ウィンドウにエラーを通知
            window.opener.postMessage({
              type: 'oauth_error',
              error: error,
              error_description: urlParams.get('error_description')
            }, window.location.origin);
          } else if (code) {
            // 認可コードを親ウィンドウに通知
            window.opener.postMessage(window.location.href, window.location.origin);
          }
        } catch (e) {
          console.error('Callback処理エラー:', e);
        } finally {
          // 処理完了後にウィンドウを閉じる
          setTimeout(() => window.close(), 1000);
        }
      }
    </script>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        background-color: #f5f5f5;
      }
      .message {
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
    </style>
  </head>
  <body>
    <div class="message">
      <h2>認証処理中...</h2>
      <p>このウィンドウは自動的に閉じられます。</p>
    </div>
  </body>
</html>
```

### 3. コールバックリスナー

Flutter アプリ内でコールバックを処理するコード部分です。これもWeb特有の実装です。

```dart
// frontend/lib/main.dart (MyAppクラス内)

@override
void initState() {
  super.initState();
  _authService = widget.authService;
  _checkAuth();
  _setupCallbackListener();
}

void _setupCallbackListener() {
  html.window.onMessage.listen((event) async {
    if (event.data is String && event.data.startsWith('http')) {
      final uri = Uri.parse(event.data);
      final code = uri.queryParameters['code'];
      if (code != null) {
        final result = await _authService.handleCallback(code);
        if (result) {
          setState(() {
            _isSignedIn = true;
            _loading = false;
          });
          // コールバック成功後にホーム画面に遷移
          if (mounted) {
            Navigator.pushReplacementNamed(context, '/home');
          }
        }
      }
    }
  });
}
```

## 環境設定

### 設定ファイル

```json
// frontend/assets/config/config.json (開発環境用)
{
  "user_pool_domain": "saketrail-dev.auth.ap-northeast-1.amazoncognito.com",
  "user_pool_client_id": "77maktokl4oi8mlgq98dampe0h",
  "user_pool_redirect_uri": "http://localhost:8080/callback.html"
}

// frontend/assets/config/config.prod.json (本番環境用)
{
  "user_pool_domain": "saketrail.auth.ap-northeast-1.amazoncognito.com",
  "user_pool_client_id": "saketrail",
  "user_pool_redirect_uri": "https://saketrail.vdnih.link/callback.html"
}
```

### Cognito設定

AWS CDK でCognitoの設定を管理しています。主な設定は以下の通りです。

```python
# infra/saketrail_cdk/stacks/auth_stack.py
user_pool_client = user_pool.add_client(
    "UserPoolClient",
    auth_flows=cognito.AuthFlow(
        user_password=True,
        user_srp=True,
    ),
    generate_secret=False,
    o_auth=cognito.OAuthSettings(
        callback_urls=[
            user_pool_redirect_uri,  # config.ymlから読み込んだURL
        ],
        logout_urls=[
            f"https://{config['frontend']['domain']}/logout",
        ],
        flows=cognito.OAuthFlows(
            authorization_code_grant=True
        ),
        scopes=[
            cognito.OAuthScope.OPENID,
            cognito.OAuthScope.EMAIL,
            cognito.OAuthScope.PROFILE,
        ],
    ),
)
```

## セキュリティ上の注意点

1. **トークンの安全な保存**
   - アクセストークン、リフレッシュトークンは適切な方法で保存する
   - 将来的なモバイル対応時にはSecure Storageの利用を検討

2. **リダイレクトURIの検証**
   - Cognitoコンソールに登録したリダイレクトURIと実装が一致していることを確認

3. **HTTPS通信**
   - 本番環境では必ずHTTPS通信を使用する
   - ローカル開発時もHTTPSの利用を推奨

4. **トークンの有効期限**
   - アクセストークンの有効期限が切れた場合のリフレッシュ処理を実装

## 実装上の注意点

1. **ブラウザ互換性**
   - 異なるブラウザでの動作確認
   - ポップアップブロック対策の実装

2. **エラーハンドリング**
   - 認証エラーの適切な処理
   - ユーザーに理解しやすいエラーメッセージの表示

3. **リダイレクト後のURL処理**
   - ハッシュフラグメントやクエリパラメータの適切な処理
   - 状態管理のための`state`パラメータの活用

## 将来的な拡張計画

1. **モバイル対応（iOS/Android）**
   - ディープリンクを使用した認証フローの実装
   - プラットフォーム固有の認証処理の追加

2. **リフレッシュトークンの活用**
   - アクセストークンの自動更新機能の実装

3. **ソーシャルログイン**
   - Google、Apple、LINEなどのIdP連携

4. **多要素認証（MFA）**
   - SMS認証やTOTPの導入

5. **セッション管理の強化**
   - アイドルタイムアウトの実装
   - デバイス追跡機能の追加 