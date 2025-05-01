import 'package:flutter/material.dart';
import 'package:amplify_flutter/amplify_flutter.dart';
import 'package:amplify_auth_cognito/amplify_auth_cognito.dart';
import 'package:amplify_authenticator/amplify_authenticator.dart';
import 'dart:io' show Platform;
import 'dart:async';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'auth_service.dart';
import 'home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final amplify = Amplify;
  final auth = AmplifyAuthCognito();
  if (!amplify.isConfigured) {
    // 環境によって設定ファイルを切り替え
    final configAsset =
        kReleaseMode
            ? 'lib/amplifyconfiguration_prod.json'
            : 'lib/amplifyconfiguration_dev.json';
    final configString = await rootBundle.loadString(configAsset);
    await amplify.addPlugin(auth);
    await amplify.configure(configString);
  }
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final AuthService _authService = AuthService();
  bool _isSignedIn = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final signedIn = await _authService.isSignedIn();
    setState(() {
      _isSignedIn = signedIn;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }
    return MaterialApp(
      home:
          _isSignedIn
              ? const HomeScreen()
              : LoginScreen(
                onLogin: () async {
                  final result = await _authService.signInWithCognito();
                  if (result) {
                    setState(() {
                      _isSignedIn = true;
                    });
                  }
                },
              ),
    );
  }
}

class LoginScreen extends StatelessWidget {
  final Future<void> Function() onLogin;
  const LoginScreen({Key? key, required this.onLogin}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ログイン')),
      body: Center(
        child: ElevatedButton(
          onPressed: onLogin,
          child: const Text('Cognitoでログイン'),
        ),
      ),
    );
  }
}
