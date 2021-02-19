import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchTypeIF } from '@/interfaces'

export const SearchTypes: Array<SearchTypeIF> = [
  {
    selectDisabled: false,
    divider: false,
    searchTypeUI: UISearchTypes.SERIAL_NUMBER,
    searchTypeAPI: APISearchTypes.SERIAL_NUMBER,
    textLabel: 'Enter a serial number',
    hints: {
      searchValue: 'Serial numbers normally contain letters and numbers only'
    }
  },
  {
    selectDisabled: true,
    divider: false,
    searchTypeUI: UISearchTypes.INDIVIDUAL_DEBTOR,
    searchTypeAPI: APISearchTypes.INDIVIDUAL_DEBTOR,
    textLabel: 'tbd',
    hints: null
  },
  {
    selectDisabled: true,
    divider: false,
    searchTypeUI: UISearchTypes.BUSINESS_DEBTOR,
    searchTypeAPI: APISearchTypes.BUSINESS_DEBTOR,
    textLabel: 'tbd',
    hints: null
  },
  {
    // divider in dropdown list
    selectDisabled: true,
    divider: true,
    searchTypeUI: null,
    searchTypeAPI: null,
    textLabel: null,
    hints: null
  },
  {
    divider: false,
    selectDisabled: true,
    searchTypeUI: UISearchTypes.MHR_NUMBER,
    searchTypeAPI: APISearchTypes.MHR_NUMBER,
    textLabel: 'tbd',
    hints: null
  },
  {
    divider: false,
    selectDisabled: true,
    searchTypeUI: UISearchTypes.AIRCRAFT,
    searchTypeAPI: APISearchTypes.AIRCRAFT,
    textLabel: 'tbd',
    hints: null
  },
  {
    divider: false,
    selectDisabled: true,
    searchTypeUI: UISearchTypes.REGISTRATION_NUMBER,
    searchTypeAPI: APISearchTypes.REGISTRATION_NUMBER,
    textLabel: 'Enter a registration number',
    hints: null
  }
]
