/** Common Input Field Validation Functions. **/
export const useInputRules = () => {
  const maxLength = (maxLength: number): Array<Function> => {
    return [
      v => (v || '').length <= maxLength || `Maximum ${maxLength} characters`
    ]
  }

  const minLength = (minLength: number): Array<Function> => {
    return [
      v => (v || '').length >= minLength || `Minimum ${minLength} characters`
    ]
  }

  const isStringOrNumber = (): Array<Function> => {
    return [
      v => (v ? /^[a-zA-Z0-9_ ]*$/g.test(v) : true) || 'Invalid characters'
    ]
  }

  // check if entire value has empty spaces
  const isEmpty = (): Array<Function> => {
    return [
      v => !/^\s+$/g.test(v) || 'Invalid spaces'
    ]
  }

  const invalidSpaces = (): Array<Function> => {
    return [
      v => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
      v => !/\s$/g.test(v) || 'Invalid spaces' // trailing spaces
    ]
  }

  const required = (stringDescription: string): Array<Function> => {
    return [
      v => !!v || `${stringDescription}`
    ]
  }

  const isNumber = (numberType: string, maxDigits: number = null, maxValue: number = null): Array<Function> => {
    const maxDigitRule = new RegExp(`^\\d{1,${maxDigits}}$`)

    return [
      v => (v ? /^\d+$/g.test(v) : true) || `${numberType} must be a valid whole number (cannot contain decimals)`,
      v => ((v && maxDigits) ? maxDigitRule.test(v) : true) || `Maximum ${maxDigits} characters`,
      v => ((v && maxValue) ? v < maxValue : true) || `${numberType} must be less than ${maxValue}`
    ]
  }

  // Check if string starts with any of the search values
  const startsWith = (errorMessage: string, ...searchValues: string[]): Array<Function> => {
    const values = '^' + Object.values({ ...searchValues }).join('|^')
    const exp = new RegExp(values, 'g')
    return [
      (v:any) => !!(v || '').match(exp) || errorMessage
    ]
  }

  // Check if value is a greater than maxNumber
  const graterThan = (maxNumber: number, errorMessage: string) => {
    return [
      (v:number) => !v || v <= maxNumber || errorMessage
    ]
  }

  /** Create a custom rules array use predefined rules. **/
  const customRules = (...rules: any) => {
    return [].concat(...rules)
  }

  return {
    customRules,
    isEmpty,
    invalidSpaces,
    isStringOrNumber,
    required,
    isNumber,
    startsWith,
    graterThan,
    minLength,
    maxLength
  }
}
