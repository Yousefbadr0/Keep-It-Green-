import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Thrown for non-2xx responses, carrying the backend's message.
class ApiException implements Exception {
  final String message;
  final int statusCode;
  ApiException(this.message, this.statusCode);
  @override
  String toString() => message;
}

/// Single source of truth for talking to the Keep It Green .NET API.
class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  // ---------------------------------------------------------------------------
  // Where the .NET backend lives.
  // Compile-time default (used until you set a server inside the app):
  //   Web (Edge/Chrome) -> localhost ;  phone/emulator -> the LAN default below.
  // When your Wi-Fi / IP changes, you do NOT rebuild — just open the app's
  // "Server settings" screen and type the new PC IP. It's saved on the phone.
  // ---------------------------------------------------------------------------
  static const String _lanBaseUrl = 'https://keepitgreen.runasp.net';
  static const String defaultBaseUrl = kIsWeb ? 'http://localhost:5217' : _lanBaseUrl;

  String? _server; // runtime override typed in the app
  String get baseUrl => (_server != null && _server!.isNotEmpty) ? _server! : defaultBaseUrl;
  String get serverLabel => baseUrl;
  bool get hasCustomServer => _server != null && _server!.isNotEmpty;

  String? _token;
  // Logged in if the access token is still valid OR we hold a refresh token (the
  // first 401 then refreshes silently). Prevents both the old "stale token, empty
  // Home" bug and needless re-logins.
  bool get isLoggedIn {
    if (_token == null || _token!.isEmpty) return false;
    try {
      final exp = _payload()['exp'];
      if (exp is int && DateTime.now().millisecondsSinceEpoch >= exp * 1000) {
        return _refresh != null && _refresh!.isNotEmpty;
      }
    } catch (_) {/* no/undecodable exp -> treat as valid */}
    return true;
  }

  Future<void> loadToken() async {
    final p = await SharedPreferences.getInstance();
    _token = p.getString('kig_token');
    _refresh = p.getString('kig_refresh');
    // One-time cleanup: drop any old saved server (e.g. a LAN IP from earlier
    // testing) so upgrades always default to the live cloud backend.
    const cfgVersion = 2;
    if (p.getInt('kig_cfgv') != cfgVersion) {
      await p.remove('kig_server');
      await p.setInt('kig_cfgv', cfgVersion);
    }
    _server = p.getString('kig_server');
  }

  /// Turn user input like "192.168.1.50" into "http://192.168.1.50:5217".
  String _normalizeServer(String raw) {
    raw = raw.trim().replaceAll(RegExp(r'/+$'), '');
    if (raw.isEmpty) return '';
    if (!raw.startsWith('http://') && !raw.startsWith('https://')) raw = 'http://$raw';
    final afterScheme = raw.replaceFirst(RegExp(r'^https?://'), '');
    if (!afterScheme.contains(':')) raw = '$raw:5217';
    return raw;
  }

  /// Save the backend address typed in the app (empty clears it -> default).
  Future<void> setServer(String raw) async {
    final v = _normalizeServer(raw);
    _server = v.isEmpty ? null : v;
    final p = await SharedPreferences.getInstance();
    if (_server == null) {
      await p.remove('kig_server');
    } else {
      await p.setString('kig_server', _server!);
    }
  }

  /// Quick reachability check for the Server settings screen.
  /// Any HTTP reply means the PC is reachable; only refused/timeout is a fail.
  Future<bool> ping() async {
    try {
      final r = await http.get(Uri.parse('$baseUrl/')).timeout(const Duration(seconds: 6));
      return r.statusCode >= 200 && r.statusCode < 500;
    } catch (_) {
      return false;
    }
  }

  /// Decode the JWT payload (claims) as a map.
  Map<String, dynamic> _payload() {
    var payload = _token!.split('.')[1].replaceAll('-', '+').replaceAll('_', '/');
    payload = payload.padRight(payload.length + (4 - payload.length % 4) % 4, '=');
    return jsonDecode(utf8.decode(base64.decode(payload))) as Map<String, dynamic>;
  }

  /// Display name decoded from the JWT (falls back to "there").
  String get userName {
    try {
      final map = _payload();
      for (final k in ['unique_name', 'name', 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name']) {
        if (map[k] != null) return map[k].toString();
      }
    } catch (_) {}
    return 'there';
  }

  /// True when the logged-in account has the Admin role. The role claim key
  /// varies (short "role" vs the ClaimTypes.Role URI), and can be a list.
  bool get isAdmin {
    try {
      final map = _payload();
      final roles = <String>[];
      for (final e in map.entries) {
        final k = e.key.toLowerCase();
        if (k == 'role' || k == 'roles' || k.endsWith('/role') || k.endsWith('/roles')) {
          final v = e.value;
          if (v is List) {
            roles.addAll(v.map((x) => x.toString()));
          } else if (v != null) {
            roles.add(v.toString());
          }
        }
      }
      return roles.any((r) => r.toLowerCase() == 'admin');
    } catch (_) {
      return false;
    }
  }

  Future<void> _setToken(String? t) async {
    _token = t;
    final p = await SharedPreferences.getInstance();
    if (t == null) {
      await p.remove('kig_token');
    } else {
      await p.setString('kig_token', t);
    }
  }

  String? _refresh; // rotating refresh token (see _tryRefresh)
  Future<void> _setRefresh(String? t) async {
    _refresh = t;
    final p = await SharedPreferences.getInstance();
    if (t == null) {
      await p.remove('kig_refresh');
    } else {
      await p.setString('kig_refresh', t);
    }
  }

  Map<String, String> _headers({bool auth = true}) => {
        'Content-Type': 'application/json',
        if (auth && isLoggedIn) 'Authorization': 'Bearer $_token',
      };

  dynamic _decode(http.Response r) {
    dynamic body;
    try {
      body = r.body.isNotEmpty ? jsonDecode(r.body) : null;
    } catch (_) {
      body = r.body;
    }
    if (r.statusCode >= 200 && r.statusCode < 300) return body;
    String msg = 'Request failed (${r.statusCode})';
    if (body is Map && body['Message'] != null) {
      msg = body['Message'].toString();
    } else if (body is List && body.isNotEmpty) {
      msg = body
          .map((e) => e is Map ? (e['description'] ?? e['Description'] ?? e) : e)
          .join(' ');
    }
    throw ApiException(msg, r.statusCode);
  }

  /// Runs an authed request; on 401 it silently refreshes the access token once
  /// (rotating refresh token) and retries, so users stay signed in indefinitely
  /// without ever seeing a login screen mid-task.
  Future<dynamic> _authed(Future<http.Response> Function() send) async {
    try {
      return _decode(await send());
    } on ApiException catch (e) {
      if (e.statusCode == 401 && await _tryRefresh()) {
        return _decode(await send());
      }
      rethrow;
    } catch (_) {
      throw ApiException('Cannot reach the server. Is the backend running?', 0);
    }
  }

  Future<bool> _tryRefresh() async {
    if (_refresh == null || _refresh!.isEmpty) return false;
    try {
      final r = await http.post(Uri.parse('$baseUrl/api/User/Refresh'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'RefreshToken': _refresh}));
      if (r.statusCode < 200 || r.statusCode >= 300) return false;
      final body = jsonDecode(r.body) as Map<String, dynamic>;
      await _setToken(body['Token'] as String?);
      await _setRefresh(body['RefreshToken'] as String?);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<dynamic> _get(String path) =>
      _authed(() => http.get(Uri.parse('$baseUrl$path'), headers: _headers()));

  Future<dynamic> _post(String path, [Object? body, bool auth = true]) async {
    if (!auth) {
      try {
        return _decode(await http.post(Uri.parse('$baseUrl$path'),
            headers: _headers(auth: false), body: body != null ? jsonEncode(body) : null));
      } on ApiException {
        rethrow;
      } catch (_) {
        throw ApiException('Cannot reach the server. Is the backend running?', 0);
      }
    }
    return _authed(() => http.post(Uri.parse('$baseUrl$path'),
        headers: _headers(), body: body != null ? jsonEncode(body) : null));
  }

  Future<dynamic> _put(String path, [Object? body]) =>
      _authed(() => http.put(Uri.parse('$baseUrl$path'),
          headers: _headers(), body: body != null ? jsonEncode(body) : null));

  Future<dynamic> _delete(String path) =>
      _authed(() => http.delete(Uri.parse('$baseUrl$path'), headers: _headers()));

  // ---- auth ----
  Future<void> login(String email, String password) async {
    final r = await _post('/api/User/Login', {'Email': email, 'Password': password}, false);
    await _setToken(r['Token'] as String);
    await _setRefresh(r['RefreshToken'] as String?);
  }

  Future<void> register(String userName, String email, String password) =>
      _post('/api/User/Register', {'UserName': userName, 'Email': email, 'Password': password}, false);

  Future<void> logout() async {
    await _setToken(null);
    await _setRefresh(null);
  }

  // ---- ATM pairing (scan the machine QR / enter the code) ----
  Future<Map<String, dynamic>> pair(String code) async =>
      Map<String, dynamic>.from(await _post('/api/Otp/Pair', {'Code': code}));

  /// End the current user's active session (tapped "Finish" on the phone) so the
  /// machine returns to idle. Best-effort — never blocks leaving the screen.
  Future<void> endSession() async {
    try {
      await _post('/api/Otp/EndSession');
    } catch (_) {/* ignore — the session also ends on the machine's idle timeout */}
  }

  /// Is this user's session still live? The live screen polls this so it auto-closes when
  /// the MACHINE ends the session. Fail-safe: returns true on a network blip (never closes).
  Future<bool> sessionActive() async {
    try {
      return (await _get('/api/Otp/session/active'))['Active'] as bool? ?? true;
    } catch (_) {
      return true;
    }
  }

  // ---- user data ----
  Future<num> coins() async => (await _get('/api/User/Coins'))['Coins'] as num;
  Future<List<dynamic>> machines() async => await _get('/api/Machine') as List<dynamic>;
  Future<String> generateOtp(int machineId) async =>
      (await _get('/api/Otp/Generate/$machineId'))['Otp'].toString();
  Future<List<dynamic>> myTransactions() async =>
      await _get('/api/Transaction/User') as List<dynamic>;
  Future<List<dynamic>> promos() async => await _get('/api/Promo') as List<dynamic>;
  Future<Map<String, dynamic>> redeem(int promoId) async =>
      Map<String, dynamic>.from(await _post('/api/Redemption/$promoId'));
  Future<List<dynamic>> myRedemptions() async =>
      await _get('/api/Redemption/My') as List<dynamic>;

  // ---- admin ----
  Future<void> addMachine(String name, String location, bool available) =>
      _post('/api/Machine', {'Name': name, 'Location': location, 'IsAvailable': available});
  Future<void> setMachineAvailable(int id, bool available) =>
      _put('/api/Machine/$id', {'IsAvailable': available});
  Future<void> deleteMachine(int id) => _delete('/api/Machine/$id');

  Future<List<dynamic>> vendors() async => await _get('/api/Vendor') as List<dynamic>;
  Future<void> addVendor(String name, String email, String? description) =>
      _post('/api/Vendor', {'Name': name, 'Email': email, 'Description': description});

  Future<void> addPromo({
    required int vendorId,
    required String code,
    required int requiredCoins,
    required DateTime expiration,
    required int usageLimit,
  }) =>
      _post('/api/Promo', {
        'VendorId': vendorId,
        'Code': code,
        'RequiredCoins': requiredCoins,
        'ExpirationDate': expiration.toIso8601String(),
        'UsageLimit': usageLimit,
      });

  /// All transactions recorded at a machine (admin report).
  Future<List<dynamic>> adminTransactions(int machineId) async =>
      await _get('/api/Transaction/Admin/$machineId?page=1&pageSize=200') as List<dynamic>;
}
