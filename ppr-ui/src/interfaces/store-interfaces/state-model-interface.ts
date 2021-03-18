import { AccountInformationIF, SearchResponseIF, TombStoneIF, SearchTypeIF } from '@/interfaces'

// State model example
export interface StateModelIF {
  tombstone: TombStoneIF
  accountInformation: AccountInformationIF
  savedResults: any
  // results from current search
  searchResults: SearchResponseIF
  searchedType: SearchTypeIF
  searchedValue: string
}
