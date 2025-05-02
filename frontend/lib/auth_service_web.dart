import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:oauth2_client/oauth2_client.dart';
import 'package:oauth2_client/oauth2_helper.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;

abstract class AuthService {
  Future<bool> signIn();
  Future<void> signOut();
  Future<bool> handleCallback(String code); // Web用
  Future<String?> getAccessToken();
  Future<bool> isSignedIn();

  static Future<AuthService> create() async => await WebAuthService.create();
}

class WebAuthService implements AuthService {
  late final String clientId;
  late final String redirectUrl;
  late final String authorizationEndpoint;
  late final String tokenEndpoint;
  late final OAuth2Helper _oauth2Helper;
  late final OAuth2Client _oauth2Client;

  static const List<String> scopes = ['openid', 'profile', 'email'];

  WebAuthService._();

  static Future<WebAuthService> create() async {
    final configString = await rootBundle.loadString(
      'assets/config/config.json',
    );
    final config = json.decode(configString);
    final domain = config['user_pool_domain'];
    final clientId = config['user_pool_client_id'];
    final redirectUrl = config['user_pool_redirect_uri'];
    final authorizationEndpoint = 'https://$domain/oauth2/authorize';
    final tokenEndpoint = 'https://$domain/oauth2/token';

    final client = OAuth2Client(
      authorizeUrl: authorizationEndpoint,
      tokenUrl: tokenEndpoint,
      redirectUri: redirectUrl,
      customUriScheme: 'http',
    );

    final helper = OAuth2Helper(
      client,
      clientId: clientId,
      scopes: scopes,
      // Cognitoの設定に合わせてパラメータを追加
      authCodeParams: {'response_type': 'code', 'client_id': clientId},
    );

    final service = WebAuthService._();
    service.clientId = clientId;
    service.redirectUrl = redirectUrl;
    service.authorizationEndpoint = authorizationEndpoint;
    service.tokenEndpoint = tokenEndpoint;
    service._oauth2Helper = helper;
    service._oauth2Client = client;
    return service;
  }

  @override
  Future<bool> signIn() async {
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

  @override
  Future<bool> handleCallback(String code) async {
    try {
      // OAuth2Clientのtokenメソッドを使用してトークンを取得
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

  @override
  Future<void> signOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('id_token');
    // ブラウザのセッションもクリア
    html.window.localStorage.clear();
    html.window.sessionStorage.clear();
  }

  @override
  Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  @override
  Future<bool> isSignedIn() async {
    final token = await getAccessToken();
    return token != null;
  }
}
