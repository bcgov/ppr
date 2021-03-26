import { UISearchTypes } from '@/enums';
import { SearchHistoryResponseIF } from '@/interfaces';
import { mockedSearchResponse } from './mock-search-responses';

export const mockedSearchHistory: SearchHistoryResponseIF = {
  searches: [
    mockedSearchResponse[UISearchTypes.SERIAL_NUMBER],
    mockedSearchResponse[UISearchTypes.BUSINESS_DEBTOR],
    mockedSearchResponse[UISearchTypes.MHR_NUMBER],
    mockedSearchResponse[UISearchTypes.AIRCRAFT],
    mockedSearchResponse[UISearchTypes.REGISTRATION_NUMBER]
  ]
}
