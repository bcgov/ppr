/** Common Input Field Validation Functions. **/
export const useInputRules = () => {
  const maxLength = (maxLength: number, isMaxLengthForDigits: boolean = false): Array<Function> => {
    return [
      v => (v || '').toString().length <= maxLength ||
        `Maximum ${maxLength} ${isMaxLengthForDigits ? 'digits' : 'characters'}`
    ]
  }

  const minLength = (minLength: number, isMinLengthForDigits: boolean = false): Array<Function> => {
    return [
      v => (v || '').length >= minLength || `Minimum ${minLength} ${isMinLengthForDigits ? 'digits' : 'characters'}`
    ]
  }

  const isLettersOnly = (customMsg: string = null): Array<Function> => {
    return [
      v => (v ? /^[a-zA-Z_ ]*$/g.test(v) : true) || `Enter letters only. ${customMsg}`
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

  const isNumber = (
    numberType: string = null,
    maxDigits: number = null,
    maxValue: number = null,
    customMsg: string = null
  ): Array<Function> => {
    const maxDigitRule = new RegExp(`^\\d{1,${maxDigits}}$`)

    return [
      v => ((v && numberType) ? /^\d+$/g.test(v) : true) || `${numberType} must be a valid whole number (cannot contain decimals)`,
      v => ((v && maxDigits) ? maxDigitRule.test(v) : true) || `Maximum ${maxDigits} characters`,
      v => ((v && maxValue) ? v < maxValue : true) || `${numberType} must be less than ${maxValue}`,
      v => (v ? /^\d+$/g.test(v) : true) || `${customMsg || 'Must contain numbers only'}`
    ]
  }

  const isEmailOrEmpty = (): Array<Function> => [
    (v: string) => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return !v || pattern.test(v) || 'Enter a valid email address'
    }
  ]

  const isPhone = (
    maxDigits: number = null,
    customMsg: string = null
  ): Array<Function> => {
    return [
      v => (v ? /^\d+$/g.test(v.replace('(', '').replace(') ', '').replace('-', '')) : true) || `${customMsg || 'Enter numbers only'}`,
      v => ((v && maxDigits) ? v.length >= maxDigits : true) || 'Minimum 10 digits'
    ]
  }

  // Check if string starts with any of the search values
  const startsWith = (searchValues: Array<string>, errorMessage: string): Array<Function> => {
    const values = '^' + searchValues.join('|^')
    const exp = new RegExp(values, 'g')
    return [
      (v: any) => !!(v || '').match(exp) || errorMessage
    ]
  }

  // Check if value is a greater than maxNumber
  const greaterThan = (maxNumber: number, errorMessage: string) => {
    return [
      (v: number) => !v || v <= maxNumber || errorMessage
    ]
  }

  const lessThan = (minNumber: number, errorMessage: string) => {
    return [
      (v: number) => !v || v >= minNumber || errorMessage
    ]
  }

  /** Create a custom rules array use predefined rules. **/
  const customRules = (...rules: any) => {
    return [].concat(...rules)
  }

  return {
    customRules,
    isEmailOrEmpty,
    isEmpty,
    invalidSpaces,
    isLettersOnly,
    isStringOrNumber,
    required,
    isNumber,
    startsWith,
    greaterThan,
    lessThan,
    minLength,
    maxLength,
    isPhone
  }
}
