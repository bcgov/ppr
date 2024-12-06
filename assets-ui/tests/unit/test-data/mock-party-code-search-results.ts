import { SearchPartyIF } from '@/interfaces'

export const mockedPartyCodeSearchResults: Array<SearchPartyIF> = [
  {
    address: {
      city: 'VICTORIA',
      country: 'CA',
      postalCode: 'V8V3K5',
      region: 'BC',
      street: '1061 FORT STREET'
    },
    businessName:
      'TONY SCOTT REVENUE ADMINISTRATION BRANCH',
    code: '6000',
    contact: { name: '', phoneNumber: '' }
  },
  {
    address: {
      city: 'TORONTO',
      country: 'CA',
      postalCode: 'M4R1K8',
      region: 'ON',
      street: '20 EGLINTON AVE  WEST, SUITE 1'
    },
    businessName: 'TONY DUARTE',
    code: '30002',
    contact: { areaCode: '604', name: 'BARB HEINRICH', phoneNumber: '2777777' }
  },
  {
    address: {
      city: 'ENDERBY',
      country: 'CA',
      postalCode: 'V2P6J4',
      region: 'BC',
      street: '606 OLD VERNON RD  BOX 370'
    },
    businessName: "TONY'S TIRE SERVICE LTD.",
    code: '50009',
    contact: { name: '', phoneNumber: '' }
  }
]
