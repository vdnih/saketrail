import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class CameraCaptureWidget extends StatefulWidget {
  final void Function(XFile file)? onImagePicked;

  const CameraCaptureWidget({Key? key, this.onImagePicked}) : super(key: key);

  @override
  State<CameraCaptureWidget> createState() => _CameraCaptureWidgetState();
}

class _CameraCaptureWidgetState extends State<CameraCaptureWidget> {
  XFile? _imageFile;
  final ImagePicker _picker = ImagePicker();

  Future<void> _takePhoto() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 90,
    );
    if (photo != null) {
      setState(() {
        _imageFile = photo;
      });
      if (widget.onImagePicked != null) {
        widget.onImagePicked!(photo);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (_imageFile != null)
          // WebではXFileのpathはURLとして使える
          Image.network(_imageFile!.path, height: 200),
        ElevatedButton.icon(
          icon: Icon(Icons.camera_alt),
          label: Text('写真を撮影'),
          onPressed: _takePhoto,
        ),
      ],
    );
  }
}
