import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'
import { CancelUnitNoteIF, UnitNoteIF } from '@/interfaces/unit-note-interfaces/unit-note-interface'
import { UnitNotesInfo } from '@/resources'

export const mockedUnitNotes: Array<UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-12-30T09:00:00Z',
    effectiveDateTime: '2024-01-01T12:00:00Z',
    expiryDateTime: '2024-01-30T23:59:59Z',
    remarks: 'This is a notice of caution.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-11-31T10:00:00Z',
    effectiveDateTime: '2023-12-01T00:00:00Z',
    expiryDateTime: '2023-12-31T23:59:59Z',
    remarks: 'This is an extension to the notice of caution.',
    givingNoticeParty: {
      personName: {
        first: 'Bob',
        middle: 'L',
        last: 'Brown'
      },
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.CANCELLED,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.RESTRAINING_ORDER,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-10-30T09:00:00Z',
    effectiveDateTime: '2023-11-01T12:00:00Z',
    remarks: 'This is a notice of caution.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-09-31T10:00:00Z',
    effectiveDateTime: '2023-10-01T00:00:00Z',
    expiryDateTime: '2023-10-31T23:59:59Z',
    remarks: 'This is an extension to the notice of caution.',
    givingNoticeParty: {
      personName: {
        first: 'Bob',
        middle: 'L',
        last: 'Brown'
      },
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.EXPIRED,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.PUBLIC_NOTE,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-08-31T10:00:00Z',
    effectiveDateTime: '2023-09-01T00:00:00Z',
    remarks: 'This is an extension to the notice of caution.',
    givingNoticeParty: {
      personName: {
        first: 'Bob',
        middle: 'L',
        last: 'Brown'
      },
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.CANCELLED,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-07-31T10:00:00Z',
    effectiveDateTime: '2023-08-01T00:00:00Z',
    expiryDateTime: '2023-08-31T23:59:59Z',
    remarks: 'This is an extension to the notice of caution.',
    givingNoticeParty: {
      personName: {
        first: 'Bob',
        middle: 'L',
        last: 'Brown'
      },
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.CANCELLED,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-06-30T09:00:00Z',
    effectiveDateTime: '2023-07-01T12:00:00Z',
    expiryDateTime: '2023-07-30T23:59:59Z',
    remarks: 'This is a notice of caution.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  }
]

export const mockedUnitNotes2: Array<UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.PUBLIC_NOTE,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Public Note',
    createDateTime: '2023-07-30T09:00:00Z',
    effectiveDateTime: '2023-12-01T12:00:00Z',
    remarks: 'This is a public Note.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.PUBLIC_NOTE,
    documentId: '2',
    documentRegistrationNumber: '123456',
    documentDescription: 'Public Note',
    createDateTime: '2023-06-30T09:00:00Z',
    effectiveDateTime: '2023-06-01T12:00:00Z',
    remarks: 'This is a public Note.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.CANCELLED,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.DECAL_REPLACEMENT,
    documentId: '3',
    documentRegistrationNumber: '123456',
    documentDescription: 'Decal Replacement Note',
    createDateTime: '2023-05-30T09:00:00Z',
    effectiveDateTime: '2023-06-01T12:00:00Z',
    remarks: 'This is a decal replacment Note.',
    givingNoticeParty: {
      businessName: 'HALSTON MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'KNUTSFORD',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998',
      emailAddress: 'testing@email.com'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  }
]

export const mockedUnitNotes3: Array<UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.PUBLIC_NOTE,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Public Note',
    createDateTime: '2023-07-30T09:00:00Z',
    effectiveDateTime: '2023-12-01T12:00:00Z',
    remarks: 'This is a public Note.',
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  }
]

export const mockedUnitNotes4: Array<UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution (continued)',
    createDateTime: '2023-08-30T09:00:00Z',
    effectiveDateTime: '2023-12-03T12:00:00Z',
    remarks: 'Continued until further order of the court. This is a CAUC.',
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-07-30T09:00:00Z',
    effectiveDateTime: '2023-12-01T12:00:00Z',
    expiryDateTime: '2024-03-01T12:00:00Z',
    remarks: 'This is a CAU.',
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  }
]

export const mockedNonResUnitNote: UnitNoteIF = {
    documentType: UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Public Note',
    createDateTime: '2023-07-30T09:00:00Z',
    effectiveDateTime: '2023-12-01T12:00:00Z',
    expiryDateTime: '2023-12-01T12:00:00Z',
    remarks: 'This is a public Note.',
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: true,
    nonResidentialReason: 'BURNT'
}

