import { APISearchTypes, MatchTypes, UISearchTypes } from '@/enums'
import { AutoCompleteResponseIF, AutoCompleteResultIF, SearchResponseIF, SearchResultIF } from '@/interfaces'

type mockSearchResults = {
  [UISearchTypes.SERIAL_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.INDIVIDUAL_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.BUSINESS_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.MHR_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.AIRCRAFT]?: Array<SearchResultIF>
  [UISearchTypes.REGISTRATION_NUMBER]?: Array<SearchResultIF>
}

type mockedSearchResponse = {
  [UISearchTypes.SERIAL_NUMBER]?: SearchResponseIF
  [UISearchTypes.INDIVIDUAL_DEBTOR]?: SearchResponseIF
  [UISearchTypes.BUSINESS_DEBTOR]?: SearchResponseIF
  [UISearchTypes.MHR_NUMBER]?: SearchResponseIF
  [UISearchTypes.AIRCRAFT]?: SearchResponseIF
  [UISearchTypes.REGISTRATION_NUMBER]?: SearchResponseIF
}

const mockedSearchResults: mockSearchResults = {
  [UISearchTypes.SERIAL_NUMBER]: [
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023001B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622994',
        year: 2018,
        make: 'HYUNDAI',
        model: 'TUCSON'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023001C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622995',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622996',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622997',
        year: 2017,
        make: 'TESTmake3',
        model: 'TESTmodel3'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002F',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622998',
        year: 2017,
        make: 'TESTmake4',
        model: 'TESTmodel4'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003G',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU622999',
        year: 2017,
        make: 'TESTmake5',
        model: 'TESTmodel5'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002H',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU623000',
        year: 2017,
        make: 'TESTmake6',
        model: 'TESTmodel6'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003I',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MV',
        serialNumber: 'KM8J3CA46JU623001',
        year: 2017,
        make: 'TESTmake7',
        model: 'TESTmodel7'
      }
    }
  ],
  [UISearchTypes.INDIVIDUAL_DEBTOR]: null,
  [UISearchTypes.BUSINESS_DEBTOR]: [
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '013739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 1'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '123001C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 2'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '223002D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 3'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '223003E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 4'
      }
    }
  ],
  [UISearchTypes.MHR_NUMBER]: [
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023021B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MH',
        serialNumber: 'KM8J3CA46JU622914',
        year: 2018,
        make: 'HYUNDAI',
        model: 'TUCSON',
        manufacturedHomeRegistrationNumber: '123456'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023021C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MH',
        serialNumber: 'KM8J3CA46JU622925',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1',
        manufacturedHomeRegistrationNumber: '123457'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023032D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MH',
        serialNumber: 'KM8J3CA46JU622936',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2',
        manufacturedHomeRegistrationNumber: '123457'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023013E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'MH',
        serialNumber: 'KM8J3CA46JU622947',
        year: 2017,
        make: 'TESTmake3',
        model: 'TESTmodel3',
        manufacturedHomeRegistrationNumber: '123458'
      }
    }
  ],
  [UISearchTypes.AIRCRAFT]: [
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023101B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'AC',
        serialNumber: 'KM8J3CA46JU622194',
        year: 1998,
        make: 'CESSNA',
        model: '172R SKYHAWK'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023201C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'AC',
        serialNumber: 'KM8J3CA46JU622295',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023302D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'AC',
        serialNumber: 'KM8J3CA46JU622396',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023403E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        type: 'AC',
        serialNumber: 'KM8J3CA46JU622497',
        year: 2017,
        make: 'TESTmake3',
        model: 'TESTmodel3'
      }
    }
  ],
  [UISearchTypes.REGISTRATION_NUMBER]: [
    {
      matchType: MatchTypes.EXACT,
      registrationNumber: '223456A',
      baseRegistrationNumber: '123456A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      matchType: MatchTypes.EXACT,
      registrationNumber: '223456B',
      baseRegistrationNumber: '123456B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      matchType: MatchTypes.SIMILAR,
      registrationNumber: '223455A',
      baseRegistrationNumber: '123455A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      matchType: MatchTypes.SIMILAR,
      registrationNumber: '223454A',
      baseRegistrationNumber: '123454A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    }
  ]
}
const mockedVonResults: Array<AutoCompleteResultIF> = [
  {
    type: 'name',
    value: 'test1',
    score: 1
  },
  {
    type: 'name',
    value: 'test2',
    score: 1
  },
  {
    type: 'name',
    value: 'test3',
    score: 1
  },
  {
    type: 'name',
    value: 'test4',
    score: 1
  },
  {
    type: 'name',
    value: 'test5',
    score: 1
  },
  {
    type: 'name',
    value: 'test6',
    score: 1
  }
]

export const mockedSearchResponse:mockedSearchResponse = {
  [UISearchTypes.SERIAL_NUMBER]: {
    searchId: '12234',
    searchDateTime: '2020-05-14T21:08:32Z',
    returnedResultsSize: mockedSearchResults[UISearchTypes.SERIAL_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.SERIAL_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.SERIAL_NUMBER,
      criteria: {
        value: 'serial1'
      }
    },
    results: mockedSearchResults[UISearchTypes.SERIAL_NUMBER]
  },
  [UISearchTypes.INDIVIDUAL_DEBTOR]: null,
  [UISearchTypes.BUSINESS_DEBTOR]: {
    searchId: '12236',
    searchDateTime: '2020-05-16T21:08:32Z',
    returnedResultsSize: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.BUSINESS_DEBTOR,
      criteria: {
        value: 'test business debtor'
      }
    },
    results: mockedSearchResults[UISearchTypes.BUSINESS_DEBTOR]
  },
  [UISearchTypes.MHR_NUMBER]: {
    searchId: '12237',
    searchDateTime: '2020-05-17T21:08:32Z',
    returnedResultsSize: mockedSearchResults[UISearchTypes.MHR_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.MHR_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.MHR_NUMBER,
      criteria: {
        value: '123456'
      }
    },
    results: mockedSearchResults[UISearchTypes.MHR_NUMBER]
  },
  [UISearchTypes.AIRCRAFT]: {
    searchId: '12238',
    searchDateTime: '2020-05-18T21:08:32Z',
    returnedResultsSize: mockedSearchResults[UISearchTypes.AIRCRAFT].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.AIRCRAFT].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.AIRCRAFT,
      criteria: {
        value: 'testAircraft'
      }
    },
    results: mockedSearchResults[UISearchTypes.AIRCRAFT]
  },
  [UISearchTypes.REGISTRATION_NUMBER]: {
    searchId: '12239',
    searchDateTime: '2020-05-19T21:08:32Z',
    returnedResultsSize: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER].length,
    totalResultsSize: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER].length,
    maxResultsSize: 1000,
    searchQuery: {
      type: APISearchTypes.REGISTRATION_NUMBER,
      criteria: {
        value: '123456A'
      }
    },
    results: mockedSearchResults[UISearchTypes.REGISTRATION_NUMBER]
  }
}

export const mockedVonResponse: AutoCompleteResponseIF = {
  total: 6,
  results: mockedVonResults
}
