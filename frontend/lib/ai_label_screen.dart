import 'package:flutter/material.dart';
import 'widgets/camera_capture_widget.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'auth_service.dart';
import 'dart:convert';
import 'package:flutter/services.dart';

class AiLabelScreen extends StatefulWidget {
  final AuthService authService;
  const AiLabelScreen({Key? key, required this.authService}) : super(key: key);

  @override
  State<AiLabelScreen> createState() => _AiLabelScreenState();
}

class _AiLabelScreenState extends State<AiLabelScreen> {
  XFile? _imageFile;
  bool _uploading = false;
  String? _error;
  String? _result;
  String? _apiBaseUrl;

  @override
  void initState() {
    super.initState();
    _loadApiBaseUrl();
  }

  Future<void> _loadApiBaseUrl() async {
    final configString = await rootBundle.loadString(
      'assets/config/config.json',
    );
    final config = json.decode(configString);
    setState(() {
      _apiBaseUrl = config['api_base_url'] as String?;
    });
  }

  // 画像のMIMEタイプをXFileから判定（WebはmimeType、モバイルは拡張子）
  String _detectMimeType(XFile file) {
    if (kIsWeb && file.mimeType != null) {
      return file.mimeType!;
    }
    final ext = file.path.toLowerCase();
    if (ext.endsWith('.jpg') || ext.endsWith('.jpeg')) return 'image/jpeg';
    if (ext.endsWith('.png')) return 'image/png';
    if (ext.endsWith('.webp')) return 'image/webp';
    if (ext.endsWith('.gif')) return 'image/gif';
    return 'application/octet-stream';
  }

  Future<void> _onImagePicked(XFile file) async {
    final mimeType = _detectMimeType(file);
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.contains(mimeType)) {
      setState(() {
        _error = '対応していない画像形式です。jpg, png, webp, gifのみアップロード可能です。';
        _imageFile = null;
        _result = null;
      });
      return;
    }
    setState(() {
      _imageFile = file;
      _error = null;
      _result = null;
    });
  }

  Future<void> _handleAiLabelRecognition() async {
    if (_imageFile == null || _apiBaseUrl == null) return;
    setState(() {
      _uploading = true;
      _error = null;
      _result = null;
    });
    try {
      final dio = Dio(BaseOptions(baseUrl: _apiBaseUrl!));
      final mimeType = _detectMimeType(_imageFile!);
      // AuthServiceからアクセストークンを取得
      final accessToken = await widget.authService.getAccessToken();
      if (accessToken == null) {
        setState(() {
          _error = '認証が必要です。ログインしてください。';
          _uploading = false;
        });
        return;
      }
      final presignedRes = await dio.post(
        '/ai/recognize-label/presigned-url',
        data: {'content_type': mimeType},
        options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
      );
      final uploadUrl = presignedRes.data['upload_url'] as String;
      final jobId = presignedRes.data['job_id'] as String;

      final bytes = await _imageFile!.readAsBytes();
      await Dio().put(
        uploadUrl,
        data: bytes,
        options: Options(headers: {'Content-Type': mimeType}),
      );

      setState(() {
        _result = 'アップロード完了！ジョブID: $jobId';
      });
    } catch (e) {
      String errorMsg = 'アップロード失敗: $e';
      if (e is DioException && e.response != null) {
        final data = e.response?.data;
        if (data is Map && data['error'] != null) {
          errorMsg += '\n${data['error']}';
        } else if (data is String) {
          errorMsg += '\n$data';
        }
      }
      setState(() {
        _error = errorMsg;
      });
    } finally {
      setState(() {
        _uploading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AIラベル認識'),
        backgroundColor: Colors.brown[700],
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 24),
              Text(
                '写真を撮影してラベル認識',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),
              CameraCaptureWidget(onImagePicked: _onImagePicked),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                icon: const Icon(Icons.cloud_upload),
                label: const Text('AIラベル認識'),
                onPressed:
                    (_imageFile != null && !_uploading)
                        ? _handleAiLabelRecognition
                        : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.brown[600],
                  padding: const EdgeInsets.symmetric(
                    vertical: 16,
                    horizontal: 32,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              if (_uploading) ...[
                const SizedBox(height: 16),
                const CircularProgressIndicator(),
              ],
              if (_result != null) ...[
                const SizedBox(height: 16),
                Text(_result!, style: const TextStyle(color: Colors.green)),
              ],
              if (_error != null) ...[
                const SizedBox(height: 16),
                SelectableText(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                ),
              ],
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}
