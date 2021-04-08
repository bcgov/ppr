import { AccountInformationIF, AuthorizationIF, SearchResponseIF, SearchTypeIF, UserInfoIF } from '@/interfaces'
import { IndividualNameIF } from '../ppr-api-interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  authorization: AuthorizationIF
  debtorName: IndividualNameIF
  searchHistory: Array<SearchResponseIF>
  searchResults: SearchResponseIF
  searchedType: SearchTypeIF
  searchedValue: string
  userInfo: UserInfoIF
}
