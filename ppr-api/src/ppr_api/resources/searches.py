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

from flask import current_app, g, jsonify, request
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException
from ppr_api.models import SearchRequest, SearchResult
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_bcol_help, is_staff_account
from ppr_api.services.payment import TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight


API = Namespace('searches', description='Endpoints for PPR searches.')
VAL_ERROR = 'Search request data validation errors.'  # Validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} search db save failed: {1}'
PAY_REFUND_MESSAGE = 'Account {0} search refunding payment for invoice {1}.'
PAY_REFUND_ERROR = 'Account {0} search payment refund failed for invoice {1}: {2}.'
# Map api spec search type to payment transaction details description
TO_SEARCH_TYPE_DESCRIPTION = {
    'AIRCRAFT_DOT': 'Aircraft Airframe DOT Number:',
    'BUSINESS_DEBTOR': 'Debtor Business Name:',
    'INDIVIDUAL_DEBTOR': 'Debtor Individual Name:',
    'MHR_NUMBER': 'Manufactured Home Registration Number:',
    'REGISTRATION_NUMBER': 'Registration Number:',
    'SERIAL_NUMBER': 'Serial/VIN Number:'
}
CERTIFIED_PARAM = 'certified'
ROUTING_SLIP_PARAM = 'routingSlipNumber'
DAT_NUMBER_PARAM = 'datNumber'
BCOL_NUMBER_PARAM = 'bcolAccountNumber'


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class SearchResource(Resource):
    """Resource for executing PPR searches."""

    @staticmethod
#    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post():  # pylint: disable=too-many-branches
        """Execute a new search request using criteria in the request body."""
        try:
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if not account_id:
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
            # Staff has special payment rules and setup.
            if is_staff_account(account_id) or is_bcol_help(account_id):
                return staff_search(request, request_json, account_id)

            query = SearchRequest.create_from_json(request_json, account_id,
                                                   g.jwt_oidc_token_info.get('username', None))

            # Charge a search fee.
            invoice_id = None
            payment = Payment(jwt=jwt.get_token_auth_header(),
                              account_id=account_id,
                              details=get_payment_details(query, request_json['type']))
            pay_ref = payment.create_payment(TransactionTypes.SEARCH.value, 1, None, query.client_reference_id)
            invoice_id = pay_ref['invoiceId']
            query.pay_invoice_id = int(invoice_id)
            query.pay_path = pay_ref['receipt']

            # Execute the search query: treat no results as a success.
            try:
                query.search()

                # Now save the initial detail results in the search_result table with no
                # search selection criteria (the absence indicates an incomplete search).
                search_result = SearchResult.create_from_search_query(query)
                search_result.save()

            except Exception as db_exception:   # noqa: B902; handle all db related errors.
                current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, repr(db_exception)))
                if invoice_id is not None:
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
            if account_id is None:
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
            return jsonify(search_request.updated_selection), HTTPStatus.ACCEPTED

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


def staff_search(req: request, request_json, account_id: str):
    """Execute a staff search with special payment validation and methods."""
    payment_info = build_staff_payment(req, account_id)
    # bcol help is no fee; reg staff can be no fee.
    # FAS is routing slip only.
    # BCOL is dat number (optional) and BCOL account number (mandatory).
    # All staff roles including SBC can submit no fee searches.
    if ROUTING_SLIP_PARAM in payment_info and BCOL_NUMBER_PARAM in payment_info:
        return resource_utils.staff_payment_bcol_fas()

    if CERTIFIED_PARAM in payment_info:
        request_json['certified'] = True
    query: SearchRequest = SearchRequest.create_from_json(request_json, account_id,
                                                          g.jwt_oidc_token_info.get('username', None))

    # Always create a payment transaction.
    invoice_id = None
    payment = Payment(jwt=jwt.get_token_auth_header(),
                      account_id=account_id,
                      details=get_payment_details(query, request_json['type']))
    # staff payment
    pay_ref = payment.create_payment_staff_search(payment_info, query.client_reference_id)
    invoice_id = pay_ref['invoiceId']
    query.pay_invoice_id = int(invoice_id)
    query.pay_path = pay_ref['receipt']

    # Execute the search query: treat no results as a success.
    try:
        query.search()

        # Now save the initial detail results in the search_result table with no
        # search selection criteria (the absence indicates an incomplete search).
        search_result = SearchResult.create_from_search_query(query)
        search_result.save()

    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, repr(db_exception)))
        if invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except Exception as cancel_exception:   # noqa: B902; log exception
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id,
                                                                 repr(cancel_exception)))
        raise db_exception

    return query.json, HTTPStatus.CREATED


def build_staff_payment(req: request, account_id: str):
    """Extract payment information from request parameters."""
    payment_info = {
        'transactionType': TransactionTypes.SEARCH_STAFF_NO_FEE.value
    }
    if is_bcol_help(account_id):
        return payment_info

    certified = req.args.get(CERTIFIED_PARAM)
    routing_slip = req.args.get(ROUTING_SLIP_PARAM)
    bcol_number = req.args.get(BCOL_NUMBER_PARAM)
    dat_number = req.args.get(DAT_NUMBER_PARAM)
    if certified is not None and isinstance(certified, bool) and certified:
        payment_info[CERTIFIED_PARAM] = True
    elif certified is not None and isinstance(certified, str) and \
            certified.lower() in ['true', '1', 'y', 'yes']:
        payment_info[CERTIFIED_PARAM] = True
    if routing_slip is not None:
        payment_info[ROUTING_SLIP_PARAM] = str(routing_slip)
    if bcol_number is not None:
        payment_info[BCOL_NUMBER_PARAM] = str(bcol_number)
    if dat_number is not None:
        payment_info[DAT_NUMBER_PARAM] = str(dat_number)

    if ROUTING_SLIP_PARAM in payment_info or BCOL_NUMBER_PARAM in payment_info:
        if CERTIFIED_PARAM in payment_info:
            payment_info['transactionType'] = TransactionTypes.SEARCH_STAFF_CERTIFIED.value
        else:
            payment_info['transactionType'] = TransactionTypes.SEARCH_STAFF.value
    elif CERTIFIED_PARAM in payment_info:  # Verify this is allowed.
        payment_info['transactionType'] = TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value

    return payment_info


def get_payment_details(search_request, search_type):
    """Extract the payment details value from the search request criteria."""
    details = {
        'label': TO_SEARCH_TYPE_DESCRIPTION[search_type]
    }
    if search_request.search_type == SearchRequest.SearchTypes.BUSINESS_DEBTOR.value:
        details['value'] = search_request.search_criteria['criteria']['debtorName']['business']
    elif search_request.search_type == SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value:
        details['value'] = search_request.search_criteria['criteria']['debtorName']['last'] + ', ' +\
                           search_request.search_criteria['criteria']['debtorName']['first']
    else:
        details['value'] = search_request.search_criteria['criteria']['value']

    return details
