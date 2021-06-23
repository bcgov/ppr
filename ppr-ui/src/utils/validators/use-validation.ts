export const useValidation = () => {
  const resetError = (fieldName, errors) => {
    errors.value[fieldName] = {
      type: '',
      succeeded: true,
      message: ''
    }
    return errors
  }
}
