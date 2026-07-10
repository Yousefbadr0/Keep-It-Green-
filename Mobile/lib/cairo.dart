import 'package:intl/intl.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tzdata;

/// All times in the app are shown in Cairo time (Africa/Cairo, DST-aware).
/// The backend sends UTC timestamps (…Z); we convert them here.
late tz.Location _cairo;
bool _ready = false;

void initCairo() {
  if (_ready) return;
  tzdata.initializeTimeZones();
  _cairo = tz.getLocation('Africa/Cairo');
  _ready = true;
}

tz.TZDateTime _toCairo(String iso) {
  final d = DateTime.parse(iso);
  final utc = d.isUtc ? d : DateTime.utc(d.year, d.month, d.day, d.hour, d.minute, d.second, d.millisecond);
  return tz.TZDateTime.from(utc, _cairo);
}

String cairoDateTime(String iso) {
  try { return DateFormat('d MMM · h:mm a').format(_toCairo(iso)); } catch (_) { return iso; }
}

String cairoDate(String iso) {
  try { return DateFormat('d MMM yyyy').format(_toCairo(iso)); } catch (_) { return iso; }
}

/// Is this UTC timestamp "today" in Cairo?
bool isCairoToday(String iso) {
  try {
    final d = _toCairo(iso);
    final now = tz.TZDateTime.now(_cairo);
    return d.year == now.year && d.month == now.month && d.day == now.day;
  } catch (_) { return false; }
}
