import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import '../cairo.dart';
import 'welcome_screen.dart';

/// Separate home for Admin accounts. The user-flow endpoints are role-locked to
/// "User", so admins get their own management screens instead of the reward UI.
class AdminHome extends StatefulWidget {
  const AdminHome({super.key});
  @override
  State<AdminHome> createState() => _AdminHomeState();
}

class _AdminHomeState extends State<AdminHome> {
  final PageController _controller = PageController();
  int _index = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _go(int i) {
    setState(() => _index = i);
    _controller.animateToPage(i, duration: const Duration(milliseconds: 260), curve: Curves.easeOutCubic);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: PageView(
          controller: _controller,
          onPageChanged: (i) => setState(() => _index = i),
          children: const [_MachinesTab(), _RewardsTab(), _ReportsTab(), _AdminProfile()],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: _go,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.point_of_sale_outlined), selectedIcon: Icon(Icons.point_of_sale), label: 'Machines'),
          NavigationDestination(icon: Icon(Icons.card_giftcard_outlined), selectedIcon: Icon(Icons.card_giftcard), label: 'Rewards'),
          NavigationDestination(icon: Icon(Icons.receipt_long_outlined), selectedIcon: Icon(Icons.receipt_long), label: 'Reports'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Admin'),
        ],
      ),
    );
  }
}

String _s(Map m, List<String> keys, [String def = '']) {
  for (final k in keys) {
    if (m[k] != null) return m[k].toString();
  }
  return def;
}

/// Compact filter (chips) + sort (menu) bar reused across the admin lists.
class _FilterSort extends StatelessWidget {
  final List<String> filters;
  final String filter;
  final ValueChanged<String> onFilter;
  final List<String> sorts;
  final String sort;
  final ValueChanged<String> onSort;
  const _FilterSort({
    required this.filters, required this.filter, required this.onFilter,
    required this.sorts, required this.sort, required this.onSort,
  });
  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: filters.map((f) => Padding(
              padding: const EdgeInsets.only(right: 6),
              child: ChoiceChip(
                label: Text(f),
                selected: filter == f,
                onSelected: (_) => onFilter(f),
                showCheckmark: false,
                selectedColor: Kig.mint,
                labelStyle: TextStyle(
                    color: filter == f ? Kig.forest : Kig.muted,
                    fontWeight: FontWeight.w600, fontSize: 12.5),
              ),
            )).toList(),
          ),
        ),
      ),
      PopupMenuButton<String>(
        icon: const Icon(Icons.sort, color: Kig.forest),
        tooltip: 'Sort by',
        onSelected: onSort,
        itemBuilder: (_) => sorts.map((sName) => PopupMenuItem<String>(
          value: sName,
          child: Row(children: [
            Icon(sort == sName ? Icons.radio_button_checked : Icons.radio_button_off,
                size: 16, color: sort == sName ? Kig.forest : Kig.muted),
            const SizedBox(width: 8),
            Text(sName),
          ]),
        )).toList(),
      ),
    ]);
  }
}

// ============================ MACHINES ============================
class _MachinesTab extends StatefulWidget {
  const _MachinesTab();
  @override
  State<_MachinesTab> createState() => _MachinesTabState();
}

class _MachinesTabState extends State<_MachinesTab> {
  late Future<List<dynamic>> _future;
  String _filter = 'All';       // All / Available / Offline
  String _sort = 'Name';        // Name / Location

  List<dynamic> _apply(List<dynamic> src) {
    bool avail(dynamic m) => (m['IsAvailable'] ?? m['isAvailable'] ?? false) == true;
    final list = src.where((m) =>
        _filter == 'All' ||
        (_filter == 'Available' && avail(m)) ||
        (_filter == 'Offline' && !avail(m))).toList();
    final key = _sort == 'Location' ? ['Location', 'location'] : ['Name', 'name'];
    list.sort((a, b) => _s(Map.from(a), key).toLowerCase().compareTo(_s(Map.from(b), key).toLowerCase()));
    return list;
  }

  @override
  void initState() {
    super.initState();
    _future = ApiService.instance.machines();
  }

  void _reload() => setState(() => _future = ApiService.instance.machines());

