# Debian file creation

This folder contains the Debian DEB package creation set. To build a DEP 
package you need these packages installed:

* dh-virtualenv

```bash
$ sudo apt-get install debhelper dh-virtualenv 
```

If all is setup well, then a

```bash
$ dpkg-buildpackage -us -uc -b --buildinfo-option=-udist --changes-option=-udist
```
in the project root should create a deb package in the `dist` folder.

