# (c) 2019 Juniper Networks.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
---
author: Michael Tucker (@mtucker502)
httpapi : junos_space
short_description: HttpApi Plugin for Junos Space
description:
  - This HttpApi plugin provides methods to connect to Junos Space
    applications over a HTTPS-based api.
version_added: "2.9"
"""

import json

from ansible.module_utils.basic import to_text
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.plugins.httpapi import HttpApiBase
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.six import PY3


BASE_HEADERS = {
    'Content-Type': 'application/json',
}

class HttpApi(HttpApiBase):
    def handle_httperror(self, exc):
        return exc
    def logout(self):
        logout_path = '/api/space/user-management/logout'
        user_headers = {"Accept": "application/vnd.net.juniper.space.user-management.user-ref+json;version=1"}
        response, dummy = self.send_request(
            request_method='POST',
            path=logout_path,
            headers=user_headers
        )

        # Clean up tokens
        self.connection._auth = None

    def login(self, username, password):
        if username and password:
            login_path = '/api/space/user-management/login'
            user_headers = {"Accept": "application/vnd.net.juniper.space.user-management.user-ref+json;version=1"}
            response, response_data = self.send_request(
                request_method='POST',
                path=login_path,
                payload=None,
                headers=user_headers
            )
        else:
            raise ConnectionError('Username and password are required for login')

    def send_request(self, request_method, path, payload=None, headers=None, basic_auth=False, **kwargs):
        headers = headers if headers else BASE_HEADERS
        # space platform API endpoints which are asyncrhonous require basic_auth and no JSESSIONID cookies set.
        if basic_auth:
            self.connection._auth = None

        try:
            self._display_request(request_method)
            response, response_data = self.connection.send(path, payload, method=request_method, headers=headers, **kwargs)
            value = self._get_response_value(response_data)
            return response.getcode(), self._response_to_json(value)
        except AnsibleConnectionFailure as e:
            if to_text('401') in to_text(e):
                return 401, 'Authentication failure'
            else:
                return 404, 'Object not found'
        except HTTPError as e:
            error = json.loads(e.read())
            return e.code, error

    def _display_request(self, request_method):
        self.connection.queue_message('vvvv', 'Web Services: %s %s' % (request_method, self.connection._url))

    def _get_response_value(self, response_data):
        return to_text(response_data.getvalue())

    def _response_to_json(self, response_text):
        try:
            return json.loads(response_text) if response_text else {} 
        # JSONDecodeError only available on Python 3.5+
        except ValueError:
            return response_text
    
    def update_auth(self, response, response_text):
        """Return per-request auth token.

        The response should be a dictionary that can be plugged into the
        headers of a request. The default implementation uses cookie data.
        If no authentication data is found, return None
        """

        info = dict()
        # Lowercase keys, to conform to py2 behavior, so that py3 and py2 are predictable
        info.update(dict((k.lower(), v) for k, v in response.info().items()))

        # Don't be lossy, append header values for duplicate headers
        # In Py2 there is nothing that needs done, py2 does this for us
        if PY3:
            temp_headers = {}
            for name, value in response.headers.items():
                # The same as above, lower case keys to match py2 behavior, and create more consistent results
                name = name.lower()
                if name in temp_headers:
                    temp_headers[name] = ', '.join((temp_headers[name], value))
                else:
                    temp_headers[name] = value
            info.update(temp_headers)


        cookie = info.get('set-cookie')
        if cookie:
            return {'Cookie': cookie}

        return None

