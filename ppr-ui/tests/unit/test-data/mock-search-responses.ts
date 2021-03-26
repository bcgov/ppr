import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchResponseIF } from '@/interfaces'
import { mockedSearchResults } from '.'

type mockedSearchResponse = {
  [UISearchTypes.SERIAL_NUMBER]?: SearchResponseIF
  [UISearchTypes.INDIVIDUAL_DEBTOR]?: SearchResponseIF
  [UISearchTypes.BUSINESS_DEBTOR]?: SearchResponseIF
  [UISearchTypes.MHR_NUMBER]?: SearchResponseIF
  [UISearchTypes.AIRCRAFT]?: SearchResponseIF
  [UISearchTypes.REGISTRATION_NUMBER]?: SearchResponseIF
}

export const mockedSearchResponse: mockedSearchResponse = {
  [UISearchTypes.SERIAL_NUMBER]: {
    searchId: '12234',
    searchDateTime: '2021-03-23T18:33:32Z',
    exactResultsSize: 2,
    selectedResultsSize: 3,
    returnedResultsSize: mockedSearchResults[UISearchTypes.SERIAL_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.SERIAL_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.SERIAL_NUMBER,
      criteria: {
        value: 'serial1'
      },
      clientReferenceId: '1234K'
    },
    results: mockedSearchResults[UISearchTypes.SERIAL_NUMBER]
  },
  [UISearchTypes.INDIVIDUAL_DEBTOR]: {
    searchId: '12235',
    searchDateTime: '2021-03-23T18:43:32Z',
    exactResultsSize: 3,
    selectedResultsSize: 4,
    returnedResultsSize: mockedSearchResults[UISearchTypes.INDIVIDUAL_DEBTOR].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.INDIVIDUAL_DEBTOR].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.INDIVIDUAL_DEBTOR,
      criteria: {
        debtorName: {
          first: 'test',
          last: 'tester'
        }
      },
      clientReferenceId: '123'
    },
    results: mockedSearchResults[UISearchTypes.INDIVIDUAL_DEBTOR]
  },
  [UISearchTypes.BUSINESS_DEBTOR]: {
    searchId: '12236',
    searchDateTime: '2020-05-16T21:08:32Z',
    exactResultsSize: 2,
    selectedResultsSize: 3,
    returnedResultsSize: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.BUSINESS_DEBTOR,
      criteria: {
        debtorName: {
          business: 'test business debtor'
        }
      },
      clientReferenceId: '1233333332221'
    },
    results: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR]
  },
  [UISearchTypes.MHR_NUMBER]: {
    searchId: '12237',
    searchDateTime: '2020-05-17T21:08:32Z',
    exactResultsSize: 2,
    selectedResultsSize: 3,
    returnedResultsSize: mockedSearchResults[UISearchTypes.MHR_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.MHR_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.MHR_NUMBER,
      criteria: {
        value: '123456'
      },
      clientReferenceId: ''
    },
    results: mockedSearchResults[UISearchTypes.MHR_NUMBER]
  },
  [UISearchTypes.AIRCRAFT]: {
    searchId: '12238',
    searchDateTime: '2020-05-18T21:08:32Z',
    exactResultsSize: 2,
    selectedResultsSize: 3,
    returnedResultsSize: mockedSearchResults[UISearchTypes.AIRCRAFT].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.AIRCRAFT].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.AIRCRAFT,
      criteria: {
        value: 'testAircraft'
      },
      clientReferenceId: 'abcd-123-rrr'
    },
    results: mockedSearchResults[UISearchTypes.AIRCRAFT]
  },
  [UISearchTypes.REGISTRATION_NUMBER]: {
    searchId: '12239',
    searchDateTime: '2020-05-19T21:08:32Z',
    exactResultsSize: 1,
    selectedResultsSize: 1,
    returnedResultsSize: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.REGISTRATION_NUMBER,
      criteria: {
        value: '123456A'
      },
      clientReferenceId: '1q'
    },
    results: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER]
  }
}
