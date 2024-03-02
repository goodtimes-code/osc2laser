#!/bin/Bash
venv/bin/pyinstaller --onefile --paths=venv/lib/python3.12/site-packages main.py

mkdir -p dist/osc2laser.app/Contents/MacOS

mv dist/main dist/osc2laser.app/Contents/MacOS/osc2laser
chmod +x dist/osc2laser.app/Contents/MacOS/osc2laser

cp config_laser1.txt dist/osc2laser.app/Contents/MacOS/
cp libHeliosDacAPI.so dist/osc2laser.app/Contents/MacOS/

cat > dist/osc2laser.app/Contents/Info.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>osc2laser</string>
    <key>CFBundleExecutable</key>
    <string>osc2laser</string>
    <key>CFBundleIdentifier</key>
    <string>tchnology.goodtimes.osc2laser</string>
    <key>CFBundleName</key>
    <string>osc2laser</string>
    <key>CFBundleVersion</key>
    <string>1.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

# hdiutil create -volname "osc2laser" -srcfolder dist/osc2laser.app -ov -format UDZO dist/osc2laser.dmg

pkgbuild --component dist/osc2laser.app --install-location /Applications dist/osc2laser.pkg

# Otherwise the .pkg won't install to /Applications
rm -Rf dist/osc2laser.app