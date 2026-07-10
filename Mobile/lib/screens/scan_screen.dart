import 'package:flutter/material.dart';
import 'package:flutter_zxing/flutter_zxing.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/api_service.dart';
import '../theme.dart';
import 'live_session_screen.dart';

/// QR pairing screen.
///
/// Uses `flutter_zxing` (the ZXing C++ library via FFI) — deliberately NOT an
/// ML-Kit-based scanner. The earlier `mobile_scanner`/ML-Kit path crashed on
/// some devices with a native null-pointer inside Google's barcode module
/// ("Attempt to invoke virtual method 'l4.c l4.b.a(h4.c)' on a null object").
/// ZXing has no Google Play Services dependency, so that whole failure mode
/// disappears. Manual code entry remains available as a fallback.
class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  bool _handled = false;
  bool _pairing = false;
  bool? _granted; // null = asking, true = granted, false = denied

  @override
  void initState() {
    super.initState();
    _ensurePermission();
  }

  Future<void> _ensurePermission() async {
    var status = await Permission.camera.status;
    if (!status.isGranted) status = await Permission.camera.request();
    if (mounted) setState(() => _granted = status.isGranted);
  }

  Future<void> _grantFlow() async {
    final status = await Permission.camera.request();
    if (status.isPermanentlyDenied) {
      await openAppSettings();
    } else if (mounted) {
      setState(() => _granted = status.isGranted);
    }
  }

  String? _extractCode(String raw) {
    final m = RegExp(r'\d{6}').firstMatch(raw);
    return m?.group(0) ?? (raw.trim().isNotEmpty ? raw.trim() : null);
  }

  void _onScan(Code code) {
    if (_handled || !code.isValid) return;
    final raw = code.text;
    if (raw == null) return;
    final c = _extractCode(raw);
    if (c != null) {
      setState(() => _handled = true);
      _pair(c);
    }
  }

  Future<void> _pair(String code) async {
    setState(() => _pairing = true);
    try {
      final r = await ApiService.instance.pair(code);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(MaterialPageRoute(
          builder: (_) => LiveSessionScreen(machineId: r['MachineId'] as int? ?? 0)));
    } on ApiException catch (e) {
      if (!mounted) return;
      _snack(e.message, error: true);
      setState(() {
        _handled = false;
        _pairing = false;
      });
    }
  }

  void _snack(String msg, {bool error = false}) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(
        content: Text(msg),
        backgroundColor: error ? const Color(0xFFB4452F) : Kig.forest,
        behavior: SnackBarBehavior.floating,
      ));
  }

  Future<void> _enterManually() async {
    final ctrl = TextEditingController();
    final code = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Kig.paper,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
            left: 24, right: 24, top: 22, bottom: MediaQuery.of(ctx).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Enter the machine code', style: display(20)),
            const SizedBox(height: 14),
            TextField(
                controller: ctrl,
                keyboardType: TextInputType.number,
                textAlign: TextAlign.center,
                style: display(28, color: Kig.forest),
                maxLength: 6,
                decoration: const InputDecoration(counterText: '', hintText: '------')),
            const SizedBox(height: 8),
            FilledButton(
                onPressed: () => Navigator.pop(ctx, ctrl.text.trim()),
                child: const Text('Pair')),
          ],
        ),
      ),
    );
    if (code != null && code.isNotEmpty) {
      setState(() => _handled = true);
      _pair(code);
    }
  }

  @override
  Widget build(BuildContext context) {
    final showCam = _granted == true;
    return Scaffold(
      backgroundColor: Kig.charcoal,
      body: Stack(
        children: [
          if (showCam)
            Positioned.fill(
              child: ReaderWidget(
                onScan: _onScan,
                showGallery: false,
                showToggleCamera: false,
                scanDelay: const Duration(milliseconds: 400),
                loading: const ColoredBox(
                  color: Kig.charcoal,
                  child: Center(child: CircularProgressIndicator(color: Kig.spring)),
                ),
              ),
            ),
          if (_granted == null)
            const ColoredBox(
              color: Kig.forest,
              child: Center(child: CircularProgressIndicator(color: Kig.spring)),
            ),
          if (_granted == false)
            _CameraMessage(onManual: _enterManually, onRetry: _grantFlow),

          if (_pairing)
            const IgnorePointer(
              child: ColoredBox(
                color: Color(0x660C3B2A),
                child: Center(child: CircularProgressIndicator(color: Kig.spring)),
              ),
            ),

          // top bar
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
              child: Row(children: [
                IconButton(
                    icon: const Icon(Icons.arrow_back, color: Kig.paper),
                    onPressed: () => Navigator.pop(context)),
                Text('Scan machine', style: display(18, color: Kig.paper)),
              ]),
            ),
          ),

          // bottom: instructions + manual entry (always available)
          SafeArea(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding: const EdgeInsets.only(bottom: 36),
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  if (showCam)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                      decoration: BoxDecoration(
                          color: Kig.forest.withValues(alpha: 0.75),
                          borderRadius: BorderRadius.circular(999)),
                      child: const Text('Point at the QR on the machine',
                          style: TextStyle(color: Kig.paper, fontSize: 14)),
                    ),
                  const SizedBox(height: 12),
                  TextButton(
                      onPressed: _enterManually,
                      child: Text('Enter code manually',
                          style: display(14, weight: FontWeight.w600, color: Kig.spring))),
                ]),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Shown when camera permission is denied so the user always sees why and can
/// still pair by typing the code.
class _CameraMessage extends StatelessWidget {
  final VoidCallback onManual;
  final VoidCallback onRetry;
  const _CameraMessage({required this.onManual, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: Kig.forest,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.photo_camera_outlined, color: Kig.paper, size: 48),
              const SizedBox(height: 14),
              Text('Allow camera access',
                  textAlign: TextAlign.center, style: display(20, color: Kig.paper)),
              const SizedBox(height: 8),
              Text(
                'Keep It Green needs your camera to scan the machine QR. Tap Allow — or type the code instead.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Kig.paper.withValues(alpha: 0.72), height: 1.5),
              ),
              const SizedBox(height: 20),
              FilledButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.videocam),
                label: const Text('Allow camera'),
              ),
              const SizedBox(height: 10),
              TextButton(
                onPressed: onManual,
                child: Text('Enter code manually',
                    style: display(14, weight: FontWeight.w600, color: Kig.spring)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
