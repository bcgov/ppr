import { ref } from '@vue/composition-api'
import { createDefaultValidationResult } from '@lemoncode/fonk'

const createEmptyErrors = () => ({
  businessName: createDefaultValidationResult(),
  first: createDefaultValidationResult(),
  last: createDefaultValidationResult(),
  year: createDefaultValidationResult(),
  month: createDefaultValidationResult(),
  day: createDefaultValidationResult(),
  address: createDefaultValidationResult()
})

export const useDebtorValidation = () => {
  const errors = ref(createEmptyErrors())

  const validateName = (isBusiness, form) => {
    if (isBusiness === true) {
      if (form.businessName.length === 0) {
        errors.value.businessName = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a business name'
        }
      } else {
        resetError('businessName')
      }
    } else {
      if (form.personName.first.length === 0) {
        errors.value.first = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a first name'
        }
      } else {
        resetError('first')
      }
      if (form.personName.last.length === 0) {
        errors.value.last = {
          type: 'NAME',
          succeeded: false,
          message: 'Please enter a last name'
        }
      } else {
        resetError('last')
      }
    }
  }

  const validateBirthdate = (year, month, day) => {
    if (year > 0 || month > 0 || day > 0) {
      if (year < 1800 || year > new Date().getFullYear()) {
        errors.value.year = {
          type: 'YEAR',
          succeeded: false,
          message: 'Please enter a valid year'
        }
      } else {
        resetError('year')
      }

      if (!month || month < 1 || month > 12) {
        errors.value.month = {
          type: 'MONTH',
          succeeded: false,
          message: 'Please enter a valid month'
        }
      } else {
        resetError('month')
      }

      if (day < 1 || day > 31) {
        errors.value.day = {
          type: 'DAY',
          succeeded: false,
          message: 'Please enter a valid day'
        }
      } else {
        resetError('day')
      }
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
    validateName(currentIsBusiness.value, currentDebtor.value)
    if (currentIsBusiness.value === true) {
      return errors.value.businessName.succeeded && errors.value.address.succeeded && errors.value.address.succeeded
    } else {
      return (
        errors.value.first.succeeded &&
        errors.value.last.succeeded &&
        errors.value.year.succeeded &&
        errors.value.month.succeeded &&
        errors.value.day.succeeded &&
        errors.value.address.succeeded
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
   * @param addressToValidate the address to set the validity of
   * @param isValid whether the address is valid
   */
  const updateValidity = (valid: boolean): void => {
    errors.value.address.succeeded = valid
  }

  return {
    errors,
    updateValidity,
    validateName,
    validateBirthdate,
    validateDebtorForm
  }
}
