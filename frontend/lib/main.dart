import 'package:image_picker/image_picker.dart';
import 'package:flutter/material.dart';
import 'dart:io';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Saketrail',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Saketrail')),
      body: ListView(
        children: [
          ListTile(
            title: const Text('これまで飲んだお酒記録の閲覧'),
            leading: const Icon(Icons.list),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const DrinkHistoryScreen(),
                ),
              );
            },
          ),
          ListTile(
            title: const Text('飲んだお酒登録（撮影）'),
            leading: const Icon(Icons.camera_alt),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const DrinkRegistrationScreen(),
                ),
              );
            },
          ),
          ListTile(
            title: const Text('お酒検索'),
            leading: const Icon(Icons.search),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const DrinkSearchScreen(),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class DrinkHistoryScreen extends StatelessWidget {
  const DrinkHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('飲んだお酒記録')),
      body: const Center(child: Text('これまで飲んだお酒のリストが表示されます。')),
    );
  }
}

class DrinkRegistrationScreen extends StatefulWidget {
  const DrinkRegistrationScreen({super.key});

  @override
  _DrinkRegistrationScreenState createState() =>
      _DrinkRegistrationScreenState();
}

class _DrinkRegistrationScreenState extends State<DrinkRegistrationScreen> {
  File? _image;

  Future<void> _pickImage() async {
    final ImagePicker _picker = ImagePicker();
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);

    if (image != null) {
      setState(() {
        _image = File(image.path);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('飲んだお酒登録')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _pickImage,
              child: const Text('お酒のラベルを撮影'),
            ),
            if (_image != null) Image.file(_image!),
          ],
        ),
      ),
    );
  }
}

class DrinkSearchScreen extends StatelessWidget {
  const DrinkSearchScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('お酒検索')),
      body: const Center(child: Text('お酒を検索できる画面です。')),
    );
  }
}
