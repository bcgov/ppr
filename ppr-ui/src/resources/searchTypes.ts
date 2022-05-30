import {
  APISearchTypes,
  UISearchTypes,
  APIMHRSearchTypes,
  UIMHRSearchTypes,
  BlankSearchTypes,
  APIMHRMapSearchTypes
} from '@/enums'
import { SearchTypeIF } from '@/interfaces'

export const SearchTypes: Array<SearchTypeIF> = [
  {
    class: 'search-list-header',
    selectDisabled: true,
    divider: false,
    group: 1,
    searchTypeUI: null,
    searchTypeAPI: BlankSearchTypes.BLANK1,
    textLabel: 'Personal Property Registry Search',
    hints: null,
    icon: 'mdi-car',
    color: 'primary'
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.SERIAL_NUMBER,
    searchTypeAPI: APISearchTypes.SERIAL_NUMBER,
    textLabel: 'Enter a serial number',
    hints: {
      searchValue: 'Serial numbers normally contain letters and numbers only'
    },
    group: 1
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.INDIVIDUAL_DEBTOR,
    searchTypeAPI: APISearchTypes.INDIVIDUAL_DEBTOR,
    textLabel: '',
    hints: null,
    group: 1
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.BUSINESS_DEBTOR,
    searchTypeAPI: APISearchTypes.BUSINESS_DEBTOR,
    textLabel: 'Enter a business debtor name',
    hints: {
      searchValue: 'Business names must contain between 2 and 150 characters'
    },
    group: 1
  },
  {
    // divider in dropdown list
    divider: true,
    selectDisabled: true,
    searchTypeUI: null,
    searchTypeAPI: BlankSearchTypes.BLANK2,
    textLabel: null,
    hints: null,
    group: 1
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.MHR_NUMBER,
    searchTypeAPI: APISearchTypes.MHR_NUMBER,
    textLabel: 'Enter a manufactured home registration number',
    hints: {
      searchValue: 'Manufactured home registration numbers normally contain up to 6 digits'
    },
    group: 1
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.AIRCRAFT,
    searchTypeAPI: APISearchTypes.AIRCRAFT,
    textLabel: 'Enter an aircraft airframe D.O.T. number',
    hints: {
      searchValue: 'Up to 25 characters'
    },
    group: 1
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.REGISTRATION_NUMBER,
    searchTypeAPI: APISearchTypes.REGISTRATION_NUMBER,
    textLabel: 'Enter a registration number',
    hints: {
      searchValue: 'Registration numbers contain 7 characters'
    },
    group: 1
  }
]

export const MHRSearchTypes: Array<SearchTypeIF> = [
  {
    class: 'search-list-header',
    selectDisabled: true,
    divider: false,
    group: 2,
    searchTypeUI: null,
    searchTypeAPI: BlankSearchTypes.BLANK3,
    textLabel: 'Manufactured Home Registration Search',
    hints: null,
    icon: 'mdi-home',
    color: 'success'
  },
  {
    // divider in dropdown list
    divider: true,
    selectDisabled: true,
    searchTypeUI: null,
    searchTypeAPI: BlankSearchTypes.BLANK4,
    textLabel: null,
    hints: null,
    group: 2
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UIMHRSearchTypes.MHRMHR_NUMBER,
    searchTypeAPI: APIMHRMapSearchTypes.MHRMHR_NUMBER,
    textLabel: 'Enter a manufactured home registration number',
    hints: {
      searchValue: 'Manufactured home registration numbers normally contain up to 6 digits'
    },
    group: 2
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UIMHRSearchTypes.MHROWNER_NAME,
    searchTypeAPI: APIMHRMapSearchTypes.MHROWNER_NAME,
    textLabel: '',
    hints: {
      searchValue: 'Owner names normally contain letter and numbers only'
    },
    group: 2
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UIMHRSearchTypes.MHRORGANIZATION_NAME,
    searchTypeAPI: APIMHRMapSearchTypes.MHRORGANIZATION_NAME,
    textLabel: '',
    hints: {
      searchValue: 'Organization names must contain between 2 and 70 characters'
    },
    group: 2
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UIMHRSearchTypes.MHRSERIAL_NUMBER,
    searchTypeAPI: APIMHRMapSearchTypes.MHRSERIAL_NUMBER,
    textLabel: 'Enter a serial number',
    hints: {
      searchValue: 'Serial numbers normally contain letters and numbers only'
    },
    group: 2
  }
]
