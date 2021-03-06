import { SearchCriteriaIF, SearchResultIF } from '@/interfaces'
import { ErrorIF } from './error-interface'

// Search Query response (search step 1) interface.
export interface SearchResponseIF {
  searchId: string,
  exactResultsSize?: number,
  maxResultsSize: number,
  returnedResultsSize: number,
  selectedResultsSize?: number,
  totalResultsSize: number,
  searchDateTime?: string, // UTC ISO formatted date and time.
  searchQuery: SearchCriteriaIF, // Echoes request
  results: SearchResultIF[],
  error?: ErrorIF
}
