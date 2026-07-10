import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets.dart';

class RedeemedScreen extends StatelessWidget {
  final String code;
  final String vendor;
  final num remaining;
  const RedeemedScreen({super.key, required this.code, required this.vendor, required this.remaining});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Kig.mint,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(30),
          child: Column(
            children: [
              const Spacer(),
              Container(
                width: 84, height: 84,
                decoration: BoxDecoration(
                  color: Kig.spring, shape: BoxShape.circle,
                  boxShadow: [BoxShadow(color: Kig.spring.withValues(alpha: 0.35), blurRadius: 30, offset: const Offset(0, 14))],
                ),
                child: const Center(child: Icon(Icons.check_rounded, color: Colors.white, size: 46)),
              ),
              const SizedBox(height: 16),
              Text('Redeemed!', style: display(26)),
              const SizedBox(height: 8),
              Text(vendor, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF41584C))),
              const SizedBox(height: 18),
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Kig.spring, width: 2, style: BorderStyle.solid),
                ),
                padding: const EdgeInsets.all(18),
                child: Column(
                  children: [
                    Text('YOUR CODE', style: label()),
                    const SizedBox(height: 4),
                    SelectableText(code, style: display(30, color: Kig.forest, tracking: 0.04)),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              const Text('Show this code at checkout.', style: TextStyle(color: Color(0xFF41584C), fontSize: 13)),
              const SizedBox(height: 8),
              Text.rich(TextSpan(children: [
                const TextSpan(text: 'New balance · ', style: TextStyle(color: Kig.muted, fontSize: 13)),
                TextSpan(text: '${fmtPts(remaining)} pts', style: display(13, weight: FontWeight.w700, color: Kig.forest)),
              ])),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  style: FilledButton.styleFrom(backgroundColor: Kig.forest, foregroundColor: Kig.paper),
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Done'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
