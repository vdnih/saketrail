import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ArticleService {
  static final String _baseUrl =
      'https://${dotenv.env['MICROCMS_SERVICE_NAME']}.microcms.io/api/v1';
  static final String _apiKey = dotenv.env['MICROCMS_API_KEY']!;

  static Future<List<dynamic>> fetchArticles() async {
    final response = await http.get(
      Uri.parse('$_baseUrl/blogs'),
      headers: {
        'X-API-KEY': _apiKey,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['contents'];
    } else {
      throw Exception('Failed to load articles');
    }
  }
}
