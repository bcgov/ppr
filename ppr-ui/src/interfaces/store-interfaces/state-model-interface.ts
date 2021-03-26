import { AccountInformationIF, SearchResponseIF, TombStoneIF, SearchTypeIF } from '@/interfaces'
import { IndividualNameIF } from '../ppr-api-interfaces';

// State model example
export interface StateModelIF {
  tombstone: TombStoneIF
  accountInformation: AccountInformationIF
  debtorName: IndividualNameIF
  searchHistory: Array<SearchResponseIF>
  // results from current search
  searchResults: SearchResponseIF
  searchedType: SearchTypeIF
  searchedValue: string
}
