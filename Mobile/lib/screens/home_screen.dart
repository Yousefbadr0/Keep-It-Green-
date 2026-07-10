import 'package:flutter/material.dart';
import 'home_tab.dart';
import 'rewards_tab.dart';
import 'history_tab.dart';
import 'profile_tab.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final PageController _controller = PageController();
  int _index = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // Tapping the bottom bar animates the pager to that page (keeps them in sync).
  void _go(int i) {
    setState(() => _index = i);
    _controller.animateToPage(i, duration: const Duration(milliseconds: 260), curve: Curves.easeOutCubic);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Swipe left/right to move between pages; each tab lazy-loads its data and
      // supports pull-to-refresh.
      body: SafeArea(
        bottom: false,
        child: PageView(
          controller: _controller,
          onPageChanged: (i) => setState(() => _index = i),
          children: const [HomeTab(), RewardsTab(), HistoryTab(), ProfileTab()],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: _go,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.card_giftcard_outlined), selectedIcon: Icon(Icons.card_giftcard), label: 'Rewards'),
          NavigationDestination(icon: Icon(Icons.history), label: 'Activity'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
