#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2018 Arnav Borborah
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# To install the requirements for this script, run:
#     pip install -r requirements.txt

"""
Unfollow all the users on Github who don't
care enough to follow you back.

Usage:
  github_unfollower.py <username> <password>
  github_unfollower.py (-h | --help | --version)

Arguments:
  username      The Github username to run this script for
  password      The password, or a personal access token with the
                follow/unfollow scope enabled, corresponding to 'username'

Options:
  -h --help     Show this screen and exit
  --version     Show version and exit
"""

from functools import lru_cache
import sys

from docopt import docopt
import requests


class AuthenticatedGithubUser:
    def __init__(self, username, github_pa_token):
        self._api_session = requests.Session()

        self._api_session.auth = (username, github_pa_token)

        # Verify whether everything is set up properly (auth, etc.)
        try:
            test_response = self._api_session.get(
                'https://api.github.com', timeout=5)
            test_response.raise_for_status()
        except requests.exceptions.HTTPError:
            # TODO: Properly handle errors here

            # 401 -> Not authenticated
            if test_response.status_code == 401:
                print('Error! 401 Unauthorized!')
            else:
                print(f'HTTP Error! (Response {test_response.status_code})')
            raise

    # TODO: A better name and API for this function
    def _followers_or_following(self, followers_or_following):
        """Returns either the user's followers or who they are following"""

        if followers_or_following not in ['followers', 'following']:
            raise ValueError('followers_or_following must be \'followers\''
                             'or \'following\'!')

        result = []

        current_url = f'https://api.github.com/user/{followers_or_following}?page=1'  # noqa

        while True:
            try:
                current_response = self._api_session.get(
                    current_url, timeout=5)
                current_response.raise_for_status()
            except requests.exceptions.HTTPError:
                # TODO: Properly handle HTTP error
                print(f'HTTP Error! (Response {current_response.status_code})')
                break

            result.extend(
                [follower['login'] for follower in current_response.json()])

            try:
                current_url = current_response.links['next']['url']
            except KeyError:
                break

        return result

    @property
    @lru_cache(maxsize=None)
    def followers(self):
        """"Get the user's followers"""

        return self._followers_or_following('followers')

    @property
    @lru_cache(maxsize=None)
    def following(self):
        """Get who the user is following"""

        return self._followers_or_following('following')

    # Not implemented because this function is not used for this script
    def follow(self, username):
        """Follow a user on Github"""
        raise NotImplementedError('This function is not used for this script!')

    def unfollow(self, username):
        """Unfollow a user on Github"""

        try:
            response = self._api_session.delete(
                f'https://api.github.com/user/following/{username}', timeout=5)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # TODO: Properly handle HTTP error
            print(f'HTTP Error! (Response {response.status_code})')

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._api_session.close()


def main():
    if len(sys.argv) == 1:  # Show help screen when no arguments are passed
        sys.argv.append('-h')

    cmd_arguments = docopt(__doc__, version='github_unfollower.py v1.0.0')

    unfollowed_users = []

    with AuthenticatedGithubUser(cmd_arguments['<username>'],
                                 cmd_arguments['<password>']) as github_user:

        for user in github_user.following:
            if user not in github_user.followers:
                github_user.unfollow(user)
                unfollowed_users.append(user)

    print(f'The following users were unfollowed: {unfollowed_users}')


if __name__ == '__main__':
    sys.exit(main())
