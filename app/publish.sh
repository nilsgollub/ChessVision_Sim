#!/usr/bin/env bash
# Baut die Android-App „Brettfreunde“ auf dem Steuer-Container und legt sie ins F-Droid-Repo des
# Homelabs (http://apps.srv.local/fdroid/repo, Skript im Homeserver-Repo). Updates kommen über F-Droid.
# Die App ist eine Hülle: Startseite in www/ wählt den Server, dann lädt sie die Web-App von dort.
# Ein neues Frontend braucht also kein neues APK, nur Änderungen an www/ oder android/.
# Die Versionsnummer ist die Anzahl der Commits, deshalb vor dem Veröffentlichen committen.
# Aufruf: app/publish.sh
set -euo pipefail
cd "$(dirname "$0")"
if [ -n "$(git status --porcelain --untracked-files=no -- .)" ]; then
  echo "Erst committen: die Versionsnummer ist die Anzahl der Commits." >&2
  exit 1
fi
export ANDROID_HOME=/opt/android-sdk
[ -d node_modules ] || npm ci
npx cap sync android
cd android
[ -f local.properties ] || echo "sdk.dir=$ANDROID_HOME" > local.properties
./gradlew --no-daemon -q assembleRelease
/root/repos/Homeserver/scripts/fdroid-publish.sh app/build/outputs/apk/release/app-release.apk
