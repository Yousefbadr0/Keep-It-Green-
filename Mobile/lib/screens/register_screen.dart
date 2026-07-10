import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import '../widgets.dart';
import 'login_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;
  bool _busy = false;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (_name.text.trim().isEmpty || _email.text.trim().isEmpty || _password.text.isEmpty) {
      showSnack(context, 'Please fill in all fields', error: true);
      return;
    }
    setState(() => _busy = true);
    try {
      await ApiService.instance.register(_name.text.trim(), _email.text.trim(), _password.text);
      if (!mounted) return;
      showSnack(context, 'Account created â€” please log in');
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const LoginScreen()));
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
      appBar: AppBar(backgroundColor: Kig.forest, foregroundColor: Kig.paper, elevation: 0),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(28, 8, 28, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Center(child: LeafToken(size: 64)),
              const SizedBox(height: 18),
              Text('Create account', style: display(28, color: Kig.paper)),
              const SizedBox(height: 6),
              Text('Start earning points for recycling', style: TextStyle(color: hint)),
              const SizedBox(height: 26),
              TextField(controller: _name, decoration: const InputDecoration(labelText: 'Username')),
              const SizedBox(height: 14),
              TextField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email')),
              const SizedBox(height: 14),
              TextField(
                controller: _password,
                obscureText: _obscure,
                decoration: InputDecoration(
                  labelText: 'Password',
                  helperText: 'Min 6 chars Â· upper, lower, digit, symbol',
                  suffixIcon: IconButton(
                    icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off, color: Kig.muted),
                    onPressed: () => setState(() => _obscure = !_obscure),
                  ),
                ),
              ),
              const SizedBox(height: 22),
              FilledButton(
                onPressed: _busy ? null : _register,
                child: _busy
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Kig.forest))
                    : const Text('Create account'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
