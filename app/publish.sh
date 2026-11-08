#!/usr/bin/env bash
# Baut die Android-App „Brettfreunde“ (Release-APK).
# Die App ist eine Hülle: Die Startseite in www/ wählt den Server, dann lädt sie die Web-App von dort.
# Ein neues Frontend braucht also kein neues APK, nur Änderungen an www/ oder android/.
# Die Versionsnummer ist die Anzahl der Commits, deshalb vor dem Veröffentlichen committen.
#
# Optional: app/publish.env (nicht im Repo) mit
#   PUBLISH_CMD=/pfad/zu/eigenem/skript.sh   # bekommt den APK-Pfad, z.B. zum Ablegen in ein F-Droid-Repo
# Aufruf: app/publish.sh
set -euo pipefail
cd "$(dirname "$0")"
if [ -n "$(git status --porcelain --untracked-files=no -- .)" ]; then
  echo "Erst committen: die Versionsnummer ist die Anzahl der Commits." >&2
  exit 1
fi
[ -f publish.env ] && . ./publish.env
export ANDROID_HOME=${ANDROID_HOME:-/opt/android-sdk}
[ -d node_modules ] || npm ci
npx cap sync android
cd android
[ -f local.properties ] || echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew --no-daemon -q assembleRelease
APK=$PWD/app/build/outputs/apk/release/app-release.apk
echo "APK: $APK"
if [ -n "${PUBLISH_CMD:-}" ]; then
  "$PUBLISH_CMD" "$APK"
fi
