import { APIRegistrationTypes, APISearchTypes, APIMHRMapSearchTypes } from '@/enums'
import {
  IndividualNameIF,
  SearchTypeIF,
  SearchValidationIF
} from '@/interfaces'

// subset of the localState that includes what the validator needs
type partialSearchState = {
  debtorName?: IndividualNameIF
  searchValue?: string
  searchValueFirst?: string
  searchValueSecond?: string
  searchValueLast?: string
  selectedSearchType: SearchTypeIF
}

const specialCharsStrict = /[!@#$%^&*(),.?"{}|<>`~_;:'/\\[\]-]/
const specialCharsLax = /[!@#$%^*(),?"{}|<>`~_[\]]/
const numbersOnly = /^\d+$/
const lettersOnly = /^[A-z]+$/
const regNumber = /^\d{6}[A-z]{1}$/
const regNumberPartial = /^\d{1,6}[A-z]{0,1}$/
// replaceAll fails in jest so use regex
const dash = /-/g

export function validateSearchAction (
  searchState: partialSearchState
): SearchValidationIF {
  const validation: SearchValidationIF = {
    category: {},
    searchValue: {}
  }
  let searchValue: string = searchState?.searchValue?.trim()
  const first = searchState?.searchValueFirst?.trim()
  const second = searchState?.searchValueSecond?.trim()
  const last = searchState?.searchValueLast?.trim()
  if (!searchState?.selectedSearchType) {
    validation.category.message = 'Please select a category'
    return validation
  }
  switch (searchState?.selectedSearchType?.searchTypeAPI) {
    case APISearchTypes.SERIAL_NUMBER:
    case APIMHRMapSearchTypes.MHRSERIAL_NUMBER:
      if (!searchValue) {
        validation.searchValue.message = 'Enter a serial number to search'
      }
      if ((searchState?.selectedSearchType?.searchTypeAPI === APISearchTypes.SERIAL_NUMBER) &&
        (searchValue?.length > 25)) {
        validation.searchValue.message = 'Maximum 25 characters'
      }
      if ((searchState?.selectedSearchType?.searchTypeAPI === APIMHRMapSearchTypes.MHRSERIAL_NUMBER) &&
        (searchValue?.length > 20)) {
        validation.searchValue.message = 'Maximum 20 characters'
      }
      break
    case APISearchTypes.INDIVIDUAL_DEBTOR:
      if (!first) {
        validation.searchValue.messageFirst = 'Enter a first name'
      } else if (first?.length > 50) {
        validation.searchValue.messageFirst = 'Maximum 50 characters'
      }
      if (second && second?.length > 50) {
        validation.searchValue.messageSecond = 'Maximum 50 characters'
      }
      if (!last) {
        validation.searchValue.messageLast = 'Enter a last name'
      } else if (last?.length > 50) {
        validation.searchValue.messageLast = 'Maximum 50 characters'
      }
      break
    case APIMHRMapSearchTypes.MHROWNER_NAME:
      if (!first) {
        validation.searchValue.messageFirst = 'Enter a first name'
      } else if (first?.length > 15) {
        validation.searchValue.messageFirst = 'Maximum 15 characters'
      }
      if (second && second?.length > 15) {
        validation.searchValue.messageSecond = 'Maximum 15 characters'
      }
      if (!last) {
        validation.searchValue.messageLast = 'Enter a last name'
      } else if (last?.length > 25) {
        validation.searchValue.messageLast = 'Maximum 25 characters'
      }
      break
    case APISearchTypes.BUSINESS_DEBTOR:
      if (!searchValue) {
        validation.searchValue.message =
          'Enter a business debtor name to search'
      }
      if (searchValue?.length > 150) {
        validation.searchValue.message = 'Maximum 150 characters'
      }
      if (searchValue?.length < 2) {
        validation.searchValue.message = 'Must contain more than 1 character'
      }
      break
    case APISearchTypes.MHR_NUMBER:
    case APIMHRMapSearchTypes.MHRMHR_NUMBER:
      if (!searchValue) {
        validation.searchValue.message =
          'Enter a manufactured home registration number'
      }
      if (searchValue?.length > 6) {
        validation.searchValue.message = 'Maximum 6 digits'
      }
      if (searchValue && !numbersOnly.test(searchValue)) {
        validation.searchValue.message = 'Must contain numbers only'
      }
      break
    case APISearchTypes.AIRCRAFT:
      if (!searchValue) {
        validation.searchValue.message =
          'Enter an aircraft airframe D.O.T. number to search'
      } else {
        searchValue = searchValue?.replace(dash, '')
        if (searchValue?.length > 25) {
          validation.searchValue.message = 'Maximum 25 characters'
        }
      }
      break
    case APISearchTypes.REGISTRATION_NUMBER:
      if (!searchValue) {
        validation.searchValue.message = 'Enter a registration number to search'
      }
      if (searchValue && searchValue.length !== 7) {
        validation.searchValue.message =
          'Registration numbers contain 7 characters'
      }
      break
    case APIMHRMapSearchTypes.MHRORGANIZATION_NAME:
      if (!searchValue) {
        validation.searchValue.message = 'Enter an organization name to search'
      }
      if (searchValue?.length > 70) {
        validation.searchValue.message = 'Maximum 70 characters'
      }
      if (searchValue?.length < 2) {
        validation.searchValue.message = 'Must contain more than 1 character'
      }
      break
  }
  if (
    Object.keys(validation.searchValue)?.length ||
    Object.keys(validation.category)?.length
  ) { return validation } else return null
}

export function validateSearchRealTime (
  searchState: partialSearchState
): SearchValidationIF {
  const validation: SearchValidationIF = {
    category: {},
    searchValue: {}
  }
  let searchValue = searchState?.searchValue?.trim()
  const first = searchState?.searchValueFirst?.trim()
  const second = searchState?.searchValueSecond?.trim()
  const last = searchState?.searchValueLast?.trim()
  switch (searchState?.selectedSearchType?.searchTypeAPI) {
    case APISearchTypes.SERIAL_NUMBER:
      if (searchValue && specialCharsStrict.test(searchValue)) {
        validation.searchValue.message =
          "Serial numbers don't normally contain special characters"
      }
      if (searchValue?.length < 4) {
        validation.searchValue.popUp = [
          'This may not be a valid serial number.',
          'You can search using this number but you might not obtain any results (the search fee will be applied).',
          'Select "Search" to continue with this serial number.'
        ]
      }
      if (searchValue?.length > 25) {
        validation.searchValue.message = 'Maximum 25 characters'
      }
      break
    case APIMHRMapSearchTypes.MHRSERIAL_NUMBER:
      if (searchValue?.length > 20) {
        validation.searchValue.message = 'Maximum 20 characters'
      }
      break
    case APISearchTypes.INDIVIDUAL_DEBTOR:
    case APIMHRMapSearchTypes.MHROWNER_NAME:
      if (first && specialCharsLax.test(first)) {
        validation.searchValue.messageFirst =
          "Names don't normally contain special characters"
      } else if (first && first?.length > 15) {
        validation.searchValue.messageFirst = 'Maximum 15 characters'
      }
      if (second && specialCharsLax.test(second)) {
        validation.searchValue.messageSecond =
          "Names don't normally contain special characters"
      } else if (second && second?.length > 15) {
        validation.searchValue.messageSecond = 'Maximum 15 characters'
      }
      if (last && specialCharsLax.test(last)) {
        validation.searchValue.messageLast =
          "Names don't normally contain special characters"
      } else if (last?.length > 25) {
        validation.searchValue.messageLast = 'Maximum 25 characters'
      }
      break
    case APISearchTypes.BUSINESS_DEBTOR:
      if (searchValue?.length > 150) {
        validation.searchValue.message = 'Maximum 150 characters'
      }
      break
    case APISearchTypes.MHR_NUMBER:
      if (searchValue?.length > 6) {
        validation.searchValue.message = 'Maximum 6 digits'
      }
      if (searchValue && !numbersOnly.test(searchValue)) {
        validation.searchValue.message = 'Must contain numbers only'
      }
      // only want popup if there isn't an error message that will prevent searching already
      if (!validation.searchValue.message && searchValue?.length < 6) {
        validation.searchValue.popUp = [
          'This may not be a valid manufactured home registration number.',
          'You can search this number but you might not obtain useful results (the search fee will be applied)'
        ]
      }
      break
    case APISearchTypes.AIRCRAFT:
      searchValue = searchValue?.replace(dash, '')
      if (searchValue?.length > 25) {
        validation.searchValue.message = 'Maximum 25 characters'
      }
      // only want popup if there isn't an error message that will prevent searching already
      if (!validation.searchValue.message && searchValue?.length < 10) {
        validation.searchValue.popUp = [
          'This may not be a valid Aircraft Airframe D.O.T. number.',
          'You can search this number but you might not obtain useful results (the search fee will be applied)'
        ]
      }
      break
    case APISearchTypes.REGISTRATION_NUMBER:
      if (searchValue && searchValue.length !== 7) {
        validation.searchValue.message =
          'Registration numbers contain 7 characters'
      }
      break
    case APIMHRMapSearchTypes.MHRORGANIZATION_NAME:
      if (searchValue?.length > 70) {
        validation.searchValue.message = 'Maximum 70 characters'
      }
      if (specialCharsLax.test(searchValue)) {
        validation.searchValue.message =
          "Names don't normally contain special characters"
      }
      break
  }
  if (
    Object.keys(validation.searchValue)?.length ||
    Object.keys(validation.category)?.length
  ) { return validation } else return null
}

export function isSecuredPartyRestrictedList (regType: string): boolean {
  const restrictedList = [
    APIRegistrationTypes.LIEN_UNPAID_WAGES,
    APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
    APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
    APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
    APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
    APIRegistrationTypes.FOREST,
    APIRegistrationTypes.LOGGING_TAX,
    APIRegistrationTypes.CARBON_TAX,
    APIRegistrationTypes.PROVINCIAL_SALES_TAX,
    APIRegistrationTypes.RURAL_PROPERTY_TAX,
    APIRegistrationTypes.INCOME_TAX,
    APIRegistrationTypes.MOTOR_FUEL_TAX,
    APIRegistrationTypes.EXCISE_TAX,
    APIRegistrationTypes.MAINTENANCE_LIEN,
    APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
    APIRegistrationTypes.OTHER,
    APIRegistrationTypes.MINERAL_LAND_TAX,
    APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
    APIRegistrationTypes.SCHOOL_ACT,
    APIRegistrationTypes.MISC_MINERAL_RESOURCE,
    APIRegistrationTypes.CROWN_MINING_TAX,
    APIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
    APIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
    APIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
    APIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
    APIRegistrationTypes.TRANSITION_TAX_LIEN
  ]
  // @ts-ignore - it doesn't like the string comparison for some reason
  if (restrictedList.includes(regType)) {
    return true
  }
  return false
}
