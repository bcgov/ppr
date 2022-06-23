export const useInputRules = () => {
  const optionalStringRules = (): Array<Function> => {
    return [
      v => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
      v => !/\s$/g.test(v) || 'Invalid spaces' // trailing spaces
    ]
  }

  const requiredStringRules = (stringDescription: string): Array<Function> => {
    return [
      v => !!v || `A ${stringDescription} is required`,
      v => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
      v => !/\s$/g.test(v) || 'Invalid spaces' // trailing spaces
    ]
  }

  const optionalNumberRules = (): Array<Function> => {
    return [
      v => (v ? /^\d+$/g.test(v) : true) || 'Invalid characters',
      v => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
      v => !/\s$/g.test(v) || 'Invalid spaces' // trailing spaces
    ]
  }

  const requiredNumberRules = (numberDescription: string): Array<Function> => {
    return [
      v => !!v || `A ${numberDescription} is required`,
      v => /^\d+$/g.test(v) || 'Invalid characters',
      v => !/^\s/g.test(v) || 'Invalid spaces', // leading spaces
      v => !/\s$/g.test(v) || 'Invalid spaces' // trailing spaces
    ]
  }

  const maxLengthRules = (maxLength: number): Array<Function> => {
    return [v => v.length <= maxLength || `Maximum ${maxLength} characters`]
  }

  return {
    optionalStringRules,
    requiredStringRules,
    optionalNumberRules,
    requiredNumberRules,
    maxLengthRules
  }
}
