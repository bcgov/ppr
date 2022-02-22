import { ErrorIF, SearchResponseIF } from '@/interfaces'

// Search Query response (search step 1) interface.
export interface SearchHistoryResponseIF {
  searches: Array<SearchResponseIF>,
  error?: ErrorIF
}
