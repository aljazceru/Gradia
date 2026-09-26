#!/bin/bash
# Build a Gradia RPM from this git checkout (Fedora 43+).
#
# Usage:
#   ./packaging/rpm/build-rpm.sh            # build SRPM + RPM
#   ./packaging/rpm/build-rpm.sh --deps     # also install build deps first (needs sudo)
#
# The RPM is built in ~/rpmbuild and ends up in ~/rpmbuild/RPMS/<arch>/.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
SPEC=packaging/rpm/gradia.spec

VERSION=$(sed -n "s/^ *version: '\([^']*\)',$/\1/p" meson.build | head -1)
if [[ -z "$VERSION" ]]; then
    echo "Could not parse project version from meson.build" >&2
    exit 1
fi

if [[ "${1:-}" == "--deps" ]]; then
    sudo dnf builddep -y "$SPEC"
fi

command -v rpmbuild >/dev/null || {
    echo "rpmbuild not found. Install it with: sudo dnf install rpm-build rpmdevtools" >&2
    exit 1
}

if command -v rpmdev-setuptree >/dev/null; then
    rpmdev-setuptree
else
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
fi
TARBALL_PATH="$HOME/rpmbuild/SOURCES/${TARBALL}"

echo "==> Creating source tarball ${TARBALL} (includes uncommitted changes)"
# Tar the worktree (tracked + new, non-ignored files) so uncommitted
# changes are included, matching the Gradia-%{version} directory the spec expects.
# (Use "git ls-files" only if you prefer committed state.)
git ls-files --cached --others --exclude-standard -z | tar --null -czf "${TARBALL_PATH}" \
    --transform "s,^,Gradia-${VERSION}/," -T -

cp "$SPEC" ~/rpmbuild/SPECS/

echo "==> Building RPM"
rpmbuild -ba ~/rpmbuild/SPECS/gradia.spec

echo
echo "==> Done. Artifacts:"
ls -1 ~/rpmbuild/RPMS/*/gradia-${VERSION}-*.rpm ~/rpmbuild/SRPMS/gradia-${VERSION}-*.rpm
