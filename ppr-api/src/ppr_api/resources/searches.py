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
"""API endpoints for executing PPR searches."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors

from registry_schemas import utils as schema_utils
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import SearchRequest, SearchResult
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment, TransactionTypes
from ppr_api.resources import utils as resource_utils


API = Namespace('searches', description='Endpoints for PPR searches.')
VAL_ERROR = 'Search request data validation errors.'  # Validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} search db save failed: {1}'
PAY_REFUND_MESSAGE = 'Account {0} search refunding payment for invoice {1}.'
PAY_REFUND_ERROR = 'Account {0} search payment refund failed for invoice {1}: {2}.'


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class SearchResource(Resource):
    """Resource for executing PPR searches."""

    @staticmethod
#    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post():
        """Execute a new search request using criteria in the request body."""
        try:

            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchQuery', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)
            # Perform any extra data validation such as start and end dates here
            SearchRequest.validate_query(request_json)
            query = SearchRequest.create_from_json(request_json, account_id)

            # Charge a search fee.
            invoice_id = None
            if account_id:
                payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                pay_ref = payment.create_payment(TransactionTypes.SEARCH.value, 1, None, query.client_reference_id)
                invoice_id = pay_ref['invoiceId']
                query.pay_invoice_id = int(invoice_id)
                query.pay_path = pay_ref['receipt']

            # Execute the search query: treat no results as a success.
            try:
                query.search()
                # if not query.search_response or query.returned_results_size == 0:
                #   return resource_utils.unprocessable_error_response('search query')

                # Now save the initial detail results in the search_result table with no
                # search selection criteria (the absence indicates an incomplete search).
                search_result = SearchResult.create_from_search_query(query)
                search_result.save()

            except Exception as db_exception:   # noqa: B902; handle all db related errors.
                current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, repr(db_exception)))
                if account_id and invoice_id is not None:
                    current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
                    try:
                        payment.cancel_payment(invoice_id)
                    except Exception as cancel_exception:   # noqa: B902; log exception
                        current_app.logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id,
                                                                         repr(cancel_exception)))

                raise db_exception

            return query.json, HTTPStatus.CREATED

        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('PUT,OPTIONS')
@API.route('/<path:search_id>', methods=['PUT', 'OPTIONS'])
class SearchDetailResource(Resource):
    """Resource for processing requests to update the search selection (UI autosave)."""

    @staticmethod
#    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def put(search_id):
        """Execute a search selection update request replacing the current value with the request body contents."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

            search_request = SearchRequest.find_by_id(search_id)
            if not search_request:
                return resource_utils.not_found_error_response('searchId', search_id)

            # Save the updated search selection.
            search_request.update_search_selection(request_json)
            return jsonify(search_request.search_response), HTTPStatus.ACCEPTED

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)
