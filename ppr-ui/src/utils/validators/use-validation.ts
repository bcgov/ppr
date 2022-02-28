export const useValidation = () => {
  const resetError = (fieldName, errors) => {
    errors[fieldName] = {
      type: '',
      succeeded: true,
      message: ''
    }
    return errors
  }

  const validateName = (isBusiness, form, localErrors) => {
    if (isBusiness === true) {
      validateBusinessName(form, localErrors.value)
    } else {
      form.personName.first = form.personName.first.trim()
      form.personName.last = form.personName.last.trim()
      validateFirstName(form, localErrors.value)
      validateLastName(form, localErrors.value)
    }
  }

  const validateBusinessName = (form, localErrors) => {
    form.businessName = form.businessName.trim()
    if (form.businessName.length === 0) {
      localErrors.businessName = {
        type: 'NAME',
        succeeded: false,
        message: 'Please enter a business name'
      }
    } else if (form.businessName.length > 150) {
      localErrors.businessName = {
        type: 'NAME',
        succeeded: false,
        message: 'Maximum 150 characters'
      }
    } else {
      localErrors.businessName = {
        type: '',
        succeeded: true,
        message: ''
      }
    }
  }

  const validateFirstName = (form, localErrors) => {
    if (form.personName.first.length === 0) {
      localErrors.first = {
        type: 'NAME',
        succeeded: false,
        message: 'Please enter a first name'
      }
    } else if (form.personName.first.length > 50) {
      localErrors.first = {
        type: 'NAME',
        succeeded: false,
        message: 'Maximum 50 characters'
      }
    } else {
      localErrors.first = {
        type: '',
        succeeded: true,
        message: ''
      }
    }
  }

  const validateLastName = (form, localErrors) => {
    if (form.personName.last.length === 0) {
      localErrors.last = {
        type: 'NAME',
        succeeded: false,
        message: 'Please enter a last name'
      }
    } else if (form.personName.last.length > 50) {
      localErrors.last = {
        type: 'NAME',
        succeeded: false,
        message: 'Maximum 50 characters'
      }
    } else {
      localErrors.last = {
        type: '',
        succeeded: true,
        message: ''
      }
    }
  }

  return {
    resetError,
    validateName,
    validateBusinessName,
    validateFirstName,
    validateLastName
  }
}
