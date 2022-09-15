import { DraftResultIF, MhRegistrationSummaryIF, RegistrationSortIF, RegistrationSummaryIF } from '@/interfaces'
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
export interface RegTableNewItemI {
  addedReg: string // used for highlight / scroll to
  addedRegParent: string // used for expand
  addedRegSummary: RegistrationSummaryIF | DraftResultIF // new item to add in table
  prevDraft: string // used to remove previous draft
}
