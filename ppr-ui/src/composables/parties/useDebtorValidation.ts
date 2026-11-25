import { ref } from 'vue'
import { createDefaultValidationResult } from '@lemoncode/fonk'
import { useValidation } from '@/utils/validators/use-validation'
import { isValidCalendarDate } from '@/utils/birthdate-helper'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  middle: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  year: createDefaultValidationResult(),
  month: createDefaultValidationResult(),
  day: createDefaultValidationResult(),
  emailAddress: createDefaultValidationResult(),
  address: createDefaultValidationResult()
})

const {
  validateName
} = useValidation()

export const useDebtorValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateBirthdate = (year, month, day) => {
    // reset errors before validation
    resetError('year')
    resetError('month')
    resetError('day')
    if (year > 0 || month > 0 || day > 0) {
      if ((!year) || !validBirthdateNumber('' + year) || year < 1800 || year > new Date().getFullYear()) {
        errors.value.year = {
          type: 'YEAR',
          succeeded: false,
          message: 'Please enter a valid year'
        }
      }

      if (!month || month < 1 || month > 12) {
        errors.value.month = {
          type: 'MONTH',
          succeeded: false,
          message: 'Please enter a valid month'
        }
      }

      if (
        (!day) || !validBirthdateNumber('' + day) || day < 1 || day > 31 ||
        // day must exist in the month (e.g. no Feb 30 or Apr 31);
        // without a valid year, check against a leap year: Feb 30 is never valid, Feb 29 might be
        (errors.value.month.succeeded &&
          !isValidCalendarDate(errors.value.year.succeeded ? Number(year) : 2000, Number(month), Number(day)))
      ) {
        errors.value.day = {
          type: 'DAY',
          succeeded: false,
          message: 'Please enter a valid day'
        }
      }
    }
  }

  /**
   * Validate the birthdate while the user is still entering it.
   * Same rules as validateBirthdate, but a field the user hasn't filled in yet is not flagged.
   * A year is treated as unfinished until it has 4 characters, unless yearDone is set (e.g. on blur).
   */
  const validateBirthdateLive = (year, month, day, yearDone = false) => {
    validateBirthdate(year, month, day)
    const yearStr = year ? String(year) : ''
    if (!yearStr || (!yearDone && yearStr.length < 4)) resetError('year')
    if (!month) resetError('month')
    if (!day) resetError('day')
  }

  const validateEmail = (email: string) => {
    let isValid = true
    if (email) {
       
      const VALID_FORMAT = new RegExp(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      )
      isValid = VALID_FORMAT.test(email)
    }
    if (!isValid) {
      errors.value.emailAddress = {
        type: 'EMAIL',
        succeeded: false,
        message: 'Please enter a valid email address'
      }
    } else {
      resetError('emailAddress')
    }
  }

  const validateDebtorForm = (
    currentIsBusiness,
    currentDebtor,
    year,
    month,
    day
  ): boolean => {
    validateBirthdate(year.value, month.value, day.value)
    validateName(currentIsBusiness.value, currentDebtor.value, errors)
    validateEmail(currentDebtor.value.emailAddress)
    if (currentIsBusiness.value === true) {
      return (
        errors.value.businessName.succeeded &&
        errors.value.address.succeeded &&
        errors.value.emailAddress.succeeded
      )
    } else {
      return (
        errors.value.first.succeeded &&
        errors.value.middle.succeeded &&
        errors.value.last.succeeded &&
        errors.value.year.succeeded &&
        errors.value.month.succeeded &&
        errors.value.day.succeeded &&
        errors.value.address.succeeded &&
        errors.value.emailAddress.succeeded
      )
    }
  }

  const resetError = fieldName => {
    errors.value[fieldName] = {
      type: '',
      succeeded: true,
      message: ''
    }
  }

  /**
   * Handles validity events from address sub-components.
   * @param valid whether the address is valid
   */
  const updateValidity = (valid: boolean): void => {
    errors.value.address.succeeded = valid
  }

  /**
   * A simple check that a birthdate year or day string is an integer.
   * @param number Number as a string to verify.
   * @returns True if number is an integer.
   */
  const validBirthdateNumber = (number: string): boolean => {
    if (number.length !== 0 && number.trim().length === 0) {
      return false
    }
    return /^\d+$/.test(number)
  }

  return {
    errors,
    updateValidity,
    validateName,
    validateBirthdate,
    validateBirthdateLive,
    validateEmail,
    validateDebtorForm
  }
}
