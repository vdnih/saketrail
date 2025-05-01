// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

// このテストはWeb専用コード（dart:html依存）のため、Dart VM上では実行できません。
// Webテスト環境が整うまで一時的に無効化します。

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:saketrail/home_screen.dart';
import 'package:saketrail/login_screen.dart';

void main() {
  // テスト無効化中

  testWidgets('HomeScreenの主要UI要素が表示される', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: HomeScreen()));
    expect(find.text('SakeTrail'), findsOneWidget);
    expect(find.text('おすすめの日本酒'), findsOneWidget);
    expect(find.text('獺祭 純米大吟醸'), findsOneWidget);
    expect(find.text('黒龍 大吟醸'), findsOneWidget);
    expect(find.text('AIラベル認識で日本酒を探す'), findsOneWidget);
    // ListView内の要素はスクロールして検出
    await tester.scrollUntilVisible(
      find.text('飲んだ日本酒の履歴を見る'),
      100.0,
      scrollable: find.byType(Scrollable),
    );
    expect(find.text('飲んだ日本酒の履歴を見る'), findsOneWidget);
  });

  testWidgets('LoginScreenのボタンとタイトルが表示される', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(home: LoginScreen(onLogin: () async {})),
    );
    expect(find.text('Cognitoでログイン'), findsOneWidget);
    expect(find.text('ログイン'), findsOneWidget);
  });
}

// void main() {
//   testWidgets('Counter increments smoke test', (WidgetTester tester) async {
//     // AuthServiceのダミーを生成
//     final authService = await WebAuthService.create();
//
//     // Build our app and trigger a frame.
//     await tester.pumpWidget(MyApp(authService: authService));
//
//     // Verify that our counter starts at 0.
//     expect(find.text('0'), findsOneWidget);
//     expect(find.text('1'), findsNothing);
//
//     // Tap the '+' icon and trigger a frame.
//     await tester.tap(find.byIcon(Icons.add));
//     await tester.pump();
//
//     // Verify that our counter has incremented.
//     expect(find.text('0'), findsNothing);
//     expect(find.text('1'), findsOneWidget);
//   });
// }
