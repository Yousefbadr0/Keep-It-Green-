import 'package:flutter/material.dart';
import 'cairo.dart';
import 'services/api_service.dart';
import 'theme.dart';
import 'screens/welcome_screen.dart';
import 'screens/home_screen.dart';
import 'screens/admin_home.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  initCairo();
  await ApiService.instance.loadToken();
  runApp(const KeepItGreenApp());
}

class KeepItGreenApp extends StatelessWidget {
  const KeepItGreenApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Keep It Green',
        debugShowCheckedModeBanner: false,
        theme: buildTheme(),
        home: !ApiService.instance.isLoggedIn
            ? const WelcomeScreen()
            : (ApiService.instance.isAdmin ? const AdminHome() : const HomeScreen()),
      );
}
