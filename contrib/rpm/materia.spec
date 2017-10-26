%define bdbv 4.8.30
%global selinux_variants mls strict targeted

%if 0%{?_no_gui:1}
%define _buildqt 0
%define buildargs --with-gui=no
%else
%define _buildqt 1
%if 0%{?_use_qt4}
%define buildargs --with-qrencode --with-gui=qt4
%else
%define buildargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:		materia
Version:	0.12.0
Release:	2%{?dist}
Summary:	Peer to Peer Cryptographic Currency

Group:		Applications/System
License:	MIT
URL:		https://materia.org/
Source0:	https://materia.org/bin/materia-core-%{version}/materia-%{version}.tar.gz
Source1:	http://download.oracle.com/berkeley-db/db-%{bdbv}.NC.tar.gz

Source10:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/debian/examples/materia.conf

#man pages
Source20:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/debian/manpages/materiad.1
Source21:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/debian/manpages/materia-cli.1
Source22:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/debian/manpages/materia-qt.1
Source23:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/debian/manpages/materia.conf.5

#selinux
Source30:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/rpm/materia.te
# Source31 - what about materia-tx and bench_materia ???
Source31:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/rpm/materia.fc
Source32:	https://raw.githubusercontent.com/materia/materia/v%{version}/contrib/rpm/materia.if

Source100:	https://upload.wikimedia.org/wikipedia/commons/4/46/Materia.svg

%if 0%{?_use_libressl:1}
BuildRequires:	libressl-devel
%else
BuildRequires:	openssl-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	miniupnpc-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	libevent-devel


Patch0:		materia-0.12.0-libressl.patch


%description
Materia is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of materias is carried out collectively by the network.

