INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (200000000, 'T500000', 'PS12345', 'MHREG', now() at time zone 'UTC', 
'{
  "clientReferenceId": "EX-MH001234",
  "declaredValue": "120000.00",
  "submittingParty": {
    "businessName": "ABC SEARCHING COMPANY",
    "address": {
      "street": "222 SUMMER STREET",
      "city": "VICTORIA",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8W 2V8"
    },
    "emailAddress": "bsmith@abc-search.com",
    "phoneNumber": "6041234567",
    "phoneExtension": "546"
  },
  "ownerGroups": [
    {
      "groupId": 1,
      "owners": [
        {
          "individualName": {
            "first": "Jane",
            "last": "Smith"
          },
          "address": {
            "street": "3122B LYNNLARK PLACE",
            "city": "VICTORIA",
            "region": "BC",
            "postalCode": " ",
            "country": "CA"
          },
          "phoneNumber": "6041234567"
        }
      ],
      "type": "TC",
      "interest": "UNDIVIDED 4/5",
      "interestNumerator": 4,
      "status": "ACTIVE",
      "tenancySpecified": true
    }, {
      "groupId": 2,
      "owners": [
        {
          "individualName": {
            "first": "James",
            "last": "Smith"
          },
          "address": {
            "street": "3122B LYNNLARK PLACE",
            "city": "VICTORIA",
            "region": "BC",
            "postalCode": " ",
            "country": "CA"
          },
          "phoneNumber": "6041234567"
        }
      ],
      "type": "TC",
      "interest": "UNDIVIDED 1/5",
      "interestNumerator": 1,
      "status": "ACTIVE",
      "tenancySpecified": true
    }
  ],
  "location": {
    "parkName": "HIDDEN VALLEY TRAILER COURT",
    "pad": "20",
    "address": {
      "street": "940 BLANSHARD STREET",
      "city": "VICTORIA",
      "region": "BC",
      "postalCode": " ",
      "country": "CA"
    },
    "leaveProvince": false,
    "pidNumber": "011625490",
    "taxCertificate": true,
    "taxExpiryDate": "2022-05-21T07:59:59+00:00",
    "dealerName": "NOR-TEC DESIGN GROUP LTD."
  },
  "description": {
    "manufacturer": "STARLINE",
    "baseInformation": {
      "year": 2018,
      "make": "WATSON IND. (ALTA)",
      "model": "DUCHESS"
    },
    "sectionCount": 1,
    "sections": [
      {
        "serialNumber": "52D70556",
        "lengthFeet": 52,
        "lengthInches": 0,
        "widthFeet": 12,
        "widthInches": 0
      }
    ],
    "csaNumber": "786356",
    "csaStandard": "Z240"
  }
}',
null, null, 'TESTUSER')
;
INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (200000001, 'T500001', 'PS12345', 'MHREG', now() at time zone 'UTC', '{ "clientReferenceId": "UT-TRANS0011" }',null, null, 'TESTUSER')
;
INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (200000002, 'T500002', 'PS12345', 'TRANS', now() at time zone 'UTC',
     '{
  "mhrNumber": "UT-001",
  "clientReferenceId": "UT-TRANS0011",
  "submittingParty": {
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
  "deleteOwnerGroups": [
    {
      "groupId": 5,
      "owners": [
        {
          "individualName": {
            "first": "MARY-ANNE",
            "last": "BICKNELL"
          },
          "address": {
            "street": "6665 238TH STREET",
            "city": "LANGLEY",
            "region": "BC",
            "country": "CA",
            "postalCode": "V3A 6H4"
          },
          "phoneNumber": "6044620279"
        }
      ],
      "type": "SO"
    }
  ],
  "addOwnerGroups": [
    {
      "groupId": 6,
      "owners": [
        {
          "individualName": {
            "first": "INDIANA",
            "last": "JONES"
          },
          "address": {
            "street": "1234 FRONT STREET",
            "city": "KELOWNA",
            "region": "BC",
            "country": "CA",
            "postalCode": "V2F 6H4"
          },
          "phoneNumber": "6047271234"
        }
      ],
      "type": "SO"
    }
  ]
}',
     '000900', null, 'TESTUSER')
;
