import 'package:flutter/material.dart';
import '../cairo.dart';
import '../services/api_service.dart';
import '../theme.dart';

class _Activity {
  final String title, subtitle, badge, iso, kind; // kind: item | redeem
  final Color badgeColor, avatarBg;
  _Activity(this.title, this.subtitle, this.badge, this.iso, this.kind, this.badgeColor, this.avatarBg);
}

class HistoryTab extends StatefulWidget {
  const HistoryTab({super.key});
  @override
  State<HistoryTab> createState() => _HistoryTabState();
}

class _HistoryTabState extends State<HistoryTab> {
  late Future<List<_Activity>> _data;

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<List<_Activity>> _load() async {
    final r = await Future.wait([ApiService.instance.myTransactions(), ApiService.instance.myRedemptions()]);
    final txns = r[0];
    final reds = r[1];
    final list = <_Activity>[];
    for (final t in txns) {
      final plastic = t['ItemType'] == 'Plastic';
      list.add(_Activity(
        plastic ? 'Plastic bottle' : 'Aluminum can',
        cairoDateTime(t['CreatedAt'].toString()),
        '+${t['CoinsEarned']}', t['CreatedAt'].toString(), 'item', Kig.spring, Kig.mint));
    }
    for (final d in reds) {
      list.add(_Activity(
        'Redeemed · ${d['PromoCode']}',
        cairoDateTime(d['RedemptionDate'].toString()),
        '−${d['CoinsDeducted']}', d['RedemptionDate'].toString(), 'redeem', Kig.muted, const Color(0xFFFFF1CC)));
    }
    list.sort((a, b) => b.iso.compareTo(a.iso));
    return list;
  }

  Future<void> _refresh() async {
    setState(() => _data = _load());
    await _data;
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _refresh,
      child: FutureBuilder<List<_Activity>>(
        future: _data,
        builder: (context, snap) {
          if (!snap.hasData) {
            return const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator()));
          }
          final all = snap.data!;
          final today = all.where((a) => isCairoToday(a.iso)).toList();
          final earlier = all.where((a) => !isCairoToday(a.iso)).toList();
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
            children: [
              Text('Activity', style: display(24)),
              if (all.isEmpty)
                const Padding(padding: EdgeInsets.all(30), child: Center(child: Text('No activity yet.', style: TextStyle(color: Kig.muted)))),
              if (today.isNotEmpty) ...[
                const SizedBox(height: 14),
                Text('TODAY', style: label()),
                const SizedBox(height: 8),
                ...today.map(_row),
              ],
              if (earlier.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text('EARLIER', style: label()),
                const SizedBox(height: 8),
                ...earlier.map(_row),
              ],
            ],
          );
        },
      ),
    );
  }

  Widget _row(_Activity a) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          radius: 18, backgroundColor: a.avatarBg,
          child: Text(a.kind == 'redeem' ? '★' : (a.title.startsWith('Plastic') ? 'P' : 'A'),
              style: display(14, color: Kig.forest)),
        ),
        title: Text(a.title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
        subtitle: Text(a.subtitle, style: const TextStyle(color: Kig.muted, fontSize: 12)),
        trailing: Text(a.badge, style: display(15, weight: FontWeight.w700, color: a.badgeColor)),
      ),
    );
  }
}
