# github_unfollower.py

[![Build status](https://travis-ci.org/arnavb/github_unfollower.py.svg?branch=master)](https://travis-ci.org/arnavb/github_unfollower.py) ![Supported Python versions](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg) ![License](https://img.shields.io/github/license/arnavb/github_unfollower.py.svg)


A simply utility script which unfollows all the users on Github
who don't care enough to follow you back.

## Install

This script requires at least Python 3.6. To install it, all you have
to do is:

1. Download [`github_unfollower.py`](https://raw.githubusercontent.com/arnavb/github_unfollower.py/master/github_unfollower.py) and [`requirements.txt`](https://raw.githubusercontent.com/arnavb/github_unfollower.py/master/requirements.txt)
   to a folder of your choice.
2. Create a virtualenv (not necessary, but recommended).
3. Run `pip install -r requirements.txt`.

## Run

This script can be run as follows:

```
Usage:
  github_unfollower.py <username> <password>
  github_unfollower.py (-h | --help | --version)
```

More information can be obtained by running
`github_unfollower.py --help`.