  Future<void> _add() async {
    final name = TextEditingController();
    final loc = TextEditingController();
    bool available = true;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Add machine'),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: name, decoration: const InputDecoration(labelText: 'Name')),
            const SizedBox(height: 10),
            TextField(controller: loc, decoration: const InputDecoration(labelText: 'Location (city)')),
            const SizedBox(height: 6),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Available'),
              value: available,
              onChanged: (v) => setSt(() => available = v),
            ),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Add')),
          ],
        ),
      ),
    );
    if (ok != true) return;
    if (name.text.trim().isEmpty || loc.text.trim().isEmpty) {
      if (mounted) showSnack(context, 'Name and location are required', error: true);
      return;
    }
    try {
      await ApiService.instance.addMachine(name.text.trim(), loc.text.trim(), available);
      if (mounted) showSnack(context, 'Machine added');
      _reload();
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  Future<void> _toggle(int id, bool value) async {
    try {
      await ApiService.instance.setMachineAvailable(id, value);
      _reload();
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  Future<void> _delete(int id, String name) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete machine'),
        content: Text('Remove "$name"? This cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
              style: FilledButton.styleFrom(backgroundColor: Kig.danger),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await ApiService.instance.deleteMachine(id);
      if (mounted) showSnack(context, 'Machine deleted');
      _reload();
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.paper,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _add,
        backgroundColor: Kig.spring,
        foregroundColor: Kig.forest,
        icon: const Icon(Icons.add),
        label: const Text('Add machine'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<dynamic>>(
          future: _future,
          builder: (context, snap) {
            if (!snap.hasData) {
              if (snap.hasError) return _error(snap.error);
              return const Center(child: CircularProgressIndicator());
            }
            final machines = snap.data!;
            final shown = _apply(machines);
            return ListView(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 90),
              children: [
                Text('Machines', style: display(24)),
                const SizedBox(height: 4),
                Text('${machines.length} total', style: const TextStyle(color: Kig.muted)),
                const SizedBox(height: 12),
                if (machines.isNotEmpty)
                  _FilterSort(
                    filters: const ['All', 'Available', 'Offline'], filter: _filter,
                    onFilter: (f) => setState(() => _filter = f),
                    sorts: const ['Name', 'Location'], sort: _sort,
                    onSort: (s) => setState(() => _sort = s),
                  ),
                const SizedBox(height: 10),
                if (machines.isEmpty)
                  const Padding(padding: EdgeInsets.all(30), child: Center(child: Text('No machines yet. Tap "Add machine".', style: TextStyle(color: Kig.muted)))),
                if (machines.isNotEmpty && shown.isEmpty)
                  const Padding(padding: EdgeInsets.all(20), child: Center(child: Text('No machines match this filter.', style: TextStyle(color: Kig.muted)))),
                ...shown.map((m0) {
                  final m = Map<String, dynamic>.from(m0);
                  final id = (m['Id'] ?? m['id']) as int;
                  final available = (m['IsAvailable'] ?? m['isAvailable'] ?? false) == true;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Kig.line), borderRadius: BorderRadius.circular(16)),
                    padding: const EdgeInsets.fromLTRB(16, 10, 8, 10),
                    child: Row(children: [
                      Expanded(
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text(_s(m, ['Name', 'name'], 'Machine'), style: display(16)),
                          const SizedBox(height: 2),
                          Row(children: [
                            const Icon(Icons.place_outlined, size: 14, color: Kig.muted),
                            const SizedBox(width: 3),
                            Text(_s(m, ['Location', 'location']), style: const TextStyle(color: Kig.muted, fontSize: 13)),
                            const SizedBox(width: 8),
                            _statusChip(available),
                          ]),
                        ]),
                      ),
                      Switch(value: available, activeThumbColor: Kig.spring, onChanged: (v) => _toggle(id, v)),
                      IconButton(icon: const Icon(Icons.delete_outline, color: Kig.danger), onPressed: () => _delete(id, _s(m, ['Name', 'name'], 'this machine'))),
                    ]),
                  );
                }),
              ],
            );
          },
        ),
      ),
    );
  }
}

Widget _statusChip(bool available) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: available ? Kig.mint : const Color(0xFFF1E3DF),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(available ? 'Available' : 'Offline',
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: available ? Kig.forest : Kig.danger)),
    );

