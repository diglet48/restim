#!/usr/bin/env bash
# build-mac.sh
#
# Build a standalone Restim.app for macOS and optionally install it to
# /Applications. Run this from the root of a Restim checkout:
#
#     git clone https://github.com/diglet48/restim.git
#     cd restim
#     ./build-mac.sh
#
# Flags:
#     --no-install    Build only; don't copy to /Applications.
#     --keep-venv     Reuse existing venv/ instead of recreating it.
#
# Requirements: macOS, Xcode Command Line Tools (git, codesign),
# Python 3.10 or newer.
#
# ---------------------------------------------------------------------
# NOTES FOR MAINTAINERS
#
# This script works around three issues that could be fixed upstream:
#
# 1. restim-macos.spec doesn't collect the ahrs package's data files.
#    At runtime the app fails with FileNotFoundError on WMM.COF. Fix
#    would be adding `datas=collect_data_files('ahrs')` (with the
#    appropriate import) to the Analysis() call in the spec file.
#    Until that's fixed, this script copies ahrs datas in post-build.
#
# 2. qt_ui/mainwindow.py calls logging.basicConfig('restim.log') with
#    a relative path. Finder launches apps with CWD='/', which is
#    read-only on modern macOS, so the app crashes on startup when
#    launched by double-click (terminal launches work because CWD is
#    writable). Fix would be using an absolute path under
#    ~/Library/Logs/Restim/ or similar. Until then, this script
#    installs a tiny shell wrapper that cd's to a writable dir before
#    exec'ing the real binary.
#
# 3. restim-macos.spec doesn't set CFBundleDisplayName, so Finder
#    shows the bundle filename. This script patches it post-build.
# ---------------------------------------------------------------------

set -euo pipefail

# --- Config ---
BUILD_APP_NAME="restim.app"      # what pyinstaller emits
APP_NAME="Restim.app"             # final bundle name
DISPLAY_NAME="Restim"             # Finder/Dock/Spotlight label
APP_BINARY="restim_app"           # real executable inside the bundle
WRAPPER_NAME="restim_launcher"    # CWD-fixing wrapper (workaround #2)
INSTALL_DIR="/Applications"
AHRS_REPO_URL="https://github.com/Mayitzin/ahrs.git"

# --- Flags ---
DO_INSTALL=1
KEEP_VENV=0
for arg in "$@"; do
  case "$arg" in
    --no-install) DO_INSTALL=0 ;;
    --keep-venv)  KEEP_VENV=1 ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown flag: $arg" >&2
      exit 2
      ;;
  esac
done

# --- Sanity: must be run from a Restim checkout ---
if [[ ! -f "restim-macos.spec" ]] || [[ ! -f "requirements.txt" ]]; then
  echo "ERROR: run this from the root of a Restim checkout."
  echo "       Expected restim-macos.spec and requirements.txt in $(pwd)."
  exit 1
fi

# --- Prereqs ---
echo "==> Checking prerequisites..."
for cmd in git python3 codesign; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd not found. Install Xcode Command Line Tools:"
    echo "       xcode-select --install"
    exit 1
  fi
done
PY_OK=$(python3 -c 'import sys; print(1 if sys.version_info >= (3,10) else 0)')
if [[ "$PY_OK" != "1" ]]; then
  PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  echo "ERROR: Python 3.10+ required, found $PY_VER."
  exit 1
fi

# --- Virtual environment ---
if [[ "$KEEP_VENV" == "1" ]] && [[ -d "venv" ]]; then
  echo "==> Reusing existing venv/"
else
  echo "==> Creating virtual environment..."
  rm -rf venv
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller

# --- Workaround #1 (pre-build half): verify ahrs data files exist ---
# Some ahrs wheel releases have shipped without the .COF data files.
# Catch that before the build and reinstall from git source if needed.
echo "==> Verifying ahrs data files in venv..."
AHRS_SRC=$(python -c 'import ahrs, os; print(os.path.dirname(ahrs.__file__))')
if [[ ! -f "$AHRS_SRC/utils/WMM2025/WMM.COF" ]]; then
  echo "    WMM.COF missing from pip-installed ahrs. Reinstalling from git..."
  pip uninstall --quiet --yes ahrs
  pip install --quiet "git+${AHRS_REPO_URL}"
  AHRS_SRC=$(python -c 'import ahrs, os; print(os.path.dirname(ahrs.__file__))')
  if [[ ! -f "$AHRS_SRC/utils/WMM2025/WMM.COF" ]]; then
    echo "ERROR: WMM.COF still missing after git reinstall of ahrs."
    exit 1
  fi
