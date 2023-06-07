import { UnitNoteDocTypes } from '@/enums'

export const mockUnitNotes = [
  {
    documentType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
    documentId: '1',
    documentRegistrationNumber: '123456',
    documentDescription: 'Notice of Caution',
    createDateTime: '2023-05-30T09:00:00Z',
    effectiveDateTime: '2023-06-01T12:00:00Z',
    expiryDateTime: '2023-06-30T23:59:59Z',
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
    status: 'ACTIVE',
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-05-31T10:00:00Z',
    effectiveDateTime: '2023-07-01T00:00:00Z',
    expiryDateTime: '2023-07-31T23:59:59Z',
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
    status: 'CANCELLED',
    destroyed: false
  },
  {
    documentType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
    documentId: '2',
    documentRegistrationNumber: '789012',
    documentDescription: 'Extension to Notice of Caution',
    createDateTime: '2023-05-31T10:00:00Z',
    effectiveDateTime: '2023-07-01T00:00:00Z',
    expiryDateTime: '2023-07-31T23:59:59Z',
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
    status: 'EXPIRED',
    destroyed: false
  }
]
