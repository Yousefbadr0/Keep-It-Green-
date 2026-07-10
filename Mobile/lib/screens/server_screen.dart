import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';

/// Lets the user point the app at the PC's current IP without rebuilding.
/// Reachable before login (from Welcome / Login) so you can connect first.
class ServerScreen extends StatefulWidget {
  const ServerScreen({super.key});
  @override
  State<ServerScreen> createState() => _ServerScreenState();
}

class _ServerScreenState extends State<ServerScreen> {
  late final TextEditingController _c;
  String? _status;
  bool _ok = false;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _c = TextEditingController(text: ApiService.instance.baseUrl);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  Future<void> _saveAndTest() async {
    setState(() {
      _busy = true;
      _status = null;
    });
    await ApiService.instance.setServer(_c.text);
    _c.text = ApiService.instance.baseUrl; // show the normalized value
    final ok = await ApiService.instance.ping();
    if (!mounted) return;
    setState(() {
      _busy = false;
      _ok = ok;
      _status = ok
          ? 'Connected to the server. You can log in now.'
          : "Couldn't reach the server. Check: same Wi-Fi, the IP is correct, "
              'and "Run Backend (for phone).bat" is running on the PC.';
    });
  }

  @override
  Widget build(BuildContext context) {
    final hint = Kig.paper.withValues(alpha: 0.7);
    return Scaffold(
      backgroundColor: Kig.forest,
      appBar: AppBar(
        backgroundColor: Kig.forest,
        foregroundColor: Kig.paper,
        elevation: 0,
        title: const Text('Server settings'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(28, 8, 28, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Center(child: LeafToken(size: 56)),
              const SizedBox(height: 18),
              Text('Connect to your PC', style: display(24, color: Kig.paper)),
              const SizedBox(height: 8),
              Text(
                'On the PC run "ipconfig" and use the IPv4 Address. '
                'Your phone and PC must be on the same Wi-Fi.',
                style: TextStyle(color: hint, height: 1.5),
              ),
              const SizedBox(height: 22),
              TextField(
                controller: _c,
                keyboardType: TextInputType.url,
                autocorrect: false,
                decoration: const InputDecoration(
                  labelText: 'Server address',
                  hintText: '192.168.1.27',
                ),
              ),
              const SizedBox(height: 8),
              Text('Just the IP is enough — ":5217" is added for you.',
                  style: TextStyle(color: hint, fontSize: 12.5)),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: _busy ? null : _saveAndTest,
                child: _busy
                    ? const SizedBox(
                        height: 20, width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Kig.forest))
                    : const Text('Save & test connection'),
              ),
              if (_status != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(_ok ? Icons.check_circle : Icons.error_outline,
                          color: _ok ? Kig.spring : Kig.sun, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(_status!,
                            style: TextStyle(
                                color: _ok ? Kig.spring : Kig.sun,
                                fontWeight: FontWeight.w600, height: 1.4)),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 16),
              Center(
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Done', style: display(14, weight: FontWeight.w600, color: Kig.spring)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
