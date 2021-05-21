-- Unregistered draft financing statement
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000003, 'D-T-FS01', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'NA', null, 
'{
  "type": "FINANCING_STATEMENT",
  "financingStatement": {
    "type": "SA",
    "clientReferenceId": "A-00000402",
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "debtors": [
      {
        "businessName": "Debtor 1 Inc.",
        "address": {
          "street": "721 Debtor Ave",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "A1A 1A1"
        },
        "birthDate": "1990-06-15",
        "emailAddress": "dsmith@debtor1.com"
      }
    ],
    "vehicleCollateral": [
      {
        "type": "MV",
        "serialNumber": "KM8J3CA46JU622994",
        "year": 2018,
        "make": "HYUNDAI",
        "model": "TUCSON"
      }
    ],
    "lifeYears": 5,
    "securedParties": [
      {
        "businessName": "BANK OF BRITISH COLUMBIA",
        "address": {
          "street": "3721 BEACON AVENUE",
          "city": "SIDNEY",
          "region": "BC",
          "country": "CA",
          "postalCode": "V7R 1R7"
        },
        "emailAddress": "asmith@bobc.com"
      }
    ]
  }
}');

-- Unregistered draft amendment statement
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000004, 'D-T-AM01', 'PS12345', CURRENT_TIMESTAMP, 'AMENDMENT', 'AM', 'TEST0001', null, 
'{
  "type": "AMENDMENT_STATEMENT",
  "amendmentStatement": {
    "baseRegistrationNumber": "023003B",
    "documentId": "D0034002",
    "description": "Amendment to correct spelling mistake in debtor name. Name changed from \"Brawn\" to \"Brown\".",
    "changeType": "AM",
    "clientReferenceId": "A-00000402",
    "baseDebtor": {
      "businessName": "DEBTOR 1 INC."
    },
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "deleteDebtors": [
      {
        "businessName": "Brawn Window Cleaning Inc.",
        "partyId": 1321065
      }
    ],
    "addDebtors": [
      {
        "businessName": "Brown Window Cleaning Inc.",
        "address": {
          "street": "1234 Blanshard St",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "V8S 3J5"
        },
        "emailAddress": "csmith@bwc.com"
      }
    ]
  }
}');

-- Unregistered draft change statement
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000005, 'D-T-CH01', 'PS12345', CURRENT_TIMESTAMP, 'CHANGE', 'DT', 'TEST0001', null,
'{
  "type": "CHANGE_STATEMENT",
  "changeStatement": {
    "baseRegistrationNumber": "023010B",
    "documentId": "D0034003",
    "changeType": "DT",
    "baseDebtor": {
      "businessName": "DEBTOR 1 INC."
    },
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "addDebtors": [
      {
        "businessName": "Brown Window Cleaning Inc.",
        "address": {
          "street": "1234 Blanshard St",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "V8S 3J5"
        },
        "emailAddress": "csmith@bwc.com"
      }
    ],
    "deleteDebtors": [
      {
        "businessName": "Brawn Window Cleaning Inc.",
        "partyId": 1321065
      }
    ]
  }
}');
