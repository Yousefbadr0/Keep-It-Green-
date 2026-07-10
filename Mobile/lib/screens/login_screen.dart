import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import 'home_screen.dart';
import 'admin_home.dart';
import 'register_screen.dart';
import 'server_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;
  bool _busy = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (_email.text.trim().isEmpty || _password.text.isEmpty) {
      showSnack(context, 'Enter your email and password', error: true);
      return;
    }
    setState(() => _busy = true);
    try {
      await ApiService.instance.login(_email.text.trim(), _password.text);
      if (!mounted) return;
      final dest = ApiService.instance.isAdmin ? const AdminHome() : const HomeScreen();
      Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => dest), (r) => false);
    } on ApiException catch (e) {
      if (mounted) showSnack(context, e.message, error: true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final hint = Kig.paper.withValues(alpha: 0.7);
    return Scaffold(
      backgroundColor: Kig.forest,
      appBar: AppBar(backgroundColor: Kig.forest, foregroundColor: Kig.paper, elevation: 0, actions: [
        IconButton(
          icon: const Icon(Icons.dns_outlined),
          tooltip: 'Server settings',
          onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ServerScreen())),
        ),
      ]),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(28, 8, 28, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Center(child: LeafToken(size: 64)),
              const SizedBox(height: 18),
              Text('Welcome back', style: display(28, color: Kig.paper)),
              const SizedBox(height: 6),
              Text('Log in to keep stacking points', style: TextStyle(color: hint)),
              const SizedBox(height: 26),
              _field(_email, 'Email', keyboard: TextInputType.emailAddress),
              const SizedBox(height: 14),
              _field(_password, 'Password', obscure: _obscure, suffix: IconButton(
                icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off, color: Kig.muted),
                onPressed: () => setState(() => _obscure = !_obscure),
              )),
              const SizedBox(height: 22),
              FilledButton(
                onPressed: _busy ? null : _login,
                child: _busy
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Kig.forest))
                    : const Text('Log in'),
              ),
              const SizedBox(height: 16),
              Center(
                child: GestureDetector(
                  onTap: () => Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const RegisterScreen())),
                  child: Text.rich(TextSpan(children: [
                    TextSpan(text: "No account? ", style: TextStyle(color: hint)),
                    TextSpan(text: 'Create one', style: display(14, weight: FontWeight.w600, color: Kig.spring)),
                  ])),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(TextEditingController c, String label, {bool obscure = false, TextInputType? keyboard, Widget? suffix}) {
    return TextField(
      controller: c,
      obscureText: obscure,
      keyboardType: keyboard,
      decoration: InputDecoration(labelText: label, suffixIcon: suffix),
    );
  }
}
