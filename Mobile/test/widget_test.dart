// Smoke tests for Keep It Green. These avoid GoogleFonts (network) on purpose
// so they run fast and offline.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:keep_it_green/widgets.dart';

void main() {
  testWidgets('LeafToken renders the brand mark', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: Center(child: LeafToken()))),
    );
    expect(find.byType(LeafToken), findsOneWidget);
  });

  test('fmtPts groups thousands with commas', () {
    expect(fmtPts(15), '15');
    expect(fmtPts(1240), '1,240');
    expect(fmtPts(1000000), '1,000,000');
  });
}
