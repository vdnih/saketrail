import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  final Future<void> Function() onLogin;
  const LoginScreen({super.key, required this.onLogin});

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
