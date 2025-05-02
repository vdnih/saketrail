import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'widgets/camera_capture_widget.dart';
import 'auth_service.dart';

class HomeScreen extends StatelessWidget {
  final AuthService authService;
  const HomeScreen({super.key, required this.authService});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SakeTrail'),
        backgroundColor: Colors.brown[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'ログアウト',
            onPressed: () async {
              await authService.signOut();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () {
              // プロフィール画面への遷移（未実装）
            },
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF5E9DA), Color(0xFFE0C097)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // const SizedBox(height: 24),
              // Text(
              //   'AIラベル認識用 写真撮影',
              //   style: Theme.of(context).textTheme.titleLarge,
              // ),
              // const SizedBox(height: 16),
              // CameraCaptureWidget(
              //   onImagePicked: (file) {
              //     // ここで画像ファイルをS3アップロード等に利用可能
              //     print('画像パス: \\${file.path}');
              //   },
              // ),
              const SizedBox(height: 32),
              const Text(
                'おすすめのお酒',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF6D4C41),
                ),
              ),
              const SizedBox(height: 12),
              _buildSakeCard(
                name: '獺祭 純米大吟醸',
                brewery: '旭酒造',
                description: 'フルーティーで華やかな香り。初心者にもおすすめ。',
                url: 'https://www.asahishuzo.ne.jp/',
              ),
              _buildSakeCard(
                name: '黒龍 大吟醸',
                brewery: '黒龍酒造',
                description: '上品な旨味とキレのある後味。',
                url: 'https://www.kokuryu.co.jp/',
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.brown[600],
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                icon: const Icon(Icons.camera_alt, color: Colors.white),
                label: const Text(
                  'AIラベル認識',
                  style: TextStyle(fontSize: 18, color: Colors.white),
                ),
                onPressed: () {
                  Navigator.pushNamed(context, '/ai-label');
                },
              ),
              const SizedBox(height: 32),
              ListTile(
                leading: const Icon(Icons.history, color: Color(0xFF6D4C41)),
                title: const Text('飲んだ日本酒の履歴を見る'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  // 履歴画面への遷移（未実装）
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSakeCard({
    required String name,
    required String brewery,
    required String description,
    required String url,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              name,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              brewery,
              style: const TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text(description, style: const TextStyle(fontSize: 14)),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                icon: const Icon(Icons.open_in_new, color: Color(0xFF6D4C41)),
                label: const Text(
                  '公式サイトを見る',
                  style: TextStyle(color: Color(0xFF6D4C41)),
                ),
                onPressed: () async {
                  final uri = Uri.parse(url);
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
