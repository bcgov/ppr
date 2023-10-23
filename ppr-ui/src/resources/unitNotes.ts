import { FeeSummaryDefaults } from '@/composables/fees/enums'
import { UnitNoteDocTypes } from '@/enums'
import { UnitNoteInfoIF } from '@/interfaces'

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

export const NoticeOfCautionDropDown: Array<UnitNoteDocTypes> = [
  UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
  UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION
]

export const NoticeOfTaxSaleDropDown: Array<UnitNoteDocTypes> = [
  UnitNoteDocTypes.NOTICE_OF_REDEMPTION
]

// Dropdown items for Staff when Mhr has Residential Exemption note
export const ResidentialExemptionStaffDropDown: Array<UnitNoteDocTypes> = [
  UnitNoteDocTypes.PUBLIC_NOTE,
  UnitNoteDocTypes.CONFIDENTIAL_NOTE
]

// Dropdown items for QS when Mhr has Residential Exemption note
export const ResidentialExemptionQSDropDown: Array<UnitNoteDocTypes> = [
  UnitNoteDocTypes.PUBLIC_NOTE
]

export const UnitNotesInfo: Record<UnitNoteDocTypes, UnitNoteInfoIF> = {
  [UnitNoteDocTypes.NOTICE_OF_CAUTION]: {
    header: 'Notice of Caution',
    dropdownText: 'Notice of Caution',
    fee: FeeSummaryDefaults.UNIT_NOTE_20
  },
  [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION]: {
    header: 'Continued Notice of Caution',
    dropdownText: 'Add Continued Notice of Caution',
    dropdownIcon: 'mdi-plus',
    fee: FeeSummaryDefaults.NO_FEE,
    panelHeader: 'Notice of Caution',
    generatedRemarks: 'Continued until further order of the court.'
  },
  [UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]: {
    header: 'Extension to Notice of Caution',
    dropdownText: 'Add Extension to Notice of Caution',
    dropdownIcon: 'mdi-plus',
    fee: FeeSummaryDefaults.UNIT_NOTE_10,
    panelHeader: 'Notice of Caution'
  },
  [UnitNoteDocTypes.NOTE_CANCELLATION]: {
    header: 'Cancel Note',
    dropdownText: 'Cancel Note',
    dropdownIcon: 'mdi-delete',
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
  [UnitNoteDocTypes.RESCIND_EXEMPTION]: { // TODO: Update values and fee when working on Rescind Exemptions ticket
    header: 'Rescind Residential Exemption Order',
    dropdownText: 'Rescind Residential Exemption Order',
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
  },
  [UnitNoteDocTypes.NOTICE_OF_REDEMPTION]: {
    header: 'Notice of Redemption',
    dropdownText: 'File Notice of Redemption',
    dropdownIcon: 'mdi-file',
    fee: FeeSummaryDefaults.NO_FEE
  }
}

// Unit Notes that are submitted via /admin-registrations API endpoint
// COU, COUR, FZE, EXRE, NCAN, NRED, and THAW
export const AdminRegistrationNotes = [
  UnitNoteDocTypes.NOTE_CANCELLATION,
  UnitNoteDocTypes.NOTICE_OF_REDEMPTION
]

// Unit Notes that are submitted via /notes API endpoint
// CAU, CAUC, CAUE, NCON, NPUB, REST, TAXN, REG_102, and REGC
export const RegularRegistrationNotes = [
  UnitNoteDocTypes.NOTICE_OF_CAUTION,
  UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
  UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
  UnitNoteDocTypes.CONFIDENTIAL_NOTE,
  UnitNoteDocTypes.PUBLIC_NOTE,
  UnitNoteDocTypes.RESTRAINING_ORDER,
  UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
  UnitNoteDocTypes.DECAL_REPLACEMENT,
  UnitNoteDocTypes.REGISTRATION_CORRECTION
]

export const CancellableUnitNoteTypes: UnitNoteDocTypes[] = [
  UnitNoteDocTypes.NOTICE_OF_CAUTION,
  UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
  UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION,
  UnitNoteDocTypes.CONFIDENTIAL_NOTE,
  UnitNoteDocTypes.PUBLIC_NOTE,
  UnitNoteDocTypes.RESTRAINING_ORDER
  /*
  Possible Future Filing
  Exemptions (EXRS) (EXRN)
  */
]

export const remarksContent = {
  title: 'Remarks',
  description: 'Remarks will be shown when a search result is produced for this manufactured home.',
  sideLabel: 'Add Remarks',
  sideLabelCancelNote: 'Remarks',
  checkboxLabel: 'A notice pursuant to section 645/656 of the Local Government Act was filed'
}

// List of Unit Notes that can put MHR in Locked state for Qualified Suppliers
export const QSLockedStateUnitNoteTypes: string[] = [
  UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
  UnitNoteDocTypes.CONFIDENTIAL_NOTE,
  UnitNoteDocTypes.RESTRAINING_ORDER
]

export const cancelledWithRedemptionNote = '(Cancelled with Notice of Redemption)'
