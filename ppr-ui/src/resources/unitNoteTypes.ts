import { UnitNoteDocTypes } from '@/enums'
import { UnitNoteTypeIF } from '@/interfaces'

export const UnitNoteTypes: Array<UnitNoteTypeIF> = [
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
]
