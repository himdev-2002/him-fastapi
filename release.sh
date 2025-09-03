#!/bin/bash
# Script otomatis buat release di GitHub
# Usage: ./release.sh v1.0.0 "Catatan release"

set -e

VERSION=$1
NOTES=$2

if [ -z "$VERSION" ] || [ -z "$NOTES" ]; then
  echo "Usage: $0 <version> <release-notes>"
  echo "Example: $0 v1.0.0 'Fitur baru dan perbaikan bug'"
  exit 1
fi

echo "📌 Membuat tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION"

echo "⬆️ Push tag ke origin..."
git push origin "$VERSION"

echo "🚀 Membuat release di GitHub..."
gh release create "$VERSION" --title "Release $VERSION" --notes "$NOTES"

echo "✅ Release $VERSION berhasil dibuat!"
