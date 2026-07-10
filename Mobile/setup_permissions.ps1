# Keep It Green — camera permission setup for the QR scanner (mobile_scanner).
# Run this ONCE, right after `flutter create .`, then `flutter pub get && flutter run`.
#
#   powershell -ExecutionPolicy Bypass -File setup_permissions.ps1

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

function Save-NoBom([string]$path, [string]$text) {
    [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))
}

# ---------------- Android ----------------
$manifest = Join-Path $root 'android/app/src/main/AndroidManifest.xml'
if (Test-Path $manifest) {
    $c = Get-Content $manifest -Raw
    if ($c -notmatch 'android\.permission\.CAMERA') {
        $c = [regex]::Replace($c, '(<manifest\b[^>]*>)',
            "`$1`r`n    <uses-permission android:name=""android.permission.CAMERA"" />", 1)
        Save-NoBom $manifest $c
        Write-Host '[OK] Added CAMERA permission to AndroidManifest.xml' -ForegroundColor Green
    } else {
        Write-Host '[--] CAMERA permission already present'
    }
} else {
    Write-Host "[!!] AndroidManifest not found - run 'flutter create .' first" -ForegroundColor Yellow
}

# ---------------- iOS ----------------
$plist = Join-Path $root 'ios/Runner/Info.plist'
if (Test-Path $plist) {
    $c = Get-Content $plist -Raw
    if ($c -notmatch 'NSCameraUsageDescription') {
        $insert = "    <key>NSCameraUsageDescription</key>`r`n" +
                  "    <string>Scan the QR on the recycling machine to start a session.</string>`r`n" +
                  "</dict>`r`n</plist>"
        $c = [regex]::Replace($c, '</dict>\s*</plist>\s*$', $insert)
        Save-NoBom $plist $c
        Write-Host '[OK] Added NSCameraUsageDescription to Info.plist' -ForegroundColor Green
    } else {
        Write-Host '[--] NSCameraUsageDescription already present'
    }
} else {
    Write-Host '[--] iOS Info.plist not found (skip if not targeting iOS)'
}

Write-Host ''
Write-Host 'Done. mobile_scanner needs Android minSdk 21+ (Flutter default is fine).'
Write-Host 'Next:  flutter pub get   then   flutter run'
