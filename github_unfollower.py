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
from typing import List, Optional

from docopt import docopt
import requests


class GithubHTTPError(RuntimeError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self._status_code = status_code

    @property
    def status_code(self) -> int:
        return self._status_code


class AuthenticatedGithubUser:
    def __init__(self, username: str, password: str) -> None:
        self._api_session = requests.Session()

        self._api_session.auth = (username, password)

    def _handle_HTTP_errors(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise GithubHTTPError(
                f'HTTP Error! Status code: {response.status_code}',
                response.status_code) from http_error

    # TODO: A better name and API for this function
    def _followers_or_following(self, followers_or_following: str) -> List[str]:  # noqa
        """Returns either the user's followers or who they are following"""

        if followers_or_following not in ['followers', 'following']:
            raise ValueError('followers_or_following must be either '
                             '\'followers\' or \'following\'!')

        result = []

        current_url = f'https://api.github.com/user/{followers_or_following}?page=1'  # noqa

        while True:
            current_response = self._api_session.get(
                current_url, timeout=5)
            self._handle_HTTP_errors(current_response)

            result += [
                follower['login'] for follower in current_response.json()]

            # Traverse Github pagination through link headers
            try:
                current_url = current_response.links['next']['url']
            except KeyError:
                break

        return result

    @property
    @lru_cache(maxsize=None)
    def followers(self) -> List[str]:
        """"Get the user's followers"""

        return self._followers_or_following('followers')

    @property
    @lru_cache(maxsize=None)
    def following(self) -> List[str]:
        """Get who the user is following"""

        return self._followers_or_following('following')

    # Not implemented because this function is not used for this script
    def follow(self, username: str) -> None:
        """Follow a user on Github"""
        pass

    def unfollow(self, username: str) -> None:
        """Unfollow a user on Github"""

        response = self._api_session.delete(
            f'https://api.github.com/user/following/{username}', timeout=5)
        self._handle_HTTP_errors(response)

    def __enter__(self) -> 'AuthenticatedGithubUser':
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self._api_session.close()


def main(passed_argv: List[str]) -> Optional[int]:
    argv = passed_argv[1:]
    if len(argv) == 1:  # Show help screen when no arguments are passed
        argv.append('-h')

    cmd_arguments = docopt(__doc__, argv=argv,
                           version='github_unfollower.py v1.0.0')

    unfollowed_users = []

    with AuthenticatedGithubUser(cmd_arguments['<username>'],
                                 cmd_arguments['<password>']) as github_user:
        try:
            for user in github_user.following:
                if user not in github_user.followers:
                    github_user.unfollow(user)
                    unfollowed_users.append(user)

        except GithubHTTPError as github_http_error:
            if github_http_error.status_code == 401:
                print('Error! The Github credentials you entered were '
                      'incorrect.')
            elif github_http_error.status_code == 404:
                print('Error! No user was found with the username '
                      f'\'{cmd_arguments["username"]}\'!')
            else:
                print(github_http_error)

            return 1

    print(f'The following users were unfollowed: {unfollowed_users}')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
