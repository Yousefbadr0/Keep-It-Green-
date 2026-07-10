import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets.dart';
import 'login_screen.dart';
import 'register_screen.dart';
import 'server_screen.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.forest,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            children: [
              Align(
                alignment: Alignment.centerRight,
                child: IconButton(
                  icon: const Icon(Icons.dns_outlined, color: Kig.paper),
                  tooltip: 'Server settings',
                  onPressed: () => Navigator.of(context)
                      .push(MaterialPageRoute(builder: (_) => const ServerScreen())),
                ),
              ),
              const Spacer(),
              const LeafToken(size: 92),
              const SizedBox(height: 20),
              Text.rich(TextSpan(children: [
                TextSpan(text: 'Keep It ', style: display(30, color: Kig.paper)),
                TextSpan(text: 'Green', style: display(30, color: Kig.spring)),
              ])),
              const SizedBox(height: 12),
              Text('Recycling that rewards you.', style: display(15, weight: FontWeight.w500, color: Kig.sun)),
              const SizedBox(height: 12),
              Text(
                'Scan a machine, drop your bottles and cans, and stack up points for real perks.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Kig.paper.withValues(alpha: 0.7), height: 1.6, fontSize: 14),
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RegisterScreen())),
                  child: const Text('Create account'),
                ),
              ),
              const SizedBox(height: 14),
              GestureDetector(
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const LoginScreen())),
                child: Text.rich(TextSpan(children: [
                  TextSpan(text: 'I already have an account · ', style: TextStyle(color: Kig.paper.withValues(alpha: 0.75), fontSize: 14)),
                  TextSpan(text: 'Log in', style: display(14, weight: FontWeight.w600, color: Kig.spring)),
                ])),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}
