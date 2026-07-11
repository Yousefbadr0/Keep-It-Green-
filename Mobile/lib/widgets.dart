import 'package:flutter/material.dart';
import 'theme.dart';

/// The Keep It Green mark — a leaf inside a rounded "token".
class LeafToken extends StatelessWidget {
  final double size;
  final Color bg;
  final Color leaf;
  const LeafToken({super.key, this.size = 64, this.bg = Kig.spring, this.leaf = Colors.white});
  @override
  Widget build(BuildContext context) => Container(
        width: size,
        height: size,
        decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(size * 0.28)),
        child: Center(child: CustomPaint(size: Size(size * 0.6, size * 0.6), painter: _LeafPainter(leaf, bg))),
      );
}

class _LeafPainter extends CustomPainter {
  final Color leaf;
  final Color vein;
  _LeafPainter(this.leaf, this.vein);
  @override
  void paint(Canvas c, Size s) {
    final k = s.width / 100;
    final body = Path()
      ..moveTo(50 * k, 18 * k)
      ..cubicTo(72 * k, 34 * k, 72 * k, 63 * k, 50 * k, 82 * k)
      ..cubicTo(28 * k, 63 * k, 28 * k, 34 * k, 50 * k, 18 * k)
      ..close();
    c.drawPath(body, Paint()..color = leaf);
    Paint v(double w) => Paint()
      ..color = vein
      ..strokeWidth = w * k
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;
    c.drawLine(Offset(50 * k, 26 * k), Offset(50 * k, 78 * k), v(5));
    c.drawLine(Offset(50 * k, 45 * k), Offset(65 * k, 37 * k), v(4));
    c.drawLine(Offset(50 * k, 45 * k), Offset(35 * k, 37 * k), v(4));
    c.drawLine(Offset(50 * k, 58 * k), Offset(63 * k, 51 * k), v(4));
    c.drawLine(Offset(50 * k, 58 * k), Offset(37 * k, 51 * k), v(4));
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}

/// Sun-colored points pill, e.g. "+15 pts" or "1,240 pts".
class PointsPill extends StatelessWidget {
  final String text;
  final Color bg;
  final Color fg;
  const PointsPill(this.text, {super.key, this.bg = Kig.sun, this.fg = Kig.forest});
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
        decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
        child: Text(text, style: display(13, color: fg)),
      );
}

String fmtPts(num n) {
  final s = n.round().toString();
  return s.replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');
}

/// Compact filter (chips) + sort (menu) bar shared by every long list in the app
/// (activity, rewards, admin machines/reports/vendors). Pass an empty `filters`
/// list to show only the sort menu.
class FilterSortBar extends StatelessWidget {
  final List<String> filters;
  final String filter;
  final ValueChanged<String> onFilter;
  final List<String> sorts;
  final String sort;
  final ValueChanged<String> onSort;
  const FilterSortBar({
    super.key,
    this.filters = const [],
    this.filter = '',
    required this.onFilter,
    required this.sorts,
    required this.sort,
    required this.onSort,
  });

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(
        child: filters.length > 1
            ? SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: filters
                      .map((f) => Padding(
                            padding: const EdgeInsets.only(right: 6),
                            child: ChoiceChip(
                              label: Text(f),
                              selected: filter == f,
                              onSelected: (_) => onFilter(f),
                              showCheckmark: false,
                              selectedColor: Kig.mint,
                              labelStyle: TextStyle(
                                  color: filter == f ? Kig.forest : Kig.muted,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12.5),
                            ),
                          ))
                      .toList(),
                ),
              )
            : const SizedBox.shrink(),
      ),
      PopupMenuButton<String>(
        icon: const Icon(Icons.sort, color: Kig.forest),
        tooltip: 'Sort by',
        onSelected: onSort,
        itemBuilder: (_) => sorts
            .map((s) => PopupMenuItem<String>(
                  value: s,
                  child: Row(children: [
                    Icon(sort == s ? Icons.radio_button_checked : Icons.radio_button_off,
                        size: 16, color: sort == s ? Kig.forest : Kig.muted),
                    const SizedBox(width: 8),
                    Text(s),
                  ]),
                ))
            .toList(),
      ),
    ]);
  }
}

void showSnack(BuildContext context, String message, {bool error = false}) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(
      content: Text(message),
      backgroundColor: error ? const Color(0xFFB4452F) : Kig.forest,
      behavior: SnackBarBehavior.floating,
    ));
}