Widget _error(Object? e) => Center(
      child: Padding(
        padding: const EdgeInsets.all(30),
        child: Text('Could not load.\n$e', textAlign: TextAlign.center, style: const TextStyle(color: Kig.muted)),
      ),
    );

// ============================ REWARDS ============================
class _RewardsTab extends StatefulWidget {
  const _RewardsTab();
  @override
  State<_RewardsTab> createState() => _RewardsTabState();
}

class _RewardsTabState extends State<_RewardsTab> {
  late Future<List<dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _future = ApiService.instance.vendors();
  }

  void _reload() => setState(() => _future = ApiService.instance.vendors());

  Future<void> _addVendor() async {
    final name = TextEditingController();
    final email = TextEditingController();
    final desc = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add vendor'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: name, decoration: const InputDecoration(labelText: 'Name')),
          const SizedBox(height: 10),
          TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email')),
          const SizedBox(height: 10),
          TextField(controller: desc, decoration: const InputDecoration(labelText: 'Description (optional)')),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Add')),
        ],
      ),
    );
    if (ok != true) return;
    if (name.text.trim().isEmpty || email.text.trim().isEmpty) {
      if (mounted) showSnack(context, 'Name and email are required', error: true);
      return;
    }
    try {
      await ApiService.instance.addVendor(name.text.trim(), email.text.trim(), desc.text.trim().isEmpty ? null : desc.text.trim());
      if (mounted) showSnack(context, 'Vendor added');
      _reload();
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  Future<void> _addPromo(List<dynamic> vendors) async {
    if (vendors.isEmpty) {
      showSnack(context, 'Add a vendor first', error: true);
      return;
    }
    int vendorId = (vendors.first['Id'] ?? vendors.first['id']) as int;
    final code = TextEditingController();
    final coins = TextEditingController(text: '50');
    final usage = TextEditingController(text: '10');
    DateTime expiry = DateTime.now().add(const Duration(days: 30));
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Add promo code'),
          content: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              DropdownButtonFormField<int>(
                initialValue: vendorId,
                decoration: const InputDecoration(labelText: 'Vendor'),
                items: vendors
                    .map((v) => DropdownMenuItem<int>(
                          value: (v['Id'] ?? v['id']) as int,
                          child: Text(_s(Map<String, dynamic>.from(v), ['Name', 'name'], 'Vendor')),
                        ))
                    .toList(),
                onChanged: (v) => vendorId = v ?? vendorId,
              ),
              const SizedBox(height: 10),
              TextField(controller: code, decoration: const InputDecoration(labelText: 'Code')),
              const SizedBox(height: 10),
              TextField(controller: coins, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Required points')),
              const SizedBox(height: 10),
              TextField(controller: usage, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Usage limit')),
              const SizedBox(height: 10),
              Row(children: [
                Expanded(child: Text('Expires: ${cairoDate(expiry.toIso8601String())}', style: const TextStyle(color: Kig.muted))),
                TextButton(
                  onPressed: () async {
                    final d = await showDatePicker(context: ctx, initialDate: expiry, firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 730)));
                    if (d != null) setSt(() => expiry = d);
                  },
                  child: const Text('Pick date'),
                ),
              ]),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Add')),
          ],
        ),
      ),
    );
    if (ok != true) return;
    if (code.text.trim().isEmpty) {
      if (mounted) showSnack(context, 'Code is required', error: true);
      return;
    }
    try {
      await ApiService.instance.addPromo(
        vendorId: vendorId,
        code: code.text.trim(),
        requiredCoins: int.tryParse(coins.text.trim()) ?? 0,
        expiration: expiry,
        usageLimit: int.tryParse(usage.text.trim()) ?? 1,
      );
      if (mounted) showSnack(context, 'Promo added');
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.paper,
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<dynamic>>(
          future: _future,
          builder: (context, snap) {
            final vendors = snap.hasData ? snap.data! : const [];
            return ListView(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 30),
              children: [
                Text('Rewards', style: display(24)),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(child: FilledButton.tonalIcon(onPressed: _addVendor, icon: const Icon(Icons.store_outlined), label: const Text('Add vendor'))),
                  const SizedBox(width: 10),
                  Expanded(child: FilledButton.icon(onPressed: () => _addPromo(vendors), icon: const Icon(Icons.local_offer_outlined), label: const Text('Add promo'))),
                ]),
                const SizedBox(height: 18),
                Text('Vendors', style: display(16)),
                const SizedBox(height: 8),
                if (!snap.hasData) const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator())),
                if (snap.hasData && vendors.isEmpty)
                  const Padding(padding: EdgeInsets.all(20), child: Text('No vendors yet.', style: TextStyle(color: Kig.muted))),
                ...vendors.map((v0) {
                  final v = Map<String, dynamic>.from(v0);
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Kig.line), borderRadius: BorderRadius.circular(14)),
                    padding: const EdgeInsets.all(14),
                    child: Row(children: [
                      const Icon(Icons.store_mall_directory_outlined, color: Kig.forest),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text(_s(v, ['Name', 'name'], 'Vendor'), style: display(15)),
                          Text(_s(v, ['Email', 'email']), style: const TextStyle(color: Kig.muted, fontSize: 12.5)),
                        ]),
                      ),
                    ]),
                  );
                }),
              ],
            );
          },
        ),
      ),
    );
  }
}

