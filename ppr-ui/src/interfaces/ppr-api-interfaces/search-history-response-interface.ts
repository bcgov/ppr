import { ErrorIF, SearchResponseIF, ManufacturedHomeSearchResponseIF } from '@/interfaces'

// Search Query response (search step 1) interface.
export interface SearchHistoryResponseIF {
  searches: Array<SearchResponseIF>,
  error?: ErrorIF
}

export interface MHRSearchHistoryResponseIF {
  searches: Array<ManufacturedHomeSearchResponseIF>,
  error?: ErrorIF
}
