import { FeeSummaryDefaults } from '@/composables/fees/enums'
import { UnitNoteDocTypes } from '@/enums'

export const UnitNotesDropdown: Array<UnitNoteDocTypes> = [
  UnitNoteDocTypes.DECAL_REPLACEMENT,
  UnitNoteDocTypes.PUBLIC_NOTE,
  UnitNoteDocTypes.NOTICE_OF_CAUTION,
  UnitNoteDocTypes.CONFIDENTIAL_NOTE,
  UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
  UnitNoteDocTypes.RESTRAINING_ORDER
  // original list of Note types
  // UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
  // UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
  // UnitNoteDocTypes.NOTE_CANCELLATION,
  // UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION,
  // UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER
]

export const UnitNotesInfo = {
  [UnitNoteDocTypes.NOTICE_OF_CAUTION]: {
    header: 'Notice of Caution',
    dropdownText: 'Notice of Caution',
    fee: FeeSummaryDefaults.UNIT_NOTE_20
  },
  [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION]: {
    header: 'Continued Notice of Caution',
    dropdownText: 'Continued Notice of Caution',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]: {
    header: 'Extension to Notice of Caution',
    dropdownText: 'Extension to Notice of Caution',
    fee: FeeSummaryDefaults.UNIT_NOTE_10
  },
  [UnitNoteDocTypes.NOTE_CANCELLATION]: {
    header: 'Cancel Note',
    dropdownText: 'Cancel Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.CONFIDENTIAL_NOTE]: {
    header: 'Confidential Note',
    dropdownText: 'Confidential Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.PUBLIC_NOTE]: {
    header: 'Public Note',
    dropdownText: 'Public Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.RESTRAINING_ORDER]: {
    header: 'Restraining Order',
    dropdownText: 'Restraining Order',
    fee: FeeSummaryDefaults.UNIT_NOTE_20
  },
  [UnitNoteDocTypes.NOTICE_OF_TAX_SALE]: {
    header: 'Notice of Tax Sale',
    dropdownText: 'Notice of Tax Sale',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.DECAL_REPLACEMENT]: {
    header: 'Decal Replacement',
    dropdownText: 'Decal Replacement',
    fee: FeeSummaryDefaults.UNIT_NOTE_10
  },
  [UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION]: {
    header: 'Non-Residential Exemption',
    dropdownText: 'Non-Residential Exemption',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER]: {
    header: 'Residential Exemption Order',
    dropdownText: 'Residential Exemption Order',
    fee: FeeSummaryDefaults.UNIT_NOTE_50
  },
  [UnitNoteDocTypes.TRANSPORT_PERMIT]: {
    header: 'Transport Permit',
    dropdownText: 'Transport Permit',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.TRANSPORT_PERMIT_EXTENSION]: {
    header: 'Transport Permit Extension',
    dropdownText: 'Transport Permit Extension',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.REGISTRATION_CORRECTION]: {
    header: 'Registration Correction',
    dropdownText: 'Registration Correction',
    fee: FeeSummaryDefaults.NO_FEE
  }
}
