import 'package:flutter_appauth/flutter_appauth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uni_links/uni_links.dart';

class AuthService {
  static const String clientId = 'YOUR_COGNITO_APP_CLIENT_ID';
  static const String redirectUrl = 'saketrail://callback';
  static const String issuer =
      'https://YOUR_COGNITO_DOMAIN.auth.REGION.amazoncognito.com';
  static const List<String> scopes = ['openid', 'profile', 'email'];

  final FlutterAppAuth _appAuth = FlutterAppAuth();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  Future<bool> signInWithCognito() async {
    try {
      final AuthorizationTokenResponse? result = await _appAuth
          .authorizeAndExchangeCode(
            AuthorizationTokenRequest(
              clientId,
              redirectUrl,
              issuer: issuer,
              scopes: scopes,
            ),
          );
      if (result != null) {
        await _secureStorage.write(
          key: 'access_token',
          value: result.accessToken,
        );
        await _secureStorage.write(key: 'id_token', value: result.idToken);
        await _secureStorage.write(
          key: 'refresh_token',
          value: result.refreshToken,
        );
        return true;
      }
      return false;
    } catch (e) {
      print('Sign in error: $e');
      return false;
    }
  }

  Future<void> signOut() async {
    await _secureStorage.deleteAll();
  }

  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: 'access_token');
  }

  Future<bool> isSignedIn() async {
    final token = await getAccessToken();
    return token != null;
  }
}
