[![Build Status](https://travis-ci.org/rbrito/edx-dl.png?branch=master)](https://travis-ci.org/rbrito/edx-dl)
[![Coverage Status](https://coveralls.io/repos/rbrito/edx-dl/badge.png)](https://coveralls.io/r/rbrito/edx-dl)

# edx-dl

`edx-dl` is a simple tool to download video lectures (and, optionally,
subtitles) from edx-based sites, like edX.org, MongoDB.com or Stanford's
online platforms.

It is written in Python and requires only a few modules (see the
Installation section below for the requirements).  It is written to be
platform independent and should work fine under any Unix, Windows or MacOS X
system, provided the dependencies are met.


# Installation

## The recommended (supported) way

The edx-dl program requires a Python interpreter (either version 2.x with
x >= 6 or version 3.x) and some dependencies.

After obtaining the source code for `edx-dl` (either via a clone of the
repository or via a tarball), you have to install the dependencies.  The
recommended way of installing them is to issue:

    pip install -r requirements.txt


## Doing it on your own (a.k.a. the unsupported way)

If you want to install the dependencies on your own (e.g., to have a minimal
set of dependencies), you can simply install a sufficiently recent version
of [BeautifulSoup 4][0]. Any version starting with 4.1.3 should work. The
second dependency is [youtube-dl][1].

If you use a Linux distribution derived from Debian, then the package
`python-bs4` should work, as long as it is version is >= 4.1.3.

Similarly, you can install the package `youtube-dl` in a Debian-based
distribution.  Note that it is *always* recommended to use the most recent
version of `youtube-dl`, as Youtube frequently changes the layout of the
site and `youtube-dl` is constantly updated to take such changes into
account.

The most recent version of `youtube-dl` in Debian is found in
[the Debian archive][2].

If you don't use the recommended method above of installing the dependencies
(i.e., using `pip`), then you should use the packages from the Debian
archive, and not those from Ubuntu, Linux Mint or other Debian-derived
distributions, as they are frequently *much* older than the one in Debian.

**Remark:** The package in Debian is maintained by @rbrito one of the
developers of `edx-dl`.

Otherwise, keep your `youtube-dl` version updated with the use of:

    youtube-dl --update


[0]: http://www.crummy.com/software/BeautifulSoup/
[1]: https://github.com/rg3/youtube-dl
[2]: http://packages.debian.org/sid/youtube-dl


# Usage

FIXME: This part is completely outdated and should be updated to reflect the
changes of the `master` branch.

## Needed information

For using the script, you will have to inform the script of 3 pieces of
information:

1. The URL of the class that you want to download the videos from.
2. The e-mail address that you used to register with the site. For the sake
   of the examples, we will assume that it is `user@example.com`.
3. Your password for that site. For the sake of the examples, we will assume
   that it is `123456`.

The URL of the class is one of the most important points. It should look
like:

    https://courses.edx.org/courses/BerkeleyX/CS191x/2013_Spring/courseware/


## The actual usage

Regardless of if you are using Python 2 or Python 3, you can simply use:

    python edx-dl -u user@user.com -p 123456 https://courses.edx.org/courses/BerkeleyX/CS191x/2013_Spring/courseware/


## The result

In the current implementation (which is going to change soon), you will get
a long stream of "garbage looking" lines, each with 11 characters, which are
the IDs of the videos on Youtube.com. You should pass them as arguments to
`youtube-dl` to get the videos actually downloaded.

FIXME: Explain this better.

----

# Authors

* @emadshaaban92
* @iemejia
* @rbrito
* @shk3

And many other contributors.
