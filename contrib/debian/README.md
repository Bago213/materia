
Debian
====================
This directory contains files used to package materiad/materia-qt
for Debian-based Linux systems. If you compile materiad/materia-qt yourself, there are some useful files here.

## materia: URI support ##


materia-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install materia-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your materia-qt binary to `/usr/bin`
and the `../../share/pixmaps/materia128.png` to `/usr/share/pixmaps`

materia-qt.protocol (KDE)

