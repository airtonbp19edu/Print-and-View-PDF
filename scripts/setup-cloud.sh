#!/usr/bin/env bash
# Local runtime overlay for the Debian 13 cloud image; no system installation.
set -euo pipefail
runtime_dir=/workspace/.print-view-runtime
mkdir -p "$runtime_dir/apt/state/lists/partial" "$runtime_dir/apt/cache/archives/partial" "$runtime_dir/apt/log"
setup_dir="$(mktemp -d /tmp/print-view-apt-XXXXXX)"
trap 'rm -rf -- "$setup_dir"' EXIT
mkdir -p "$setup_dir/parts" "$setup_dir/sources"
cat > "$setup_dir/debian.sources" <<'EOF'
Types: deb
URIs: https://deb.debian.org/debian
Suites: trixie
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
cat > "$setup_dir/apt.conf" <<EOF
Dir::Etc::parts "$setup_dir/parts";
Dir::Etc::sourcelist "$setup_dir/debian.sources";
Dir::Etc::sourceparts "$setup_dir/sources";
Dir::State "$runtime_dir/apt/state";
Dir::Cache "$runtime_dir/apt/cache";
Dir::Log "$runtime_dir/apt/log";
APT::Sandbox::User "$(id -un)";
EOF
cd "$runtime_dir"
APT_CONFIG="$setup_dir/apt.conf" apt-get update
APT_CONFIG="$setup_dir/apt.conf" apt-get download python3-gi-cairo=3.50.0-4+b1 7zip=25.01+dfsg-1~deb13u2
dpkg-deb --extract python3-gi-cairo_3.50.0-4+b1_amd64.deb gi-cairo
dpkg-deb --extract 7zip_25.01+dfsg-1~deb13u2_amd64.deb 7zip
/usr/bin/python3 - <<'PY'
import gi
from pathlib import Path
overlay = Path('/workspace/.print-view-runtime/gi-cairo/usr/lib/python3/dist-packages/gi')
for source in Path(gi.__path__[0]).iterdir():
    target = overlay / source.name
    if not target.exists():
        target.symlink_to(source)
PY
PYTHONPATH="$runtime_dir/gi-cairo/usr/lib/python3/dist-packages" /usr/bin/python3 - <<'PY'
import gi
gi.require_foreign('cairo')
import cairo, PIL, cryptography
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
print('GTK/Cairo and Python PDF runtime available')
PY
"$runtime_dir/7zip/usr/lib/7zip/7z" i >/dev/null
