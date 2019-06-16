# Debian file creation

This folder contains the Debian DEB package creation set. To build a DEB 
package you need these packages installed:

* debhelper
* dh-virtualenv

```bash
$ sudo apt-get install debhelper dh-virtualenv 
```

If all is setup well, then a
```bash
$ dpkg-buildpackage -us -uc -b --buildinfo-option=-udist --changes-option=-udist
```
in the **project root** should create a deb package in the `dist` folder.

Remark: you have to run `dpkg-buildpackage` outside of the Python3 virtual 
environment, if any is present.