// ============================ REPORTS ============================
class _ReportsTab extends StatefulWidget {
  const _ReportsTab();
  @override
  State<_ReportsTab> createState() => _ReportsTabState();
}

class _ReportsTabState extends State<_ReportsTab> {
  List<dynamic> _machines = [];
  int? _machineId;
  Future<List<dynamic>>? _txns;
  bool _loadingMachines = true;
  String _filter = 'All';        // All / Plastic / Aluminum
  String _sort = 'Newest';       // Newest / Oldest / Most points

  List<dynamic> _apply(List<dynamic> src) {
    bool plastic(dynamic t) => _s(Map.from(t), ['ItemType', 'itemType', 'Type']).toLowerCase().contains('plastic');
    int pts(dynamic t) => int.tryParse(_s(Map.from(t), ['CoinsEarned', 'coinsEarned', 'Points', 'points', 'Coins'])) ?? 0;
    String when(dynamic t) => _s(Map.from(t), ['CreatedAt', 'createdAt', 'Date', 'date', 'Time']);
    final list = src.where((t) =>
        _filter == 'All' ||
        (_filter == 'Plastic' && plastic(t)) ||
        (_filter == 'Aluminum' && !plastic(t))).toList();
    if (_sort == 'Most points') {
      list.sort((a, b) => pts(b).compareTo(pts(a)));
    } else if (_sort == 'Oldest') {
      list.sort((a, b) => when(a).compareTo(when(b)));   // ISO strings sort chronologically
    } else {
      list.sort((a, b) => when(b).compareTo(when(a)));   // Newest
    }
    return list;
  }

  @override
  void initState() {
    super.initState();
    _loadMachines();
  }

