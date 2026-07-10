// Keep It Green — Flutter theme. Requires: google_fonts in pubspec.yaml
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class KigColors {
  static const spring   = Color(0xFF18C964);
  static const forest   = Color(0xFF0C3B2A);
  static const sun      = Color(0xFFFFC83D);
  static const mint     = Color(0xFFDCF1E2);
  static const paper    = Color(0xFFF6F7F1);
  static const charcoal = Color(0xFF13201A);
  static const muted    = Color(0xFF6B7A72);
}

ThemeData kigTheme() {
  final base = ThemeData(useMaterial3: true, brightness: Brightness.light);
  return base.copyWith(
    scaffoldBackgroundColor: KigColors.paper,
    colorScheme: const ColorScheme.light(
      primary: KigColors.spring,
      secondary: KigColors.sun,
      surface: KigColors.paper,
      onPrimary: KigColors.forest,
      onSurface: KigColors.charcoal,
    ),
    textTheme: TextTheme(
      // display / headings / numbers / labels  -> Space Grotesk
      displayLarge: GoogleFonts.spaceGrotesk(fontSize: 52, fontWeight: FontWeight.w700, letterSpacing: -1, color: KigColors.charcoal),
      headlineSmall: GoogleFonts.spaceGrotesk(fontSize: 32, fontWeight: FontWeight.w700, color: KigColors.charcoal),
      titleMedium:  GoogleFonts.spaceGrotesk(fontSize: 22, fontWeight: FontWeight.w500, color: KigColors.charcoal),
      labelSmall:   GoogleFonts.spaceGrotesk(fontSize: 13, fontWeight: FontWeight.w500, letterSpacing: 1.8, color: KigColors.muted),
      // body -> Hanken Grotesk
      bodyLarge:  GoogleFonts.hankenGrotesk(fontSize: 17, height: 1.7, color: KigColors.charcoal),
      bodyMedium: GoogleFonts.hankenGrotesk(fontSize: 15, height: 1.6, color: KigColors.charcoal),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: KigColors.spring,
        foregroundColor: KigColors.forest,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        textStyle: GoogleFonts.spaceGrotesk(fontWeight: FontWeight.w700, fontSize: 16),
      ),
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    ),
  );
}
