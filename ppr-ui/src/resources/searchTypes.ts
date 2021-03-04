import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchTypeIF } from '@/interfaces'

export const SearchTypes: Array<SearchTypeIF> = [
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.SERIAL_NUMBER,
    searchTypeAPI: APISearchTypes.SERIAL_NUMBER,
    textLabel: 'Enter a serial number',
    hints: {
      searchValue: 'Serial numbers normally contain letters and numbers only'
    }
  },
  {
    divider: false,
    selectDisabled: true,
    searchTypeUI: UISearchTypes.INDIVIDUAL_DEBTOR,
    searchTypeAPI: APISearchTypes.INDIVIDUAL_DEBTOR,
    textLabel: 'tbd',
    hints: null
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.BUSINESS_DEBTOR,
    searchTypeAPI: APISearchTypes.BUSINESS_DEBTOR,
    textLabel: 'Enter a business debtor name',
    hints: {
      searchValue: 'Business names must contain between 2 and 70 characters'
    }
  },
  {
    // divider in dropdown list
    divider: true,
    selectDisabled: true,
    searchTypeUI: null,
    searchTypeAPI: null,
    textLabel: null,
    hints: null
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.MHR_NUMBER,
    searchTypeAPI: APISearchTypes.MHR_NUMBER,
    textLabel: 'Enter a manufactured home registration number',
    hints: {
      searchValue: 'Manufactured home registration number must contain 6 digits'
    }
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.AIRCRAFT,
    searchTypeAPI: APISearchTypes.AIRCRAFT,
    textLabel: 'Enter an aircraft airframe D.O.T. number',
    hints: {
      searchValue: 'Up to 25 letters'
    }
  },
  {
    divider: false,
    selectDisabled: false,
    searchTypeUI: UISearchTypes.REGISTRATION_NUMBER,
    searchTypeAPI: APISearchTypes.REGISTRATION_NUMBER,
    textLabel: 'Enter a registration number',
    hints: {
      searchValue: 'Registration numbers contain 6 digits followed by 1 letter, e.g., 123456A'
    }
  }
]
