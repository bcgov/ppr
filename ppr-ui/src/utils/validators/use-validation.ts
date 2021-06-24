export const useValidation = () => {
  const resetError = (fieldName, errors) => {
    console.log(errors)
    errors[fieldName] = {
      type: '',
      succeeded: true,
      message: ''
    }
    return errors
  }
  return {
    resetError
  }
}
