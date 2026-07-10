import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import 'welcome_screen.dart';

class ProfileTab extends StatefulWidget {
  const ProfileTab({super.key});
  @override
  State<ProfileTab> createState() => _ProfileTabState();
}

class _ProfileTabState extends State<ProfileTab> {
  late Future<num> _coins;

  @override
  void initState() {
    super.initState();
    _coins = ApiService.instance.coins();
  }

  Future<void> _logout() async {
    await ApiService.instance.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const WelcomeScreen()), (r) => false);
  }

  @override
  Widget build(BuildContext context) {
    final name = ApiService.instance.userName;
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
      children: [
        Text('Profile', style: display(24)),
        const SizedBox(height: 18),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                CircleAvatar(radius: 26, backgroundColor: Kig.mint, child: Text(name.isNotEmpty ? name[0].toUpperCase() : 'U', style: display(20, color: Kig.forest))),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(name, style: display(18)),
                      const SizedBox(height: 2),
                      FutureBuilder<num>(
                        future: _coins,
                        builder: (context, s) => Text(
                          s.hasData ? '${fmtPts(s.data!)} points' : '… points',
                          style: const TextStyle(color: Kig.muted),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        OutlinedButton.icon(
          onPressed: _logout,
          icon: const Icon(Icons.logout, color: Color(0xFFB4452F)),
          label: const Text('Log out', style: TextStyle(color: Color(0xFFB4452F))),
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 14),
            side: const BorderSide(color: Kig.line),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          ),
        ),
      ],
    );
  }
}
