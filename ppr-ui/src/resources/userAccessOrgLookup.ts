import { OrgLookupConfigIF } from '@/interfaces'
import { MhrSubTypes } from '@/enums'

export const UserAccessOrgLookupConfig: Record<MhrSubTypes, OrgLookupConfigIF> = {
  [MhrSubTypes.LAWYERS_NOTARIES]: {
    fieldLabel: 'Find or Enter the Full Legal Name of the Business',
    fieldHint: 'Example: Legal business name of lawyer, notary or law firm',
    nilSearchText: 'If the Qualified Supplier is not an active registered B.C. business, you can manually enter the' +
      ' full legal name of the business.'
  },
  [MhrSubTypes.MANUFACTURER]: {
    fieldLabel: 'Find or Enter the Full Legal Name of the Business',
    fieldHint: 'Example: Legal business name of Manufacturer',
    nilSearchText: 'If the Qualified Supplier is not an active registered B.C. business, you can manually enter the' +
      ' full legal name of the business.'
  },
  [MhrSubTypes.DEALERS]: {
    fieldLabel: 'Find or Enter the Full Legal Name of the Business',
    fieldHint: 'Example: Legal business name of Home Dealer',
    nilSearchText: 'If the Qualified Supplier is not an active registered B.C. business, you can manually enter the' +
      ' full legal name of the business.'
  },
  [MhrSubTypes.QUALIFIED_SUPPLIER]: {
    fieldLabel: '',
    fieldHint: '',
    nilSearchText: ''
  },
  [MhrSubTypes.GENERAL_PUBLIC]: {
    fieldLabel: '',
    fieldHint: '',
    nilSearchText: ''
  }
}
