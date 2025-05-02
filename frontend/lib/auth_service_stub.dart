abstract class AuthService {
  Future<bool> signIn();
  Future<void> signOut();
  Future<bool> handleCallback(String code); // Web用
  Future<String?> getAccessToken();
  Future<bool> isSignedIn();

  static Future<AuthService> create() async =>
      throw UnimplementedError('Web専用です');
}

class WebAuthService implements AuthService {
  static Future<WebAuthService> create() async =>
      throw UnimplementedError('Web専用です');
  @override
  Future<bool> signIn() async => throw UnimplementedError('Web専用です');
  @override
  Future<void> signOut() async => throw UnimplementedError('Web専用です');
  @override
  Future<bool> handleCallback(String code) async =>
      throw UnimplementedError('Web専用です');
  @override
  Future<String?> getAccessToken() async => throw UnimplementedError('Web専用です');
  @override
  Future<bool> isSignedIn() async => throw UnimplementedError('Web専用です');
}
