# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exposes all of the resource endpoints mounted in Flask-Blueprints."""
# pylint: disable=too-few-public-methods
from typing import Optional

from flask import Flask

from .callbacks import bp as callbacks_bp
from .drafts import bp as drafts_bp
from .financing_statements import bp as financing_statements_bp
from .historical_searches import bp as historical_searches_bp
from .meta import bp as meta_bp
from .ops import bp as ops_bp
from .party_codes import bp as party_codes_bp
from .search_history import bp as search_history_bp
from .search_results import bp as search_results_bp
from .searches import bp as searches_bp
from .user_profile import bp as user_profile_bp


class V1Endpoint:
    """Setup all the V1 Endpoints."""

    def __init__(self):
        """Create the endpoint setup, without initializations."""
        self.app: Optional[Flask] = None

    def init_app(self, app):
        """Register and initialize the Endpoint setup."""
        if not app:
            raise Exception('Cannot initialize without a Flask App.')  # pylint: disable=broad-exception-raised

        self.app = app

        self.app.register_blueprint(callbacks_bp)
        self.app.register_blueprint(drafts_bp)
        self.app.register_blueprint(financing_statements_bp)
        self.app.register_blueprint(historical_searches_bp)
        self.app.register_blueprint(meta_bp)
        self.app.register_blueprint(party_codes_bp)
        self.app.register_blueprint(ops_bp)
        self.app.register_blueprint(search_history_bp)
        self.app.register_blueprint(searches_bp)
        self.app.register_blueprint(search_results_bp)
        self.app.register_blueprint(user_profile_bp)


v1_endpoint = V1Endpoint()  # pylint: disable=invalid-name
