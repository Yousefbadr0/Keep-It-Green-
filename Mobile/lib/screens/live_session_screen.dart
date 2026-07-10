import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';

class LiveSessionScreen extends StatefulWidget {
  final int machineId;
  const LiveSessionScreen({super.key, required this.machineId});
  @override
  State<LiveSessionScreen> createState() => _LiveSessionScreenState();
}

class _LiveSessionScreenState extends State<LiveSessionScreen> {
  Timer? _timer;
  bool _baselineSet = false;
  int _baselineCount = 0;
  num _total = 0;
  List<dynamic> _sessionItems = [];
  String _location = 'the machine';

  @override
  void initState() {
    super.initState();
    _resolveLocation();
    _poll();
    _timer = Timer.periodic(const Duration(seconds: 3), (_) => _poll());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _resolveLocation() async {
    try {
      final ms = await ApiService.instance.machines();
      final m = ms.firstWhere((e) => e['Id'] == widget.machineId, orElse: () => null);
      if (m != null && mounted) setState(() => _location = m['Location'] ?? 'the machine');
    } catch (_) {}
  }

  Future<void> _poll() async {
    try {
      final results = await Future.wait([
        ApiService.instance.coins(),
        ApiService.instance.myTransactions(),
        ApiService.instance.sessionActive(),
      ]);
      final coins = results[0] as num;
      final txns = results[1] as List<dynamic>;
      final active = results[2] as bool;
      if (!_baselineSet) {
        _baselineCount = txns.length;
        _baselineSet = true;
      }
      if (!mounted) return;
      if (!active) {                 // the machine ended the session -> auto-close, no Finish tap needed
        _onSessionEnded();
        return;
      }
      setState(() {
        _total = coins;
        _sessionItems = txns.length > _baselineCount ? txns.sublist(_baselineCount) : const [];
      });
    } catch (_) {/* keep last state */}
  }

  void _onSessionEnded() {
    _timer?.cancel();
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(const SnackBar(
          content: Text('Session ended'), behavior: SnackBarBehavior.floating));
    Navigator.of(context).popUntil((r) => r.isFirst);
  }

  @override
  Widget build(BuildContext context) {
    final hint = Kig.paper.withValues(alpha: 0.65);
    final last = _sessionItems.isNotEmpty ? _sessionItems.last : null;
    return Scaffold(
      backgroundColor: Kig.forest,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
              child: Row(children: [
                Container(width: 8, height: 8, decoration: const BoxDecoration(color: Kig.spring, shape: BoxShape.circle)),
                const SizedBox(width: 8),
                Text('Connected · $_location', style: TextStyle(color: hint, fontSize: 13)),
              ]),
            ),
            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 120, height: 120,
                      decoration: BoxDecoration(
                        color: Kig.spring.withValues(alpha: 0.14),
                        shape: BoxShape.circle,
                        border: Border.all(color: last != null ? Kig.spring : hint, width: 2),
                      ),
                      child: Center(child: Icon(Icons.check_rounded, size: 40, color: last != null ? Kig.spring : hint)),
                    ),
                    const SizedBox(height: 16),
                    if (last != null) ...[
                      Text(last['ItemType'] == 'Plastic' ? 'Plastic bottle' : 'Aluminum can', style: display(22, color: Kig.paper)),
                      const SizedBox(height: 6),
                      Text('accepted', style: TextStyle(color: hint)),
                      const SizedBox(height: 10),
                      PointsPill('+${last['CoinsEarned']} pts'),
                    ] else ...[
                      Text('Drop an item at the machine', style: display(20, color: Kig.paper)),
                      const SizedBox(height: 6),
                      Text('Plastic & aluminum earn points', style: TextStyle(color: hint)),
                    ],
                    const SizedBox(height: 18),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.alphabetic,
                      children: [
                        Text(fmtPts(_total), style: display(32, color: Kig.paper)),
                        const SizedBox(width: 5),
                        Text('pts total', style: TextStyle(color: hint, fontSize: 14)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(22, 0, 22, 22),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('THIS SESSION · ${_sessionItems.length} ITEMS', style: label(color: hint)),
                  const SizedBox(height: 8),
                  ..._sessionItems.reversed.take(3).map((t) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(t['ItemType'] == 'Plastic' ? 'Plastic bottle' : 'Aluminum can', style: TextStyle(color: Kig.paper.withValues(alpha: 0.85))),
                            Text('+${t['CoinsEarned']}', style: display(14, weight: FontWeight.w600, color: Kig.sun)),
                          ],
                        ),
                      )),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: () {
                        ApiService.instance.endSession(); // machine returns to idle
                        Navigator.of(context).popUntil((r) => r.isFirst);
                      },
                      child: const Text('Finish session'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
