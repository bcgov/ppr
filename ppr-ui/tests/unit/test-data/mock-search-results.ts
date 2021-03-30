import { MatchTypes, UISearchTypes } from '@/enums'
import { SearchResultIF } from '@/interfaces'

type mockSearchResults = {
  [UISearchTypes.SERIAL_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.INDIVIDUAL_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.BUSINESS_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.MHR_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.AIRCRAFT]?: Array<SearchResultIF>
  [UISearchTypes.REGISTRATION_NUMBER]?: Array<SearchResultIF>
}

export const mockedSearchResults: mockSearchResults = {
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
  [UISearchTypes.INDIVIDUAL_DEBTOR]: [
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '013739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        personName: {
          first: 'test',
          last: 'tester'
        },
        birthDate: '1997-07-16T19:20:30+01:00'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '014739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        personName: {
          first: 'test',
          second: 'test',
          last: 'tester'
        },
        birthDate: '1994-02-11T19:10:30+01:00'
      }
    },
    {
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        personName: {
          first: 'tests',
          last: 'tester'
        },
        birthDate: '1977-09-16T19:20:30+01:00'
      }
    },
    {
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '113739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        personName: {
          first: 'testing',
          last: 'tests'
        },
        birthDate: '1965-11-16T05:20:30+01:00'
      }
    }
  ],
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
      matchType: MatchTypes.SIMILAR,
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