import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import 'redeemed_screen.dart';

class RewardsTab extends StatefulWidget {
  const RewardsTab({super.key});
  @override
  State<RewardsTab> createState() => _RewardsTabState();
}

class _RewardsTabState extends State<RewardsTab> {
  late Future<(num, List<dynamic>)> _data;

  @override
  void initState() {
    super.initState();
    _data = _load();
  }

  Future<(num, List<dynamic>)> _load() async {
    final r = await Future.wait([ApiService.instance.coins(), ApiService.instance.promos()]);
    return (r[0] as num, r[1] as List<dynamic>);
  }

  Future<void> _refresh() async {
    setState(() => _data = _load());
    await _data;
  }

  Future<void> _redeem(Map<String, dynamic> promo, num balance) async {
    final cost = promo['RequiredCoins'] as num;
    if (balance < cost) {
      showSnack(context, 'Not enough points for this reward', error: true);
      return;
    }
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Redeem reward'),
        content: Text('Redeem ${promo['VendorName']} for ${fmtPts(cost)} points?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Redeem')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      final r = await ApiService.instance.redeem(promo['Id'] as int);
      if (!mounted) return;
      await Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => RedeemedScreen(
          code: r['PromoCode']?.toString() ?? '',
          vendor: promo['VendorName']?.toString() ?? '',
          remaining: (r['RemainingCoins'] as num?) ?? 0,
        ),
      ));
      _refresh();
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _refresh,
      child: FutureBuilder<(num, List<dynamic>)>(
        future: _data,
        builder: (context, snap) {
          final balance = snap.hasData ? snap.data!.$1 : 0;
          final promos = snap.hasData ? snap.data!.$2 : const [];
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Rewards', style: display(24)),
                  PointsPill('${fmtPts(balance)} pts', bg: Kig.forest, fg: Kig.sun),
                ],
              ),
              const SizedBox(height: 16),
              if (!snap.hasData) const Center(child: Padding(padding: EdgeInsets.all(30), child: CircularProgressIndicator())),
              if (snap.hasData && promos.isEmpty)
                const Padding(padding: EdgeInsets.all(30), child: Center(child: Text('No rewards available yet.', style: TextStyle(color: Kig.muted)))),
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 0.82,
                children: promos.map<Widget>((p) => _RewardCard(
                      promo: Map<String, dynamic>.from(p),
                      affordable: balance >= (p['RequiredCoins'] as num),
                      onTap: () => _redeem(Map<String, dynamic>.from(p), balance),
                    )).toList(),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _RewardCard extends StatelessWidget {
  final Map<String, dynamic> promo;
  final bool affordable;
  final VoidCallback onTap;
  const _RewardCard({required this.promo, required this.affordable, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Kig.line), borderRadius: BorderRadius.circular(16)),
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 54,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                gradient: const LinearGradient(colors: [Kig.mint, Color(0xFFEDF3EF)]),
              ),
              child: const Center(child: Icon(Icons.local_offer_outlined, color: Kig.forest)),
            ),
            const SizedBox(height: 10),
            Text(promo['VendorName'] ?? '', style: display(14), maxLines: 1, overflow: TextOverflow.ellipsis),
            const Row(children: [
              Icon(Icons.lock_outline, size: 12, color: Kig.muted),
              SizedBox(width: 3),
              Expanded(child: Text('Redeem to reveal code', style: TextStyle(color: Kig.muted, fontSize: 11.5), maxLines: 1, overflow: TextOverflow.ellipsis)),
            ]),
            const Spacer(),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 5),
              decoration: BoxDecoration(
                color: affordable ? Kig.sun : Kig.line,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Center(child: Text('${fmtPts(promo['RequiredCoins'] as num)} pts', style: display(12, color: Kig.forest))),
            ),
          ],
        ),
      ),
    );
  }
}
