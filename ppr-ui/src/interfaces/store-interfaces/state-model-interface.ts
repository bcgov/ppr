import { AccountInformationIF, SearchResponseIF, SearchResultIF, TombStoneIF } from '@/interfaces'

// State model example
export interface StateModelIF {
  tombstone: TombStoneIF
  accountInformation: AccountInformationIF
  searching: boolean
  // results from current search
  searchResults: SearchResponseIF
}