export const mockedCancelPublicNote: CancelUnitNoteIF = {
  cancelledDocumentType: UnitNoteDocTypes.PUBLIC_NOTE,
  cancelledDocumentDescription: 'Public Note',
  cancelledDocumentRegistrationNumber: '12345678',
  documentType: UnitNoteDocTypes.NOTE_CANCELLATION,
  documentId: '',
  remarks: 'Original remarks for Public Note.',
  givingNoticeParty: {
    personName: {
      first: 'Bob',
      middle: 'L',
      last: 'Brown'
    },
    address: {
      street: 'PO BOX 266',
      city: 'KNUTSFORD',
      region: 'BC',
      country: 'CA',
      postalCode: 'V0E 2A0'
    },
    phoneNumber: '2508289998',
    emailAddress: 'testing@email.com'
  },
  destroyed: false
}

export const mockedUnitNotesCancelled: Array<CancelUnitNoteIF | UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.NOTE_CANCELLATION,
    documentId: '2',
    documentRegistrationNumber: '1234567',
    documentDescription: 'Cancellation of Notice of Caution',
    createDateTime: '2024-01-30T09:00:00Z',
    cancelledDocumentDescription: 'Notice of Caution',
    cancelledDocumentRegistrationNumber: '123456',
    cancelledDocumentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    remarks: 'This is a cancellation of a notice of caution.',
    givingNoticeParty: {
      businessName: 'James MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'Vancouver',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508281298'
    },
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-12-30T09:00:00Z',
    effectiveDateTime: '2024-01-01T12:00:00Z',
    expiryDateTime: '2024-01-30T23:59:59Z',
    remarks: 'This is a notice of caution.',
    givingNoticeParty: {
      businessName: 'James MODULAR HOMES LTD.',
      address: {
        street: 'PO BOX 266',
        city: 'Vancouver',
        region: 'BC',
        country: 'CA',
        postalCode: 'V0E 2A0'
      },
      phoneNumber: '2508289998'
    },
    status: UnitNoteStatusTypes.CANCELLED,
    destroyed: false
  }
]

// Notice of Tax Sale - TAXN type
export const mockedUnitNotes5: Array<UnitNoteIF> = [
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_TAX_SALE].header,
    createDateTime: '2023-08-30T09:00:00Z',
    effectiveDateTime: '2023-12-03T12:00:00Z',
    remarks: 'This is a Notice of Tax Sale note.',
    status: UnitNoteStatusTypes.ACTIVE,
    destroyed: false
  }
]

// Confidential Unit Note
export const mockedConfidentialUnitNote: UnitNoteIF = {
  documentType: UnitNoteDocTypes.CONFIDENTIAL_NOTE,
  documentId: '123',
  documentRegistrationNumber: '123456',
  documentDescription: UnitNotesInfo[UnitNoteDocTypes.CONFIDENTIAL_NOTE].header,
  createDateTime: '2023-08-28T21:13:59+00:00',
  effectiveDateTime: '2023-08-28T21:13:59+00:00',
  remarks: 'NCON Remarks.',
  status: UnitNoteStatusTypes.ACTIVE,
  destroyed: false
}

// Notice of Tax Sale (Cancelled with Notice of Redemption)
export const mockedCancelledTaxSaleNote: UnitNoteIF = {
  documentType: UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
  documentId: '10',
  documentRegistrationNumber: '11223456',
  documentDescription: UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_TAX_SALE].header,
  createDateTime: '2023-07-22T09:00:00Z',
  effectiveDateTime: '2023-12-03T12:00:00Z',
  givingNoticeParty: {
    address: {
      city: 'VICTORIA',
      country: 'CA',
      postalCode: 'V4V1C1',
      region: 'BC',
      street: '123 MAIN ST'
    },
    personName: {
      first: 'OWNER',
      last: 'ONE'
    }
  },
  remarks: 'This is a Notice of Tax Sale note.',
  status: UnitNoteStatusTypes.CANCELLED,
  destroyed: false
}

// Notice of Redemption - NRED type
export const mockedNoticeOfRedemption: CancelUnitNoteIF = {
  cancelledDocumentDescription: UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_TAX_SALE].header,
  cancelledDocumentRegistrationNumber: '11223456',
  cancelledDocumentType: UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
  documentType: UnitNoteDocTypes.NOTICE_OF_REDEMPTION,
  documentId: '113',
  documentRegistrationNumber: '12334456',
  documentDescription: UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_REDEMPTION].header,
  createDateTime: '2023-08-30T09:00:00Z',
  effectiveDateTime: '2023-12-05T12:00:00Z',
  remarks: 'Original remarks for Notice of Tax Sale. This is a Notice of Redemption note.',
  status: UnitNoteStatusTypes.ACTIVE,
  destroyed: false
}

// Residential Exemption - EXRS type
export const mockedResidentialExemptionOrder: UnitNoteIF = {
  documentType: UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER,
  documentId: '12345678',
  documentRegistrationNumber: '5544332',
  documentDescription: UnitNotesInfo[UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER].header,
  createDateTime: '2023-08-20T09:00:00Z',
  effectiveDateTime: '2023-08-20T09:00:00Z',
  remarks: 'Residential Exemption remarks',
  status: UnitNoteStatusTypes.ACTIVE,
  destroyed: false
}