%if %{_buildqt}
%package core
Summary:	Peer to Peer Cryptographic Currency
Group:		Applications/System
Obsoletes:	%{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
%if 0%{?_use_qt4}
BuildRequires:	qt-devel
%else
BuildRequires:	qt5-qtbase-devel
# for /usr/bin/lrelease-qt5
BuildRequires:	qt5-linguist
%endif
BuildRequires:	protobuf-devel
BuildRequires:	qrencode-devel
BuildRequires:	%{_bindir}/desktop-file-validate
# for icon generation from SVG
BuildRequires:	%{_bindir}/inkscape
BuildRequires:	%{_bindir}/convert

%description core
Materia is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of materias is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Materia wallet, this is probably the package you want.
%endif


%package libs
Summary:	Materia shared libraries
Group:		System Environment/Libraries

%description libs
This package provides the materiaconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:	Development files for materia
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
materiaconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package server
Summary:	The materia daemon
Group:		System Environment/Daemons
Requires:	materia-utils = %{version}-%{release}
Requires:	selinux-policy policycoreutils-python
Requires(pre):	shadow-utils
Requires(post):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
Requires(postun):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
BuildRequires:	systemd
BuildRequires:	checkpolicy
BuildRequires:	%{_datadir}/selinux/devel/Makefile

%description server
This package provides a stand-alone materia-core daemon. For most users, this
package is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
materia-core node they use to connect to the network.

If you use the graphical materia-core client then you almost certainly do not
need this package.

%package utils
Summary:	Materia utilities
Group:		Applications/System

%description utils
This package provides several command line utilities for interacting with a
materia-core daemon.

The materia-cli utility allows you to communicate and control a materia daemon
over RPC, the materia-tx utility allows you to create a custom transaction, and
the bench_materia utility can be used to perform some benchmarks.

This package contains utilities needed by the materia-server package.


%prep
%setup -q
%patch0 -p1 -b .libressl
cp -p %{SOURCE10} ./materia.conf.example
tar -zxf %{SOURCE1}
cp -p db-%{bdbv}.NC/LICENSE ./db-%{bdbv}.NC-LICENSE
mkdir db4 SELinux
cp -p %{SOURCE30} %{SOURCE31} %{SOURCE32} SELinux/


%build
CWD=`pwd`
cd db-%{bdbv}.NC/build_unix/
../dist/configure --enable-cxx --disable-shared --with-pic --prefix=${CWD}/db4
make install
cd ../..

./autogen.sh
%configure LDFLAGS="-L${CWD}/db4/lib/" CPPFLAGS="-I${CWD}/db4/include/" --with-miniupnpc --enable-glibc-back-compat %{buildargs}
make %{?_smp_mflags}

pushd SELinux
for selinuxvariant in %{selinux_variants}; do
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
	mv materia.pp materia.pp.${selinuxvariant}
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
done
popd


%install
make install DESTDIR=%{buildroot}

mkdir -p -m755 %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/materiad %{buildroot}%{_sbindir}/materiad

# systemd stuff
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/materia.conf
d /run/materiad 0750 materia materia -
EOF
touch -a -m -t 201504280000 %{buildroot}%{_tmpfilesdir}/materia.conf

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/materia
# Provide options to the materia daemon here, for example
# OPTIONS="-testnet -disable-wallet"

OPTIONS=""

# System service defaults.
# Don't change these unless you know what you're doing.
CONFIG_FILE="%{_sysconfdir}/materia/materia.conf"
DATA_DIR="%{_localstatedir}/lib/materia"
PID_FILE="/run/materiad/materiad.pid"
EOF
touch -a -m -t 201504280000 %{buildroot}%{_sysconfdir}/sysconfig/materia

mkdir -p %{buildroot}%{_unitdir}
cat <<EOF > %{buildroot}%{_unitdir}/materia.service
[Unit]
Description=Materia daemon
After=syslog.target network.target

[Service]
Type=forking
ExecStart=%{_sbindir}/materiad -daemon -conf=\${CONFIG_FILE} -datadir=\${DATA_DIR} -pid=\${PID_FILE} \$OPTIONS
EnvironmentFile=%{_sysconfdir}/sysconfig/materia
User=materia
Group=materia

Restart=on-failure
PrivateTmp=true
TimeoutStopSec=120
TimeoutStartSec=60
StartLimitInterval=240
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF
touch -a -m -t 201504280000 %{buildroot}%{_unitdir}/materia.service
#end systemd stuff

mkdir %{buildroot}%{_sysconfdir}/materia
mkdir -p %{buildroot}%{_localstatedir}/lib/materia

#SELinux
for selinuxvariant in %{selinux_variants}; do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 SELinux/materia.pp.${selinuxvariant} %{buildroot}%{_datadir}/selinux/${selinuxvariant}/materia.pp
done

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/materia.ico %{buildroot}%{_datadir}/pixmaps/materia.ico
install -p share/pixmaps/nsis-header.bmp %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/nsis-wizard.bmp %{buildroot}%{_datadir}/pixmaps/
install -p %{SOURCE100} %{buildroot}%{_datadir}/pixmaps/materia.svg
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/materia16.png -w16 -h16
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/materia32.png -w32 -h32
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/materia64.png -w64 -h64
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/materia128.png -w128 -h128
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/materia256.png -w256 -h256
%{_bindir}/convert -resize 16x16 %{buildroot}%{_datadir}/pixmaps/materia256.png %{buildroot}%{_datadir}/pixmaps/materia16.xpm
%{_bindir}/convert -resize 32x32 %{buildroot}%{_datadir}/pixmaps/materia256.png %{buildroot}%{_datadir}/pixmaps/materia32.xpm
%{_bindir}/convert -resize 64x64 %{buildroot}%{_datadir}/pixmaps/materia256.png %{buildroot}%{_datadir}/pixmaps/materia64.xpm
%{_bindir}/convert -resize 128x128 %{buildroot}%{_datadir}/pixmaps/materia256.png %{buildroot}%{_datadir}/pixmaps/materia128.xpm
%{_bindir}/convert %{buildroot}%{_datadir}/pixmaps/materia256.png %{buildroot}%{_datadir}/pixmaps/materia256.xpm
touch %{buildroot}%{_datadir}/pixmaps/*.png -r %{SOURCE100}
touch %{buildroot}%{_datadir}/pixmaps/*.xpm -r %{SOURCE100}

# Desktop File - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/materia-core.desktop
[Desktop Entry]
Encoding=UTF-8
Name=Materia
Comment=Materia P2P Cryptocurrency
Comment[fr]=Materia, monnaie virtuelle cryptographique pair à pair
Comment[tr]=Materia, eşten eşe kriptografik sanal para birimi
Exec=materia-qt %u
Terminal=false
Type=Application
Icon=materia128
MimeType=x-scheme-handler/materia;
Categories=Office;Finance;
EOF
# change touch date when modifying desktop
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/applications/materia-core.desktop
%{_bindir}/desktop-file-validate %{buildroot}%{_datadir}/applications/materia-core.desktop

# KDE protocol - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/kde4/services
cat <<EOF > %{buildroot}%{_datadir}/kde4/services/materia-core.protocol
[Protocol]
exec=materia-qt '%u'
protocol=materia
input=none
output=none
helper=true
listing=
reading=false
writing=false
makedir=false
deleting=false
EOF
# change touch date when modifying protocol
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/kde4/services/materia-core.protocol
%endif

# man pages
install -D -p %{SOURCE20} %{buildroot}%{_mandir}/man1/materiad.1
install -p %{SOURCE21} %{buildroot}%{_mandir}/man1/materia-cli.1
%if %{_buildqt}
install -p %{SOURCE22} %{buildroot}%{_mandir}/man1/materia-qt.1
%endif
install -D -p %{SOURCE23} %{buildroot}%{_mandir}/man5/materia.conf.5

# nuke these, we do extensive testing of binaries in %%check before packaging
rm -f %{buildroot}%{_bindir}/test_*

%check
make check
pushd src
srcdir=. test/materia-util-test.py
popd
qa/pull-tester/rpc-tests.py -extended

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre server
getent group materia >/dev/null || groupadd -r materia
getent passwd materia >/dev/null ||
	useradd -r -g materia -d /var/lib/materia -s /sbin/nologin \
	-c "Materia wallet server" materia
exit 0

%post server
%systemd_post materia.service
# SELinux
if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
for selinuxvariant in %{selinux_variants}; do
	%{_sbindir}/semodule -s ${selinuxvariant} -i %{_datadir}/selinux/${selinuxvariant}/materia.pp &> /dev/null || :
done
%{_sbindir}/semanage port -a -t materia_port_t -p tcp 9616
%{_sbindir}/semanage port -a -t materia_port_t -p tcp 9617
%{_sbindir}/semanage port -a -t materia_port_t -p tcp 19616
%{_sbindir}/semanage port -a -t materia_port_t -p tcp 19617
%{_sbindir}/fixfiles -R materia-server restore &> /dev/null || :
%{_sbindir}/restorecon -R %{_localstatedir}/lib/materia || :
fi

%posttrans server
%{_bindir}/systemd-tmpfiles --create

%preun server
%systemd_preun materia.service

%postun server
%systemd_postun materia.service
# SELinux
if [ $1 -eq 0 ]; then
	if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
	%{_sbindir}/semanage port -d -p tcp 9616
	%{_sbindir}/semanage port -d -p tcp 9617
	%{_sbindir}/semanage port -d -p tcp 19616
	%{_sbindir}/semanage port -d -p tcp 19617
	for selinuxvariant in %{selinux_variants}; do
		%{_sbindir}/semodule -s ${selinuxvariant} -r materia &> /dev/null || :
	done
	%{_sbindir}/fixfiles -R materia-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/materia ] && \
		%{_sbindir}/restorecon -R %{_localstatedir}/lib/materia &> /dev/null || :
	fi
fi

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files core
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING materia.conf.example doc/README.md doc/bips.md doc/files.md doc/multiwallet-qt.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/materia-qt
%attr(0644,root,root) %{_datadir}/applications/materia-core.desktop
%attr(0644,root,root) %{_datadir}/kde4/services/materia-core.protocol
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.svg
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/materia-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files server
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING materia.conf.example doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_sbindir}/materiad
%attr(0644,root,root) %{_tmpfilesdir}/materia.conf
%attr(0644,root,root) %{_unitdir}/materia.service
%dir %attr(0750,materia,materia) %{_sysconfdir}/materia
%dir %attr(0750,materia,materia) %{_localstatedir}/lib/materia
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/materia
%attr(0644,root,root) %{_datadir}/selinux/*/*.pp
%attr(0644,root,root) %{_mandir}/man1/materiad.1*
%attr(0644,root,root) %{_mandir}/man5/materia.conf.5*

%files utils
%defattr(-,root,root,-)
%license COPYING
%doc COPYING materia.conf.example doc/README.md
%attr(0755,root,root) %{_bindir}/materia-cli
%attr(0755,root,root) %{_bindir}/materia-tx
%attr(0755,root,root) %{_bindir}/bench_materia
%attr(0644,root,root) %{_mandir}/man1/materia-cli.1*
%attr(0644,root,root) %{_mandir}/man5/materia.conf.5*



%changelog
* Fri Feb 26 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-2
- Rename Qt package from materia to materia-core
- Make building of the Qt package optional
- When building the Qt package, default to Qt5 but allow building
-  against Qt4
- Only run SELinux stuff in post scripts if it is not set to disabled

* Wed Feb 24 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-1
- Initial spec file for 0.12.0 release

# This spec file is written from scratch but a lot of the packaging decisions are directly
# based upon the 0.11.2 package spec file from https://www.ringingliberty.com/materia/
