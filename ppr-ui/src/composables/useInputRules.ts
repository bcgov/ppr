/** Common Input Field Validation Functions. **/
export const useInputRules = () => {
  const maxLength = (maxLength: number): Array<Function> => {
    return [
      v => v.length <= maxLength || `Maximum ${maxLength} characters`
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

  const isNumber = (): Array<Function> => {
    return [
      v => (v ? /^\d+$/g.test(v) : true) || 'Invalid number'
    ]
  }

  const customRules = (...rules: any) => {
    return [].concat(...rules)
  }

  return {
    customRules,
    invalidSpaces,
    required,
    isNumber,
    maxLength
  }
}
