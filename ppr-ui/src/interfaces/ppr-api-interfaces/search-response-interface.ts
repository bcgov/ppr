import { SearchCriteriaIF, SearchResultIF } from '@/interfaces'

// Search Query response (search step 1) interface.
export interface SearchResponseIF {
  searchId: string,
  maxResultsSize: number,
  totalResultsSize: number,
  returnedResultsSize: number,
  searchDateTime?: string, // UTC ISO formatted date and time.
  searchQuery: SearchCriteriaIF, // Echoes request
  results: SearchResultIF[] | {}
  errors?: string
}
