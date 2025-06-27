import type {
  ErrorIF,
  ManufacturedHomeSearchResultIF,
  PaymentIF,
  SearchCriteriaIF,
  SearchResultIF
} from '@/interfaces'

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
  error?: ErrorIF,
  inProgress?: boolean,
  isPending?: boolean,
  loadingPDF?: boolean,
  userId?: string,
  username?: string,
  payment?: PaymentIF,
  paymentPending?: boolean
}

export interface ManufacturedHomeSearchResponseIF {
  searchId: string,
  totalResultsSize: number,
  selectedResultsSize?: number,
  searchDateTime?: string, // UTC ISO formatted date and time.
  searchQuery: SearchCriteriaIF, // Echoes request
  results: ManufacturedHomeSearchResultIF[],
  error?: ErrorIF,
  inProgress?: boolean,
  loadingPDF?: boolean,
  userId?: string,
  username?: string,
  payment: PaymentIF,
  paymentPending?: boolean
}
