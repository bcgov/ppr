import { FeeSummaryDefaults } from '@/composables/fees/enums'
import { UnitNoteDocTypes } from '@/enums'

/* eslint-disable max-len */
export const unitNotes = {
  addUnitNoteDropdown: [
    {
      unitNoteType: UnitNoteDocTypes.NOTICE_OF_CAUTION,
      textLabel: 'Notice of Caution'
    },
    {
      unitNoteType: UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
      textLabel: 'Continued Notice of Caution'
    },
    {
      unitNoteType: UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
      textLabel: 'Extension to Notice of Caution'
    },
    {
      unitNoteType: UnitNoteDocTypes.NOTE_CANCELLATION,
      textLabel: 'Note Cancellation'
    },
    {
      unitNoteType: UnitNoteDocTypes.CONFIDENTIAL_NOTE,
      textLabel: 'Confidential Note'
    },
    {
      unitNoteType: UnitNoteDocTypes.PUBLIC_NOTE,
      textLabel: 'Public Note'
    },
    {
      unitNoteType: UnitNoteDocTypes.RESTRAINING_ORDER,
      textLabel: 'Restraining Order'
    },
    {
      unitNoteType: UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
      textLabel: 'Notice of Tax Sale'
    },
    {
      unitNoteType: UnitNoteDocTypes.DECAL_REPLACEMENT,
      textLabel: 'Decal Replacement'
    },
    {
      unitNoteType: UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION,
      textLabel: 'Non-Residential Exemption'
    },
    {
      unitNoteType: UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER,
      textLabel: 'Residential Exemption Order'
    }
  ],

  [UnitNoteDocTypes.NOTICE_OF_CAUTION]: {
    header: 'Notice of Caution',
    typeDesc: 'Notice of Caution',
    fee: FeeSummaryDefaults.UNIT_NOTE_20
  },
  [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION]: {
    header: 'Continued Notice of Caution',
    typeDesc: 'Continued Notice of Caution',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]: {
    header: 'Extension to Notice of Caution',
    typeDesc: 'Extension to Notice of Caution',
    fee: FeeSummaryDefaults.UNIT_NOTE_10
  },
  [UnitNoteDocTypes.NOTE_CANCELLATION]: {
    header: 'Cancel Note',
    typeDesc: 'Cancel Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.CONFIDENTIAL_NOTE]: {
    header: 'Confidential Note',
    typeDesc: 'Confidential Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.PUBLIC_NOTE]: {
    header: 'Public Note',
    typeDesc: 'Public Note',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.RESTRAINING_ORDER]: {
    header: 'Restraining Order',
    typeDesc: 'Restraining Order',
    fee: FeeSummaryDefaults.UNIT_NOTE_20
  },
  [UnitNoteDocTypes.NOTICE_OF_TAX_SALE]: {
    header: 'Notice of Tax Sale',
    typeDesc: 'Notice of Tax Sale',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.DECAL_REPLACEMENT]: {
    header: 'Decal Replacement',
    typeDesc: 'Decal Replacement',
    fee: FeeSummaryDefaults.UNIT_NOTE_10
  },
  [UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION]: {
    header: 'Non-Residential Exemption',
    typeDesc: 'Non-Residential Exemption',
    fee: FeeSummaryDefaults.NO_FEE
  },
  [UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER]: {
    header: 'Residential Exemption Order',
    typeDesc: 'Residential Exemption Order',
    fee: FeeSummaryDefaults.UNIT_NOTE_50
  }
}
