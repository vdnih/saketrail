import 'package:flutter/material.dart';
import 'dart:async';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'auth_service.dart';
import 'home_screen.dart';
import 'login_screen.dart';
import 'dart:html' as html;
import 'ai_label_screen.dart';

Future<AuthService> getAuthService() async {
  return await AuthService.create();
}

void main() {
  runApp(const AppRoot());
}

class AppRoot extends StatelessWidget {
  const AppRoot({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<AuthService>(
      future: getAuthService(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const MaterialApp(home: LoadingScreen());
        }
        return MyApp(authService: snapshot.data!);
      },
    );
  }
}

class MyApp extends StatefulWidget {
  final AuthService authService;
  const MyApp({super.key, required this.authService});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late final AuthService _authService;
  bool _isSignedIn = false;
  bool _loading = true;

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

  Future<void> _checkAuth() async {
    final signedIn = await _authService.isSignedIn();
    if (mounted) {
      setState(() {
        _isSignedIn = signedIn;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SakeTrail',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/',
      routes: {
        '/':
            (context) =>
                _loading
                    ? const LoadingScreen()
                    : _isSignedIn
                    ? HomeScreen(authService: _authService)
                    : LoginScreen(onLogin: _handleLogin),
        '/login': (context) => LoginScreen(onLogin: _handleLogin),
        '/home':
            (context) => AuthGuard(
              child: HomeScreen(authService: _authService),
              authService: _authService,
            ),
        '/callback': (context) => const CallbackHandlerScreen(),
        '/ai-label': (context) => AiLabelScreen(authService: _authService),
      },
    );
  }

  Future<void> _handleLogin() async {
    final result = await _authService.signIn();
    if (result && mounted) {
      setState(() {
        _isSignedIn = true;
      });
      Navigator.pushReplacementNamed(context, '/home');
    }
  }
}

class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}

class CallbackHandlerScreen extends StatelessWidget {
  const CallbackHandlerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: Text('認証処理中...')));
  }
}

class AuthGuard extends StatelessWidget {
  final Widget child;
  final AuthService authService;

  const AuthGuard({super.key, required this.child, required this.authService});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: authService.isSignedIn(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.data == true) {
          return child;
        } else {
          Future.microtask(
            () => Navigator.pushReplacementNamed(context, '/login'),
          );
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
      },
    );
  }
}
