import { UISearchTypes, UIMHRSearchTypes } from '@/enums'
import { SearchHistoryResponseIF } from '@/interfaces'
import { mockedSearchResponse, mockedMHRSearchResponse } from './mock-search-responses'

export const mockedSearchHistory: SearchHistoryResponseIF = {
  searches: [
    mockedSearchResponse[UISearchTypes.SERIAL_NUMBER],
    mockedSearchResponse[UISearchTypes.INDIVIDUAL_DEBTOR],
    mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR],
    mockedSearchResponse[UISearchTypes.MHR_NUMBER],
    mockedSearchResponse[UISearchTypes.AIRCRAFT],
    mockedSearchResponse[UISearchTypes.REGISTRATION_NUMBER]
  ],
  searchesWithMHR: [
    mockedMHRSearchResponse[UIMHRSearchTypes.MHRMHR_NUMBER],
    mockedMHRSearchResponse[UIMHRSearchTypes.MHRORGANIZATION_NAME],
    mockedMHRSearchResponse[UIMHRSearchTypes.MHROWNER_NAME],
    mockedMHRSearchResponse[UIMHRSearchTypes.MHRSERIAL_NUMBER]
  ]
}
