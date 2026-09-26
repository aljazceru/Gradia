Name:           gradia
Version:        1.13.0
Release:        1%{?dist}
Summary:        Screenshot beautifier for GNOME

License:        GPL-3.0-or-later
URL:            https://github.com/AlexanderVanhee/Gradia
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  make
BuildRequires:  meson >= 1.0.0
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  blueprint-compiler
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk4) >= 4.12.0
BuildRequires:  pkgconfig(libadwaita-1) >= 1.5.0
BuildRequires:  pkgconfig(gtksourceview-5)
BuildRequires:  pkgconfig(pygobject-3.0) >= 3.48.0
BuildRequires:  desktop-file-utils
BuildRequires:  appstream

# lib* deps are intentional: PyGI loads their typelibs at runtime, no ELF link exists
Requires:       gtk4%{?_isa}
Requires:       libadwaita%{?_isa}
Requires:       gtksourceview5%{?_isa}
Requires:       libportal%{?_isa}
Requires:       libsoup3%{?_isa}
Requires:       python3-gobject
Requires:       python3-cairo
Requires:       python3-pillow
Requires:       python3-pytesseract

# OCR works out of the box when tesseract and a language pack are present
Recommends:     tesseract%{?_isa}
Recommends:     tesseract-osd
Recommends:     tesseract-langpack-eng

%description
Gradia makes screenshots ready for the world: it quickly edits images to fix
transparent or oddly sized screenshots and offers options to enhance their
overall appearance, with backgrounds, gradients, padding, drawing tools and
text extraction (OCR) built in.

%prep
%autosetup -n Gradia-%{version}

%build
%meson -Denable-ocr=true
%meson_build

%install
%meson_install
%find_lang gradia

# meson installs the launcher r-xr-xr-x; RPM expects 755
chmod 755 %{buildroot}%{_bindir}/gradia
# C source is not needed at runtime (shipped prebuilt as libgradient_gen.so)
rm %{buildroot}%{_datadir}/gradia/gradia/graphics/gradient_gen.c

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/be.alexandervanhee.gradia.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/be.alexandervanhee.gradia.metainfo.xml

%post
if [ $1 -gt 1 ] || [ $1 -eq 1 ]; then
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :
  gtk4-update-icon-cache -q -t -f %{_datadir}/icons/hicolor &>/dev/null || :
  update-desktop-database -q %{_datadir}/applications &>/dev/null || :
fi

%postun
if [ $1 -eq 0 ]; then
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :
  gtk4-update-icon-cache -q -t -f %{_datadir}/icons/hicolor &>/dev/null || :
  update-desktop-database -q %{_datadir}/applications &>/dev/null || :
fi

%files -f gradia.lang
%license COPYING
%doc README.md
%{_bindir}/gradia
%{_datadir}/gradia/
# compiled gradient module (FHS: arch-specific code lives under libdir)
%{_libdir}/gradia/
%{_datadir}/applications/be.alexandervanhee.gradia.desktop
%{_metainfodir}/be.alexandervanhee.gradia.metainfo.xml
%{_datadir}/dbus-1/services/be.alexandervanhee.gradia.service
%{_datadir}/glib-2.0/schemas/be.alexandervanhee.gradia.gschema.xml
%ghost %attr(0644,root,root) %{_datadir}/glib-2.0/schemas/gschemas.compiled
%{_datadir}/icons/hicolor/scalable/apps/be.alexandervanhee.gradia.svg
%{_datadir}/icons/hicolor/symbolic/apps/be.alexandervanhee.gradia-symbolic.svg
%ghost %attr(0644,root,root) %{_datadir}/icons/hicolor/icon-theme.cache
# Bundled font (Caveat, OFL) shipped with the app, auto-discovered by fontconfig
%{_datadir}/fonts/Caveat-VariableFont_wght.ttf
%{_datadir}/fonts/LICENSE-OFL.txt

%changelog
* Thu Oct 23 2025 Gradia maintainers <https://github.com/AlexanderVanhee/Gradia> - 1.13.0-1
- Initial RPM package for Gradia 1.13.0
