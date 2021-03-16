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
"""Exposes all of the resource endpoints mounted in Flask-Blueprint style.

Uses restplus namespaces to mount individual api endpoints into the service.

All services have 2 defaults sets of endpoints:
 - ops
 - meta
That are used to expose operational health information about the service, and meta information.
"""
from flask import Blueprint
from flask_restx import Api

from .meta import API as META_API
from .ops import API as OPS_API
from .drafts import API as DRAFT_API
from .searches import API as SEARCH_API
from .search_history import API as SEARCH_HISTORY_API
from .search_results import API as SEARCH_RESULTS_API
from .party_codes import API as CLIENT_PARTY_API
from .financing_statements import API as STATEMENT_API


__all__ = ('API_BLUEPRINT', 'OPS_BLUEPRINT')

# This will add the Authorize button to the swagger docs
# TODO oauth2 & openid may not yet be supported by restplus <- check on this
AUTHORIZATIONS = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

OPS_BLUEPRINT = Blueprint('API_OPS', __name__, url_prefix='/ops')

API_OPS = Api(OPS_BLUEPRINT,
              title='Service OPS API',
              version='1.0',
              description='The Core API for the PPR System',
              security=['apikey'],
              authorizations=AUTHORIZATIONS)

API_OPS.add_namespace(OPS_API, path='/')

API_BLUEPRINT = Blueprint('API', __name__, url_prefix='/api/v1')

API = Api(API_BLUEPRINT,
          title='BCROS PPR Business API',
          version='1.0',
          description='The Core API for the Legal Entities System',
          security=['apikey'],
          authorizations=AUTHORIZATIONS)

API.add_namespace(META_API, path='/meta')
API.add_namespace(DRAFT_API, path='/drafts')
API.add_namespace(CLIENT_PARTY_API, path='/party-codes')
API.add_namespace(SEARCH_API, path='/searches')
API.add_namespace(STATEMENT_API, path='/financing-statements')
API.add_namespace(SEARCH_HISTORY_API, path='/search-history')
API.add_namespace(SEARCH_RESULTS_API, path='/search-results')
