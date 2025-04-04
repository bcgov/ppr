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
"""This module wraps the calls to external payment service used by the API."""

from enum import Enum

from mhr_api.utils.base import BaseEnum


class TransactionTypes(str, Enum):
    """Derive payment request filing type from transaction type."""

    SEARCH = "SEARCH"
    SEARCH_COMBO = "SEARCH_COMBO"
    SEARCH_STAFF = "SEARCH_STAFF"
    SEARCH_STAFF_COMBO = "SEARCH_STAFF_COMBO"
    CERTIFIED = "CERTIFIED"
    REGISTRATION = "REGISTRATION"
    TRANSFER = "TRANSFER"
    EXEMPTION_RES = "EXEMPTION_RES"
    EXEMPTION_NON_RES = "EXEMPTION_NON_RES"
    TRANSPORT_PERMIT = "TRANSPORT_PERMIT"
    TRANSPORT_PERMIT_EXT = "TRANSPORT_PERMIT_EXT"
    UNIT_NOTE = "UNIT_NOTE"
    UNIT_NOTE_TAXN = "UNIT_NOTE_TAXN"
    UNIT_NOTE_102 = "UNIT_NOTE_102"
    DECAL_REPLACE = "DECAL_REPLACE"
    UNIT_NOTE_OTHER = "UNIT_NOTE_OTHER"
    ADMIN_CORLC = "ADMIN_CORLC"
    ADMIN_RLCHG = "ADMIN_RLCHG"
    AMEND_PERMIT = "AMEND_PERMIT"
    AMENDMENT = "AMENDMENT"
    CORRECTION = "CORRECTION"
    CANCEL_PERMIT = "CANCEL_PERMIT"


class PaymentMethods(BaseEnum):
    """Render an Enum of the pay api payment methods."""

    CASH = "CASH"
    CC = "CC"
    CHEQUE = "CHEQUE"
    DIRECT_PAY = "DIRECT_PAY"
    DRAWDOWN = "DRAWDOWN"
    EFT = "EFT"
    EJV = "EJV"
    INTERNAL = "INTERNAL"
    ONLINE_BANKING = "ONLINE_BANKING"
    PAD = "PAD"
    WIRE = "WIRE"


class StatusCodes(BaseEnum):
    """Render an Enum of the pay api invoice response status codes."""

    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    CREATED = "CREATED"
    CREDITED = "CREDITED"
    DELETED = "DELETED"
    OVERDUE = "OVERDUE"
    PAID = "PAID"
    REFUND_REQUESTED = "REFUND_REQUESTED"
    REFUNDED = "REFUNDED"
    SETTLEMENT_SCHED = "SETTLEMENT_SCHED"