fi

# --- Build ---
echo "==> Building .app bundle (this is the slow part)..."
rm -rf build dist
pyinstaller restim-macos.spec --clean --noconfirm

if [[ ! -d "dist/$BUILD_APP_NAME" ]]; then
  echo "ERROR: Build finished but dist/$BUILD_APP_NAME not found."
  ls -la dist/ || true
  exit 1
fi
mv "dist/$BUILD_APP_NAME" "dist/$APP_NAME"

# --- Workaround #1 (post-build half): copy ahrs datas into bundle ---
echo "==> Copying ahrs package data files into bundle..."
AHRS_DST_ABS="$(pwd)/dist/$APP_NAME/Contents/Frameworks/ahrs"
mkdir -p "$AHRS_DST_ABS"
pushd "$AHRS_SRC" >/dev/null
find . -type f ! -name '*.py' ! -name '*.pyc' -print0 | while IFS= read -r -d '' f; do
  mkdir -p "$AHRS_DST_ABS/$(dirname "$f")"
  cp "$f" "$AHRS_DST_ABS/$f"
done
popd >/dev/null
if [[ ! -f "dist/$APP_NAME/Contents/Frameworks/ahrs/utils/WMM2025/WMM.COF" ]]; then
  echo "ERROR: WMM.COF missing from bundle after copy."
  exit 1
fi

# --- Workaround #2: CWD-fixing wrapper ---
echo "==> Installing launcher wrapper..."
WRAPPER_PATH="dist/$APP_NAME/Contents/MacOS/$WRAPPER_NAME"
cat > "$WRAPPER_PATH" <<'EOF'
#!/bin/bash
# Restim writes restim.log to CWD. Finder launches apps with CWD='/',
# which is read-only on modern macOS, so we cd somewhere writable first.
LOG_DIR="${HOME}/Library/Logs/Restim"
mkdir -p "$LOG_DIR"
cd "$LOG_DIR"
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/restim_app" "$@"
EOF
chmod +x "$WRAPPER_PATH"

# --- Workaround #3: Info.plist display name + point exe at wrapper ---
echo "==> Patching Info.plist..."
PLIST="dist/$APP_NAME/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable $WRAPPER_NAME" "$PLIST"

# --- Re-sign ---
# Modifying a bundle invalidates PyInstaller's signature. On Apple
# Silicon an invalid signature means Finder silently refuses to launch
# (direct terminal execution still works). Ad-hoc re-sign fixes this.
echo "==> Re-signing bundle (ad-hoc)..."
codesign --force --deep --sign - "dist/$APP_NAME"
codesign --verify --deep --strict "dist/$APP_NAME"

echo ""
echo "Build complete: dist/$APP_NAME"

# --- Install (optional) ---
if [[ "$DO_INSTALL" == "1" ]]; then
  echo "==> Installing to $INSTALL_DIR..."
  rm -rf "$INSTALL_DIR/$APP_NAME" "$INSTALL_DIR/$BUILD_APP_NAME"
  cp -R "dist/$APP_NAME" "$INSTALL_DIR/"
  xattr -cr "$INSTALL_DIR/$APP_NAME" 2>/dev/null || true
  touch "$INSTALL_DIR/$APP_NAME"
  /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister \
    -f "$INSTALL_DIR/$APP_NAME" 2>/dev/null || true
  killall Dock Finder 2>/dev/null || true

  echo ""
  echo "Installed: $INSTALL_DIR/$APP_NAME"
  echo "Launch from Spotlight, Launchpad, or Applications."
  echo "Logs: ~/Library/Logs/Restim/restim.log"
else
  echo "(skipping install; pass without --no-install to copy to $INSTALL_DIR)"
fi