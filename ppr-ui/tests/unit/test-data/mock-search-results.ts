import { APIVehicleTypes, MatchTypes, UIMHRSearchTypes, UISearchTypes } from '@/enums'
import { ManufacturedHomeSearchResultIF, SearchResultIF } from '@/interfaces'

type mockSearchResults = {
  [UISearchTypes.SERIAL_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.INDIVIDUAL_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.BUSINESS_DEBTOR]?: Array<SearchResultIF>
  [UISearchTypes.MHR_NUMBER]?: Array<SearchResultIF>
  [UISearchTypes.AIRCRAFT]?: Array<SearchResultIF>
  [UISearchTypes.REGISTRATION_NUMBER]?: Array<SearchResultIF>
}

type mockMHRSearchResults = {
  [UIMHRSearchTypes.MHRMHR_NUMBER]?: Array<ManufacturedHomeSearchResultIF>
  [UIMHRSearchTypes.MHRORGANIZATION_NAME]?: Array<ManufacturedHomeSearchResultIF>
  [UIMHRSearchTypes.MHROWNER_NAME]?: Array<ManufacturedHomeSearchResultIF>
  [UIMHRSearchTypes.MHRSERIAL_NUMBER]?: Array<ManufacturedHomeSearchResultIF>
}

export const mockedSearchResults: mockSearchResults = {
  [UISearchTypes.SERIAL_NUMBER]: [
    {
      id: 1,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023001B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 1,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622994',
        year: 2018,
        make: 'HYUNDAI',
        model: 'TUCSON'
      }
    },
    {
      id: 2,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023001C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 2,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622995',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1'
      }
    },
    {
      id: 3,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 3,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622996',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2'
      }
    },
    {
      id: 4,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 4,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622997',
        year: 2017,
        make: 'TESTmake3',
        model: 'TESTmodel3'
      }
    },
    {
      id: 5,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002F',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 5,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622998',
        year: 2017,
        make: 'TESTmake4',
        model: 'TESTmodel4'
      }
    },
    {
      id: 6,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003G',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 6,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU622999',
        year: 2017,
        make: 'TESTmake5',
        model: 'TESTmodel5'
      }
    },
    {
      id: 7,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023002H',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 7,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU623000',
        year: 2017,
        make: 'TESTmake6',
        model: 'TESTmodel6'
      }
    },
    {
      id: 8,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023003I',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 8,
        type: APIVehicleTypes.MOTOR_VEHICLE,
        serialNumber: 'KM8J3CA46JU623001',
        year: 2017,
        make: 'TESTmake7',
        model: 'TESTmodel7'
      }
    }
  ],
  [UISearchTypes.INDIVIDUAL_DEBTOR]: [
    {
      id: 1,
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
      id: 2,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '014739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        personName: {
          first: 'test',
          second: 'test',
          last: 'tester'
        }
      }
    },
    {
      id: 3,
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
      id: 4,
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
      id: 1,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '013739B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 1'
      }
    },
    {
      id: 2,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '123001C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 2'
      }
    },
    {
      id: 3,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '223002D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      debtor: {
        businessName: 'test 3'
      }
    },
    {
      id: 4,
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
      id: 1,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023021B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 1,
        type: APIVehicleTypes.MANUFACTURED_HOME,
        serialNumber: 'KM8J3CA46JU622914',
        year: 2018,
        make: 'HYUNDAI',
        model: 'TUCSON',
        manufacturedHomeRegistrationNumber: '123456'
      }
    },
    {
      id: 2,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023021C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 2,
        type: APIVehicleTypes.MANUFACTURED_HOME,
        serialNumber: 'KM8J3CA46JU622925',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1',
        manufacturedHomeRegistrationNumber: '123457'
      }
    },
    {
      id: 3,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023032D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 3,
        type: APIVehicleTypes.MANUFACTURED_HOME,
        serialNumber: 'KM8J3CA46JU622936',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2',
        manufacturedHomeRegistrationNumber: '123457'
      }
    },
    {
      id: 4,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023013E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 4,
        type: APIVehicleTypes.MANUFACTURED_HOME,
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
      id: 1,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023101B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 1,
        type: APIVehicleTypes.AIRCRAFT,
        serialNumber: 'KM8J3CA46JU622194',
        year: 1998,
        make: 'CESSNA',
        model: '172R SKYHAWK'
      }
    },
    {
      id: 2,
      matchType: MatchTypes.EXACT,
      baseRegistrationNumber: '023201C',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 2,
        type: APIVehicleTypes.AIRCRAFT,
        serialNumber: 'KM8J3CA46JU622295',
        year: 2017,
        make: 'TESTmake1',
        model: 'TESTmodel1'
      }
    },
    {
      id: 3,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023302D',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 3,
        type: APIVehicleTypes.AIRCRAFT,
        serialNumber: 'KM8J3CA46JU622396',
        year: 2017,
        make: 'TESTmake2',
        model: 'TESTmodel2'
      }
    },
    {
      id: 4,
      matchType: MatchTypes.SIMILAR,
      baseRegistrationNumber: '023403E',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA',
      vehicleCollateral: {
        id: 4,
        type: APIVehicleTypes.AIRCRAFT,
        serialNumber: 'KM8J3CA46JU622497',
        year: 2017,
        make: 'TESTmake3',
        model: 'TESTmodel3'
      }
    }
  ],
  [UISearchTypes.REGISTRATION_NUMBER]: [
    {
      id: 1,
      matchType: MatchTypes.EXACT,
      registrationNumber: '223456A',
      baseRegistrationNumber: '123456A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      id: 2,
      matchType: MatchTypes.SIMILAR,
      registrationNumber: '223456B',
      baseRegistrationNumber: '123456B',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      id: 3,
      matchType: MatchTypes.SIMILAR,
      registrationNumber: '223455A',
      baseRegistrationNumber: '123455A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    },
    {
      id: 4,
      matchType: MatchTypes.SIMILAR,
      registrationNumber: '223454A',
      baseRegistrationNumber: '123454A',
      createDateTime: '2020-02-21T18:56:20Z',
      registrationType: 'SA'
    }
  ]
}

