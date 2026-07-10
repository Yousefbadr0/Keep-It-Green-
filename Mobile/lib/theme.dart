import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Keep It Green — official brand palette (design handoff).
class Kig {
  static const spring = Color(0xFF18C964);   // primary — CTAs, accents
  static const forest = Color(0xFF0C3B2A);   // dark surfaces
  static const sun = Color(0xFFFFC83D);      // points / rewards
  static const mint = Color(0xFFDCF1E2);     // tint surface
  static const paper = Color(0xFFF6F7F1);    // page background
  static const charcoal = Color(0xFF13201A); // text
  static const muted = Color(0xFF6B7A72);    // secondary text
  static const line = Color(0xFFEBEEE9);     // hairline borders
  static const danger = Color(0xFFB4452F);   // destructive actions
}

/// Space Grotesk — headings, numbers, labels.
TextStyle display(double size, {FontWeight weight = FontWeight.w700, Color? color, double tracking = -0.01}) =>
    GoogleFonts.spaceGrotesk(fontSize: size, fontWeight: weight, color: color, letterSpacing: tracking * size);

/// Uppercase tracked label (Space Grotesk).
TextStyle label({Color color = Kig.muted}) =>
    GoogleFonts.spaceGrotesk(fontSize: 12, fontWeight: FontWeight.w500, letterSpacing: 1.7, color: color);

ThemeData buildTheme() {
  final base = ThemeData(useMaterial3: true, brightness: Brightness.light);
  const scheme = ColorScheme.light(
    primary: Kig.spring,
    secondary: Kig.sun,
    surface: Kig.paper,
    onPrimary: Kig.forest,
    onSurface: Kig.charcoal,
  );
  return base.copyWith(
    colorScheme: scheme,
    scaffoldBackgroundColor: Kig.paper,
    textTheme: GoogleFonts.hankenGroteskTextTheme(base.textTheme)
        .apply(bodyColor: Kig.charcoal, displayColor: Kig.charcoal),
    appBarTheme: const AppBarTheme(
      backgroundColor: Kig.paper,
      foregroundColor: Kig.charcoal,
      elevation: 0,
      scrolledUnderElevation: 0,
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Kig.line),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: Kig.spring,
        foregroundColor: Kig.forest,
        elevation: 0,
        padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 24),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
        textStyle: GoogleFonts.spaceGrotesk(fontWeight: FontWeight.w700, fontSize: 16),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Kig.line)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Kig.line)),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Kig.spring, width: 2)),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: Colors.white,
      indicatorColor: Kig.mint,
      labelTextStyle: WidgetStateProperty.all(GoogleFonts.spaceGrotesk(fontSize: 12, fontWeight: FontWeight.w600)),
    ),
  );
}
