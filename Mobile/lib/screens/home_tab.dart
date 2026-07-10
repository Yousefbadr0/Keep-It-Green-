import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import 'scan_screen.dart';

class HomeTab extends StatefulWidget {
  const HomeTab({super.key});
  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  late Future<(num, List<dynamic>)> _data;

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<(num, List<dynamic>)> _load() async {
    final r = await Future.wait([ApiService.instance.coins(), ApiService.instance.machines()]);
    return (r[0] as num, r[1] as List<dynamic>);
  }

  Future<void> _refresh() async {
    setState(() => _data = _load());
    await _data;
  }

  // Tap a machine: scan its QR, or get a code to type on its keypad.
  void _machineActions(Map<String, dynamic> m) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(padding: const EdgeInsets.fromLTRB(20, 18, 20, 8), child: Align(alignment: Alignment.centerLeft, child: Text(m['Name'] ?? '', style: display(18)))),
            ListTile(
              leading: const Icon(Icons.qr_code_scanner, color: Kig.forest),
              title: const Text('Scan the machine QR'),
              onTap: () { Navigator.pop(ctx); Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ScanScreen())); },
            ),
            ListTile(
              leading: const Icon(Icons.dialpad, color: Kig.forest),
              title: const Text('Get a code to type on the machine'),
              onTap: () { Navigator.pop(ctx); _getCode(m['Id'] as int); },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  Future<void> _getCode(int machineId) async {
    try {
      final code = await ApiService.instance.generateOtp(machineId);
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text('Your code', style: display(20)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Type this on the machine keypad:', textAlign: TextAlign.center),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 22),
                decoration: BoxDecoration(color: Kig.mint, borderRadius: BorderRadius.circular(14), border: Border.all(color: Kig.spring, width: 2)),
                child: SelectableText(code.split('').join(' '), style: display(30, color: Kig.forest)),
              ),
              const SizedBox(height: 10),
              const Text('Valid for 5 minutes.', style: TextStyle(fontSize: 12, color: Kig.muted)),
            ],
          ),
          actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Done'))],
        ),
      );
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final name = ApiService.instance.userName;
    return RefreshIndicator(
      onRefresh: _refresh,
      child: FutureBuilder<(num, List<dynamic>)>(
        future: _data,
        builder: (context, snap) {
          final coins = snap.hasData ? snap.data!.$1 : 0;
          final machines = snap.hasData ? snap.data!.$2 : const [];
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Welcome back', style: TextStyle(color: Kig.muted, fontSize: 13)),
                        Text('Hi, $name', style: display(22)),
                      ],
                    ),
                  ),
                  CircleAvatar(
                    radius: 21, backgroundColor: Kig.mint,
                    child: Text(name.isNotEmpty ? name[0].toUpperCase() : 'U', style: display(16, color: Kig.forest)),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              // points card
              Container(
                decoration: BoxDecoration(color: Kig.forest, borderRadius: BorderRadius.circular(24)),
                padding: const EdgeInsets.all(22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('YOUR POINTS', style: label(color: Kig.paper.withValues(alpha: 0.6))),
                    const SizedBox(height: 6),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.baseline,
                      textBaseline: TextBaseline.alphabetic,
                      children: [
                        snap.hasData
                            ? Text(fmtPts(coins), style: display(46, color: Kig.sun))
                            : Text('â€”', style: display(46, color: Kig.sun)),
                        const SizedBox(width: 6),
                        Text('pts', style: display(16, weight: FontWeight.w500, color: Kig.paper.withValues(alpha: 0.7))),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text('Recycle at a machine to earn more', style: TextStyle(color: Kig.paper.withValues(alpha: 0.7), fontSize: 13)),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              // scan a machine
              GestureDetector(
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ScanScreen())),
                child: Container(
                  decoration: BoxDecoration(color: Kig.spring, borderRadius: BorderRadius.circular(18)),
                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
                  child: Row(
                    children: [
                      const LeafToken(size: 38, bg: Kig.forest, leaf: Kig.spring),
                      const SizedBox(width: 12),
                      Expanded(child: Text('Scan a machine', style: display(16, color: Kig.forest))),
                      Text('â†’', style: display(18, color: Kig.forest)),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 22),
              Text('NEARBY MACHINES', style: label()),
              const SizedBox(height: 8),
              if (!snap.hasData) const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator())),
              ...machines.map((m) => Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      onTap: m['IsAvailable'] == true ? () => _machineActions(Map<String, dynamic>.from(m)) : null,
                      leading: Container(
                        width: 9, height: 9,
                        decoration: BoxDecoration(color: m['IsAvailable'] == true ? Kig.spring : Kig.muted, shape: BoxShape.circle),
                      ),
                      title: Text(m['Name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      subtitle: Text(
                        '${m['IsAvailable'] == true ? 'Online' : 'Offline'} Â· ${m['Location'] ?? ''}',
                        style: const TextStyle(color: Kig.muted, fontSize: 12),
                      ),
                      trailing: m['IsAvailable'] == true ? const Icon(Icons.chevron_right, color: Kig.muted) : null,
                    ),
                  )),
            ],
          );
        },
      ),
    );
  }
}
