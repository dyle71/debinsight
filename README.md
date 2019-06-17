# debinsight

A tool collecting installed files, dependency and reverse dependency 
information by the help of `apt-cache` and similar tools on Debian and 
dependent operating systems.

This is a mere exercise for me making a Python 3 tool with click, uvloop, 
async, await and venv which bears _some_ benefit for the user. It is not intended
to supersede a standard tool of the operating system.

The idea is to show all the installed files of an installed package. It does also
allow for dependency-walk and reverse-dependencies. However, as this is just an
exercise for me, I didn't make any optimizations and therefore adding both options
might get somehow excessive for big packages.

## Usage

```bash
$ debinsight --help
Usage: debinsight [OPTIONS] [TARGET]...

  debinsight is collects package information by examining the dependency and
  reverse dependencies of packages installed in the Debian (or Ubuntu and
  derivates) operating systems. On default it prints the current stats of a
  package and all files the package installs.

  TARGET can be either a package name or a file on the local system.

  E.g.:
      TARGET = openssl ............ start with the openssl package installed.
      TARGET = /usr/bin/openssl ... start with the package containing which had
                                    installed the file "/usr/bin/openssl".

Options:
  --no-color            Turn off color output.
  --no-depend           Turn off output for dependencies.
  --no-rdepend          Turn off output for reverse dependencies.
  --no-files            Turn off list of files.
  -v, --version         Show version and exit.
  --json PATH           Dump found information as json into a file.
  --follow-depend       Follow dependency graph (use with caution).
  --follow-rdepend      Follow reverse dependency graph (use with caution).
  --drop-not-installed  Do not list not installed packages.
  -h, --help            Show this message and exit.
```

To see what is totally installed by bash:

```bash
$ debinsight --follow-depend --drop-not-installed bash
Found apt-cache: /usr/bin/apt-cache
Found dpkg-query: /usr/bin/dpkg-query
Searching for bash...
Package bash found.
bash: collectign status information...
bash: collecting reverse dependencies...
bash: collecting installed files...
base-files: collectign status information...
base-files: collecting reverse dependencies...
base-files: collecting installed files...
debianutils: collectign status information...
debianutils: collecting reverse dependencies...
debianutils: collecting installed files...
libc6: collectign status information...
libc6: collecting reverse dependencies...
libc6: collecting installed files...
libgcc1: collectign status information...
libgcc1: collecting reverse dependencies...
libgcc1: collecting installed files...
gcc-9-base: collectign status information...
gcc-9-base: collecting reverse dependencies...
gcc-9-base: collecting installed files...
=== Collecting information done. ===
bash
        Installed version: 5.0-3ubuntu1.1
        Dependencies: 
                base-files (>= 2.1.12)
                debianutils (>= 2.15)
        Reverse dependencies: 
        Installed files: 
                /bin/bash [1166912 Bytes]
                /etc/bash.bashrc [2319 Bytes]
                /etc/skel/.bash_logout [220 Bytes]
...
gcc-9-base
        Installed version: 9.1.0-2ubuntu2~19.04
        Reverse dependencies: 
                libgcc1 [installed]
        Installed files: 
                /usr/share/doc/gcc-9-base/README.Debian.amd64.gz [3577 Bytes]
                /usr/share/doc/gcc-9-base/TODO.Debian [1653 Bytes]
                /usr/share/doc/gcc-9-base/changelog.Debian.gz [1207 Bytes]
                /usr/share/doc/gcc-9-base/copyright [62516 Bytes]
        Total amount of bytes of installed files: 68953 Bytes
Total sum of bytes installed by these packages: 13867563 Bytes
```

The same can be achieved by
```bash
$ debinsight --follow-depend --drop-not-installed /bin/bash
```
With this, the tool searches for the package which installed the given file.

Beware, a `debsight --follow-depend libreoffice` will you collect all packages and files which
are pulled in by the libreoffice package. This can get very, very broad.


This tool does only check, what is installed on the system. It does not take any packages into 
account (dependencies or reverse dependencies) which are available on some repositories but not 
actually installed on the system at hand.


## Development

This package is meant to be developed within a Python3 virtual environment.
Therefore after cloning, create a virtual environment and activate it.
```bash
$ cd debinsight
$ python3 -m venv venv
...
$ source venv/bin/activate
...
```
Also do not forget to include the pip3 packages in the virtual environment.
```bash
$ cd debinsight
$ source venv/bin/activate
...
$ venv/bin/pip3 install -r requirements.txt
```

## Packaging

The folder `debian` contains all necessary info for creating a Debian 
package. Note: the Debian package will create a Python3 virtual environment
on the installed host too.


---

Oliver Maurhart, 2019

