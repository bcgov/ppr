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
"""This module holds data for maintaining client party name, address, and contact info.

Client parties are reusable registering parties and secured parties.
"""
from __future__ import annotations

from sqlalchemy.sql import text

from ppr_api.exceptions import DatabaseException
from ppr_api.models import AccountBcolId, Address
from ppr_api.models import utils as model_utils
from ppr_api.utils.logging import logger

from .db import db

CLIENT_CODE_BRANCH_QUERY = """
select LPAD(cc.id::text, 8, '0') as party_code, cc.id as branch_id, cc.head_id, cc.name, cc.contact_name,
       cc.contact_phone_number, cc.contact_area_cd, cc.email_address,
       a.street, a.street_additional, a.city, a.region, a.postal_code, a.country, cc.account_id
  from client_codes cc, addresses a
 where LPAD(cc.id::text, 8, '0') like :query_val
   and a.id = cc.address_id
order by cc.id
"""
GENERATED_ID_QUERY = """
select nextval('code_branch_id_seq') AS next_head_id
"""


class ClientCode(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information (registering and secured parties)."""

    __tablename__ = "client_codes"

    # key value is generated from a db function tbd. ,default=db.func.get_code_branch_id()
    id = db.mapped_column("id", db.Integer, primary_key=True, nullable=False)
    head_id = db.mapped_column("head_id", db.Integer, index=True, nullable=False)
    name = db.mapped_column("name", db.String(150), index=True, nullable=False)
    bconline_account = db.mapped_column("bconline_account", db.Integer, nullable=True)
    # contact info
    contact_name = db.mapped_column("contact_name", db.String(100), nullable=False)
    contact_area_cd = db.mapped_column("contact_area_cd", db.String(3), nullable=True)
    contact_phone_number = db.mapped_column("contact_phone_number", db.String(15), nullable=False)
    email_id = db.mapped_column("email_address", db.String(250), nullable=True)
    user_id = db.mapped_column("user_id", db.String(7), nullable=True)
    date_ts = db.mapped_column("date_ts", db.DateTime, nullable=True)
    account_id = db.mapped_column("account_id", db.String(20), index=True, nullable=True)

    # parent keys
    client_code_registration_id = db.mapped_column(
        "client_code_registration_id",
        db.Integer,
        db.ForeignKey("client_code_registrations.id"),
        nullable=True,
        index=True,
    )
    address_id = db.mapped_column("address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=False, index=True)
    users_id = db.mapped_column("users_id", db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    client_code_registration = db.relationship(
        "ClientCodeRegistration",
        foreign_keys=[client_code_registration_id],
        back_populates="client_code",
        cascade="all, delete",
        uselist=False,
    )
    address = db.relationship(
        "Address", foreign_keys=[address_id], uselist=False, back_populates="client_code", cascade="all, delete"
    )
    party = db.relationship("Party", uselist=True, back_populates="client_code")
    client_code_historical = db.relationship("ClientCodeHistorical", uselist=True, back_populates="client_code")

    @property
    def json(self) -> dict:
        """Return the client party branch as a json object."""
        party = {
            "code": self.format_party_code(),
            "headOfficeCode": self.format_head_office_code(),
            "accountId": self.account_id if self.account_id else "",
            "businessName": self.name,
            "contact": {
                "name": self.contact_name if self.contact_name else "",
                "phoneNumber": self.contact_phone_number if self.contact_phone_number else "",
            },
        }
        # if self.bconline_account:  # Verify no access issue.
        #    party["bconlineAccount"] = self.bconline_account
        if self.contact_area_cd:
            party["contact"]["areaCode"] = self.contact_area_cd
        if self.email_id:
            party["emailAddress"] = self.email_id
        if self.address:
            cp_address = self.address.json
            party["address"] = cp_address

        return party

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        db.session.add(self)
        db.session.commit()

    def format_party_code(self) -> str:
        """Return the client party code in the 8 character format padded with leading zeroes."""
        return str(self.id).strip().rjust(8, "0")

    def format_head_office_code(self) -> str:
        """Return the client party head office code in the 4 character format padded with leading zeroes."""
        return str(self.head_id).strip().rjust(4, "0")

    @classmethod
    def find_by_code(cls, code: str = None):
        """Return a client party branch json object by client code."""
        party = None
        if code:
            try:
                party = db.session.query(ClientCode).filter(ClientCode.id == int(code)).one_or_none()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_code exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception

        if party:
            return party.json

        return party

    @classmethod
    def find_by_head_office_code(cls, head_office_id: str):
        """Return a list of client parties belonging to a head office searching by code."""
        party_codes = []
        if head_office_id and len(head_office_id) <= 4 and head_office_id.strip().isdigit():
            party_list = None
            try:
                party_list = (
                    db.session.query(ClientCode)
                    .filter(ClientCode.head_id == int(head_office_id.strip()))
                    .order_by(ClientCode.id)
                    .all()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_head_office_code exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception

            if not party_list:
                return party_codes
            for party in party_list:
                party_codes.append(party.json)

        return party_codes

    @classmethod
    def find_by_head_office_start(cls, head_office_id: str):
        """Return a list of client parties belonging to a head office searching by code or partial code."""
        if len(head_office_id.strip()) == 4:
            return cls.find_by_head_office_code(head_office_id)
        party_codes = []
        # Example 111 match on 111 or 1110..1119; 001 match on 1 or 10..19.
        base_id: int = int(head_office_id.strip())
        start_id = base_id * 10
        end_id = start_id + 9
        try:
            party_list = (
                db.session.query(ClientCode)
                .filter((ClientCode.head_id == base_id) | (ClientCode.head_id.between(start_id, end_id)))
                .order_by(ClientCode.id)
                .all()
            )
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_by_head_office_start exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if not party_list:
            return party_codes
        for party in party_list:
            party_codes.append(party.json)

        return party_codes

    @classmethod
    def find_by_bcrs_account(cls, account_id: str) -> list:
        """Return a client code JSON list of party codes that match the account ID."""
        party_codes = []
        if not account_id:
            return party_codes
        try:
            party_list = (
                db.session.query(ClientCode).filter(ClientCode.account_id == account_id).order_by(ClientCode.id).all()
            )
            if not party_list:
                return party_codes
            for party in party_list:
                party_codes.append(party.json)
            return party_codes
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"DB find_by_bcrs_account exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    @classmethod
    def find_by_account_id(cls, account_id: str, crown_charge: bool = True, securities_act: bool = False):
        """Return a list of client parties searching by account ID using the account id - bcol id mapping table."""
        party_codes = []
        if not account_id:
            return party_codes
        try:
            bcol_accounts = AccountBcolId.find_by_account_id(account_id)
            ids = []
            if bcol_accounts:
                for account in bcol_accounts:
                    if (
                        crown_charge
                        and account.crown_charge_ind
                        and account.crown_charge_ind == AccountBcolId.INDICATOR_YES
                    ):
                        ids.append(account.bconline_account)
                    elif (
                        securities_act
                        and account.securities_act_ind
                        and account.securities_act_ind == AccountBcolId.INDICATOR_YES
                    ):
                        ids.append(account.bconline_account)
                    elif (
                        not crown_charge
                        and not account.crown_charge_ind
                        and not securities_act
                        and not account.securities_act_ind
                    ):
                        ids.append(account.bconline_account)
            if not ids:
                return party_codes

            party_list = db.session.query(ClientCode).filter(ClientCode.bconline_account.in_(ids)).all()
            if party_list:
                for party in party_list:
                    party_codes.append(party.json)
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_by_account_id exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        return party_codes

    @classmethod
    def find_by_branch_start(cls, branch_code: str):
        """Return a list of client parties matching on branch ids that start with a query number."""
        party_codes = []
        if not branch_code or not branch_code.strip().isdigit():
            return party_codes
        try:
            query_num: int = int(branch_code.strip())
            query_code = str(query_num) + "%"
            logger.debug(f"branch id matching on {query_code} from branch_code {branch_code}")
            party_list = (
                db.session.query(ClientCode)
                .filter(db.cast(ClientCode.id, db.String).like(query_code))
                .order_by(ClientCode.id)
                .all()
            )
            if not party_list:
                return party_codes
            for party in party_list:
                party_codes.append(party.json)
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_by_branch_start exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        return party_codes

    @classmethod
    def find_by_head_office_name(cls, head_office_name: str = None, is_fuzzy_search: bool = False):
        """Return a list of client parties belonging to a head office searching by name."""
        party_codes = []
        if head_office_name and head_office_name.strip() != "":
            try:
                name = head_office_name.strip().upper()
                party_list = None
                if is_fuzzy_search:
                    name += "%"
                    party_list = db.session.query(ClientCode).filter(ClientCode.name.like(name)).all()
                else:
                    party_list = db.session.query(ClientCode).filter(ClientCode.name == name).all()

                if not party_list:
                    return party_codes
                for party in party_list:
                    party_codes.append(party.json)
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_head_office_name exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return party_codes

    @classmethod
    def find_by_head_office(cls, name_or_id: str = None, is_fuzzy_search: bool = False):
        """Return a list of client parties belonging to a head office searching by either ID or name."""
        if is_fuzzy_search:
            return cls.find_by_head_office_name(name_or_id, is_fuzzy_search)

        if name_or_id and name_or_id.strip().isdigit():
            if len(name_or_id) <= 4:
                return cls.find_by_head_office_start(name_or_id)
            return cls.find_by_code_start(name_or_id)

        return cls.find_by_head_office_name(name_or_id)

    @classmethod
    def find_by_code_start(cls, party_code: str):
        """Return a list of client parties matching on branch ids that start with a query number."""
        client_codes = []
        if not party_code or not party_code.strip().isdigit():
            return client_codes
        try:
            query_code: str = party_code.strip() + "%"
            logger.debug(f"party code matching on {query_code}")
            query = text(CLIENT_CODE_BRANCH_QUERY)
            results = db.session.execute(query, {"query_val": query_code})
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    client_code = {
                        "code": str(row[0]),
                        "accountId": str(row[14]) if row[14] else "",
                        "businessName": str(row[3]),
                        "contact": {
                            "name": str(row[4]) if row[4] else "",
                            "phoneNumber": str(row[5]) if row[5] else "",
                        },
                        "address": {
                            "street": str(row[8]) if row[8] else "",
                            "streetAdditional": str(row[9]) if row[9] else "",
                            "city": str(row[10]) if row[10] else "",
                            "region": str(row[11]) if row[11] else "",
                            "postalCode": str(row[12]) if row[12] else "",
                            "country": str(row[13]) if row[13] else "",
                        },
                    }
                    if row[6]:
                        client_code["contact"]["areaCode"] = str(row[6])
                    if row[7]:
                        client_code["emailAddress"] = str(row[7])
                    client_codes.append(client_code)
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_by_code_start exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        return client_codes

    @staticmethod
    def get_next_head_code():
        """Get the next available head office code.

        A new head office code is used create the first branch - a new party code with a branch code of 1.
        """
        result = db.session.execute(text(GENERATED_ID_QUERY))
        row = result.first()
        head_id = int(row[0])
        logger.info(f"Next client party head office code={head_id}")
        return head_id

    @staticmethod
    def get_next_branch_code(head_office_code: str) -> int:
        """Return the next branch code for a the head office."""
        try:
            head_code: int = int(head_office_code.strip())
            party_list = (
                db.session.query(ClientCode)
                .filter(ClientCode.head_id == int(head_code))
                .order_by(ClientCode.id.desc())
                .all()
            )
            if not party_list:  # Request for a new head office and branch
                branch_id: int = head_code * 10000 + 1
                logger.info(f"No existing branch for head office {head_office_code}: returning {branch_id}")
                return branch_id
            else:
                branch_id: int = party_list[0].id + 1
                logger.info(f"Head office {head_office_code}: returning new branch code {branch_id}")
                return branch_id
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"Head office {head_office_code} get_next_branch_code exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    @staticmethod
    def create_new_from_json(json_data: dict, account_id: str):
        """Create a client party code object from dict/json as new head office and first branch."""
        code: ClientCode = ClientCode(
            head_id=ClientCode.get_next_head_code(),
            date_ts=model_utils.now_ts(),
            account_id=account_id,
            name=json_data.get("businessName"),
            email_id=json_data.get("emailAddress"),
        )
        branch_code: str = code.format_head_office_code() + "0001"
        code.id = int(branch_code)
        code.address = Address.create_from_json(json_data["address"])
        if json_data.get("contact"):
            if json_data["contact"].get("name"):
                code.contact_name = json_data["contact"].get("name")
            if json_data["contact"].get("phoneNumber"):
                code.contact_phone_number = json_data["contact"].get("phoneNumber")
            if json_data["contact"].get("areaCode"):
                code.contact_area_cd = json_data["contact"].get("areaCode")
        if json_data.get("bconlineAccount"):  # Retain for audit, not used with new codes.
            code.bconline_account = json_data.get("bconlineAccount")
        return code

    @staticmethod
    def create_new_branch_from_json(json_data: dict, account_id: str):
        """Create a client party code object from dict/json as new branch for an existing head office."""
        head_code: str = str(json_data.get("headOfficeCode").strip())
        head_id: int = int(head_code)
        code: ClientCode = ClientCode(
            head_id=head_id,
            date_ts=model_utils.now_ts(),
            account_id=account_id,
            name=json_data.get("businessName"),
            email_id=json_data.get("emailAddress"),
        )
        code.id = ClientCode.get_next_branch_code(head_code)
        code.address = Address.create_from_json(json_data["address"])
        if json_data.get("contact"):
            if json_data["contact"].get("name"):
                code.contact_name = json_data["contact"].get("name")
            if json_data["contact"].get("phoneNumber"):
                code.contact_phone_number = json_data["contact"].get("phoneNumber")
            if json_data["contact"].get("areaCode"):
                code.contact_area_cd = json_data["contact"].get("areaCode")
        if json_data.get("bconlineAccount"):  # Retain for audit, not used with new codes.
            code.bconline_account = json_data.get("bconlineAccount")
        return code