  Future<void> _loadMachines() async {
    try {
      final m = await ApiService.instance.machines();
      if (!mounted) return;
      setState(() {
        _machines = m;
        _loadingMachines = false;
        if (m.isNotEmpty) {
          _machineId = (m.first['Id'] ?? m.first['id']) as int;
          _txns = ApiService.instance.adminTransactions(_machineId!);
        }
      });
    } catch (_) {
      if (mounted) setState(() => _loadingMachines = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.paper,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 30),
        children: [
          Text('Reports', style: display(24)),
          const SizedBox(height: 4),
          const Text('Transactions recorded at a machine', style: TextStyle(color: Kig.muted)),
          const SizedBox(height: 14),
          if (_loadingMachines) const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator())),
          if (!_loadingMachines && _machines.isEmpty)
            const Padding(padding: EdgeInsets.all(20), child: Text('No machines to report on.', style: TextStyle(color: Kig.muted))),
          if (_machines.isNotEmpty)
            DropdownButtonFormField<int>(
              initialValue: _machineId,
              decoration: const InputDecoration(labelText: 'Machine'),
              items: _machines
                  .map((m) => DropdownMenuItem<int>(
                        value: (m['Id'] ?? m['id']) as int,
                        child: Text(_s(Map<String, dynamic>.from(m), ['Name', 'name'], 'Machine')),
                      ))
                  .toList(),
              onChanged: (v) => setState(() {
                _machineId = v;
                _txns = v == null ? null : ApiService.instance.adminTransactions(v);
              }),
            ),
          const SizedBox(height: 14),
          if (_txns != null)
            FutureBuilder<List<dynamic>>(
              future: _txns,
              builder: (context, snap) {
                if (!snap.hasData) {
                  if (snap.hasError) return _error(snap.error);
                  return const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()));
                }
                final txns = snap.data!;
                if (txns.isEmpty) {
                  return const Padding(padding: EdgeInsets.all(20), child: Text('No transactions at this machine yet.', style: TextStyle(color: Kig.muted)));
                }
                final shown = _apply(txns);
                return Column(
                  children: [
                    _FilterSort(
                      filters: const ['All', 'Plastic', 'Aluminum'], filter: _filter,
                      onFilter: (f) => setState(() => _filter = f),
                      sorts: const ['Newest', 'Oldest', 'Most points'], sort: _sort,
                      onSort: (s) => setState(() => _sort = s),
                    ),
                    const SizedBox(height: 10),
                    if (shown.isEmpty)
                      const Padding(padding: EdgeInsets.all(20), child: Text('No transactions match this filter.', style: TextStyle(color: Kig.muted))),
                    ...shown.map((t0) {
                    final t = Map<String, dynamic>.from(t0);
                    final item = _s(t, ['ItemType', 'itemType', 'Type']);
                    final plastic = item.toLowerCase().contains('plastic');
                    final pts = _s(t, ['CoinsEarned', 'coinsEarned', 'Points', 'points', 'Coins']);
                    final when = _s(t, ['CreatedAt', 'createdAt', 'Date', 'date', 'Time']);
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Kig.line), borderRadius: BorderRadius.circular(14)),
                      padding: const EdgeInsets.all(14),
                      child: Row(children: [
                        Icon(plastic ? Icons.local_drink_outlined : Icons.local_bar_outlined, color: Kig.forest),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Text(item.isEmpty ? 'Item' : (plastic ? 'Plastic bottle' : 'Aluminum can'), style: display(15)),
                            if (when.isNotEmpty) Text(cairoDateTime(when), style: const TextStyle(color: Kig.muted, fontSize: 12.5)),
                          ]),
                        ),
                        if (pts.isNotEmpty) PointsPill('+$pts'),
                      ]),
                    );
                  }),
                  ],
                );
              },
            ),
        ],
      ),
    );
  }
}

// ============================ ADMIN PROFILE ============================
class _AdminProfile extends StatelessWidget {
  const _AdminProfile();

  Future<void> _logout(BuildContext context) async {
    await ApiService.instance.logout();
    if (!context.mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const WelcomeScreen()), (r) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.paper,
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 30),
        children: [
          const SizedBox(height: 10),
          const Center(child: LeafToken(size: 64)),
          const SizedBox(height: 14),
          Center(child: Text(ApiService.instance.userName, style: display(22))),
          const SizedBox(height: 2),
          const Center(
            child: Text('Administrator', style: TextStyle(color: Kig.muted, fontWeight: FontWeight.w600)),
          ),
          const SizedBox(height: 28),
          Container(
            decoration: BoxDecoration(color: Colors.white, border: Border.all(color: Kig.line), borderRadius: BorderRadius.circular(16)),
            child: const Column(children: [
              ListTile(leading: Icon(Icons.point_of_sale_outlined), title: Text('Manage machines'), subtitle: Text('Add, toggle, and remove machines')),
              Divider(height: 1),
              ListTile(leading: Icon(Icons.card_giftcard_outlined), title: Text('Manage rewards'), subtitle: Text('Vendors and promo codes')),
              Divider(height: 1),
              ListTile(leading: Icon(Icons.receipt_long_outlined), title: Text('View reports'), subtitle: Text('Per-machine transactions')),
            ]),
          ),
          const SizedBox(height: 22),
          FilledButton.icon(
            style: FilledButton.styleFrom(backgroundColor: Kig.forest, foregroundColor: Kig.paper),
            onPressed: () => _logout(context),
            icon: const Icon(Icons.logout),
            label: const Text('Log out'),
          ),
        ],
      ),
    );
  }
}
