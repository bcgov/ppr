# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Mounting the end-points."""
# pylint: disable=too-few-public-methods
from http import HTTPStatus
from typing import Optional

from flask import Flask, current_app, redirect, request, url_for  # noqa: I001
from ppr_api import errorhandlers
from ppr_api.utils.run_version import get_run_version
from registry_schemas import __version__ as registry_schemas_version  # noqa: I005

from .constants import EndpointEnum, EndpointVersionEnum
from .v1 import v1_endpoint


class Endpoints:
    """Manage the mounting, traversal and redirects for a set of versioned end-points."""

    app: Optional[Flask] = None

    def init_app(self, app: Flask):
        """Initialize the endpoints mapped for all services.

        Manages the versioned routes.
        Sets up redirects based on Accept headers or Versioned routes.
        """
        self.app = app
        self._handler_setup()
        self._mount_endpoints()

    def _handler_setup(self):
        @self.app.route('/')
        def be_nice_swagger_redirect():  # pylint: disable=unused-variable
            """Redirect / to the swagger app, until the REST extension is removed."""
            # TODO: remove this when the REST extension is removed.
            return redirect(EndpointEnum.API_V1, code=HTTPStatus.MOVED_PERMANENTLY)

        @self.app.before_request
        def before_request():  # pylint: disable=unused-variable
            """Before routing the request, check the Accept Version header to route to the correct API."""
            if (version := request.headers.get('accept-version')) and request.endpoint:  # pylint: disable=R1705
                if version == EndpointVersionEnum.V1 and request.endpoint.startswith(EndpointEnum.API.name + '.'):
                    return self._redirect(
                        url_for(
                            request.endpoint.replace(EndpointEnum.API.name, EndpointEnum.API_V1.name, 1)
                        ))
                if version == EndpointVersionEnum.V1 \
                    and not request.endpoint.startswith(EndpointEnum.API_V1.name + '.') \
                        and request.endpoint.startswith(EndpointEnum.API.name + '.'):
                    return self._redirect(
                        url_for(
                            request.endpoint.replace(EndpointEnum.API.name, EndpointEnum.API_V1.name, 1)
                        ))
            return None

        @self.app.after_request
        def add_version(response):  # pylint: disable=unused-variable
            version = get_run_version()
            response.headers['API'] = f'mhr_api/{version}'
            response.headers['SCHEMAS'] = f'registry_schemas/{registry_schemas_version}'
            return response

        errorhandlers.init_app(self.app)

    def _redirect(self, path, code=302):
        if request.method == 'OPTIONS':
            options_resp = current_app.make_default_options_response()
            self._set_access_control_header(options_resp)
            return options_resp

        resp = redirect(path, code=code)
        self._set_access_control_header(resp)
        return resp

    @classmethod
    def _set_access_control_header(cls, response):  # pylint: disable=unused-variable
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'

    def _mount_endpoints(self):
        """Mount the endpoints of the system."""
        v1_endpoint.init_app(self.app)


endpoints = Endpoints()  # pylint: disable=invalid-name
