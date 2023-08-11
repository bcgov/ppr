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

from .admin_registrations import bp as admin_registrations_bp
from .documents import bp as documents_bp
from .drafts import bp as drafts_bp
from .exemptions import bp as exemptions_bp
from .ltsa_sync import bp as ltsa_sync_bp
from .manufacturer import bp as manufacturers_bp
from .meta import bp as meta_bp
from .notes import bp as notes_bp
from .ops import bp as ops_bp
from .other_registrations import bp as other_registrations_bp
from .permits import bp as permits_bp
from .qualified_supplier import bp as qualified_supplier_bp
from .registration_report_callback import bp as registration_report_callback_bp
from .registrations import bp as registrations_bp
from .search_history import bp as search_history_bp
from .search_report_callback import bp as search_report_callback_bp
from .search_results import bp as search_result_bp
from .searches import bp as searches_bp
from .service_agreements import bp as service_agreements_bp
from .transfers import bp as transfers_bp


class V1Endpoint:
    """Setup all the V1 Endpoints."""

    def __init__(self):
        """Create the endpoint setup, without initializations."""
        self.app: Optional[Flask] = None

    def init_app(self, app):
        """Register and initialize the Endpoint setup."""
        if not app:
            raise Exception('Cannot initialize without a Flask App.')

        self.app = app

        self.app.register_blueprint(admin_registrations_bp)
        self.app.register_blueprint(documents_bp)
        self.app.register_blueprint(drafts_bp)
        self.app.register_blueprint(exemptions_bp)
        self.app.register_blueprint(ltsa_sync_bp)
        self.app.register_blueprint(manufacturers_bp)
        self.app.register_blueprint(meta_bp)
        self.app.register_blueprint(notes_bp)
        self.app.register_blueprint(ops_bp)
        self.app.register_blueprint(other_registrations_bp)
        self.app.register_blueprint(permits_bp)
        self.app.register_blueprint(qualified_supplier_bp)
        self.app.register_blueprint(registrations_bp)
        self.app.register_blueprint(searches_bp)
        self.app.register_blueprint(search_history_bp)
        self.app.register_blueprint(search_result_bp)
        self.app.register_blueprint(search_report_callback_bp)
        self.app.register_blueprint(service_agreements_bp)
        self.app.register_blueprint(transfers_bp)
        self.app.register_blueprint(registration_report_callback_bp)


v1_endpoint = V1Endpoint()  # pylint: disable=invalid-name
