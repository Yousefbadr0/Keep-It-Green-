import 'package:flutter/material.dart';
import '../cairo.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';

class _Activity {
  final String title, subtitle, badge, iso, kind; // kind: item | redeem
  final num pts;
  final Color badgeColor, avatarBg;
  _Activity(this.title, this.subtitle, this.badge, this.iso, this.kind, this.pts, this.badgeColor, this.avatarBg);
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
        '+${t['CoinsEarned']}', t['CreatedAt'].toString(), plastic ? 'plastic' : 'aluminum',
        (t['CoinsEarned'] as num? ?? 0), Kig.spring, Kig.mint));
    }
    for (final d in reds) {
      list.add(_Activity(
        'Redeemed · ${d['PromoCode']}',
        cairoDateTime(d['RedemptionDate'].toString()),
        '−${d['CoinsDeducted']}', d['RedemptionDate'].toString(), 'redeem',
        (d['CoinsDeducted'] as num? ?? 0), Kig.muted, const Color(0xFFFFF1CC)));
    }
    list.sort((a, b) => b.iso.compareTo(a.iso));
    return list;
  }

  String _filter = 'All';       // All / Plastic / Aluminum / Redeemed
  String _sort = 'Newest';      // Newest / Oldest / Most points

  List<_Activity> _apply(List<_Activity> src) {
    final list = src.where((a) =>
        _filter == 'All' ||
        (_filter == 'Plastic' && a.kind == 'plastic') ||
        (_filter == 'Aluminum' && a.kind == 'aluminum') ||
        (_filter == 'Redeemed' && a.kind == 'redeem')).toList();
    if (_sort == 'Oldest') {
      list.sort((a, b) => a.iso.compareTo(b.iso));
    } else if (_sort == 'Most points') {
      list.sort((a, b) => b.pts.compareTo(a.pts));
    } else {
      list.sort((a, b) => b.iso.compareTo(a.iso));
    }
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
          final shown = _apply(all);
          // TODAY/EARLIER grouping reads naturally only in date order; for the
          // points sort we show one flat list instead.
          final grouped = _sort != 'Most points';
          final today = grouped ? shown.where((a) => isCairoToday(a.iso)).toList() : const <_Activity>[];
          final earlier = grouped ? shown.where((a) => !isCairoToday(a.iso)).toList() : const <_Activity>[];
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
            children: [
              Text('Activity', style: display(24)),
              if (all.isEmpty)
                const Padding(padding: EdgeInsets.all(30), child: Center(child: Text('No activity yet.', style: TextStyle(color: Kig.muted)))),
              if (all.isNotEmpty) ...[
                const SizedBox(height: 10),
                FilterSortBar(
                  filters: const ['All', 'Plastic', 'Aluminum', 'Redeemed'],
                  filter: _filter,
                  onFilter: (f) => setState(() => _filter = f),
                  sorts: const ['Newest', 'Oldest', 'Most points'],
                  sort: _sort,
                  onSort: (s) => setState(() => _sort = s),
                ),
              ],
              if (all.isNotEmpty && shown.isEmpty)
                const Padding(padding: EdgeInsets.all(24), child: Center(child: Text('Nothing matches this filter.', style: TextStyle(color: Kig.muted)))),
              if (!grouped) ...[
                const SizedBox(height: 12),
                ...shown.map(_row),
              ],
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
