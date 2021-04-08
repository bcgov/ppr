import { SearchResponseIF } from '@/interfaces'
import { ErrorIF } from './error-interface'

// Search Query response (search step 1) interface.
export interface SearchHistoryResponseIF {
  searches: Array<SearchResponseIF>,
  error?: ErrorIF
}