export const mockedMHRSearchResults: mockMHRSearchResults = {
  [UIMHRSearchTypes.MHRMHR_NUMBER]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 4,
      ownerName: {
        first: 'Karen',
        last: 'Pensley'
      },
      status: 'HISTORIC',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 5,
      ownerName: {
        first: 'Steve',
        last: 'Jobs'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHROWNER_NAME]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 4,
      ownerName: {
        first: 'Karen',
        last: 'Pensley'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHRORGANIZATION_NAME]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 4,
      ownerName: {
        first: 'Karen',
        last: 'Pensley'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHRSERIAL_NUMBER]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 1,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 1,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 3,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 4,
      ownerName: {
        first: 'Karen',
        last: 'Pensley'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 1,
      exemptCount: 0,
      historicalCount: 0
    }
  ]
}

export const mockedMHRSearchResultsSorted: mockMHRSearchResults = {
  [UIMHRSearchTypes.MHRMHR_NUMBER]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 5,
      ownerName: {
        first: 'Steve',
        last: 'Jobs'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 4,
      ownerName: {
        first: 'Karen',
        last: 'Pensley'
      },
      status: 'HISTORIC',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ]
}

export const mockedMHRSearchSelections: mockMHRSearchResults = {
  [UIMHRSearchTypes.MHRMHR_NUMBER]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: true,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 3,
      ownerName: {
        first: 'John',
        last: 'Lane'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHROWNER_NAME]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHRORGANIZATION_NAME]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'EXEMPT',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: true,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ],
  [UIMHRSearchTypes.MHRSERIAL_NUMBER]: [
    {
      id: 1,
      ownerName: {
        first: 'Ted',
        last: 'Smith'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: false,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    },
    {
      id: 2,
      ownerName: {
        first: 'Jane',
        last: 'Doe'
      },
      status: 'ACTIVE',
      mhrNumber: '1234567',
      serialNumber: 'ABC987',
      baseInformation: {
        year: 2000,
        make: 'Honda',
        model: 'Trailer'
      },
      homeLocation: 'Victoria',
      selected: true,
      includeLienInfo: true,
      activeCount: 0,
      exemptCount: 0,
      historicalCount: 0
    }
  ]
}
