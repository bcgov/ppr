import { UISearchTypes } from '@/enums'
import { SearchValidationIF } from '@/interfaces'

export function validateSearchAction (searchState): SearchValidationIF {
  if (!searchState.selectedSearchType) {
    return {
      category: {
        message: 'Please select a category'
      }
    }
  }
  switch (searchState.selectedSearchType.searchTypeUI) {
    case UISearchTypes.SERIAL_NUMBER:
      if (!searchState.searchValue) {
        return {
          searchValue: {
            message: 'Enter a serial number to search'
          }
        }
      }
  }
  return null
}

export function validateSearchRealTime (searchState): SearchValidationIF {
  var specialChars = /[!@#$%^&*(),.?":{}|<>]/
  const validation:SearchValidationIF = {}
  switch (searchState.selectedSearchType.searchTypeUI) {
    case UISearchTypes.SERIAL_NUMBER:
      validation.searchValue = {}
      if (searchState.searchValue && specialChars.test(searchState.searchValue)) {
        validation.searchValue.message = "Serial numbers don't normally contain special characters"
      }
      if (searchState.searchValue && searchState.searchValue.length < 4) {
        validation.searchValue.popUp = [
          'This may not be a valid serial number.',
          'You can search using this number but you might not obtain any results (the search fee will be applied).',
          'Select "Search" to continue with this serial number.'
        ]
      }
  }
  return validation
}
