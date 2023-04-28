import {
  DraftResultIF,
  MhrDraftIF,
  MhRegistrationSummaryIF,
  RegistrationSortIF,
  RegistrationSummaryIF
} from '@/interfaces'

export interface RegTableNewItemI {
  addedReg: string // used for highlight / scroll to
  addedRegParent: string // used for expand
  addedRegSummary: RegistrationSummaryIF | MhRegistrationSummaryIF | DraftResultIF | MhrDraftIF // add new item to table
  prevDraft: string // used to remove previous draft
}

export interface RegTableDataI {
  baseRegs: RegistrationSummaryIF[]
  baseMhRegs: MhRegistrationSummaryIF[]
  draftsBaseReg: DraftResultIF[]
  draftsChildReg: DraftResultIF[]
  newItem: RegTableNewItemI
  sortHasMorePages: boolean
  sortOptions: RegistrationSortIF
  sortPage: number
  totalRowCount: number
}
