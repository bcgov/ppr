import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'

export const useMhrValidations = (validationState: any) => {
  /** Set specified flag */
  const setValidation = (section: MhrSectVal, component: MhrCompVal, isValid: boolean): void => {
    validationState[section].value[component] = isValid
  }

  /** Get specified flag */
  const getValidation = (section: MhrSectVal, component: MhrCompVal): boolean => {
    return validationState[section].value[component]
  }

  /** Is true when app-wide validations is flagged and specified component is invalid . */
  const getSectionValidation = (section: MhrSectVal, component: MhrCompVal): boolean => {
    return validationState.reviewConfirmValid.value.validateApp && !validationState[section].value[component]
  }

  /** Is true when all flags are true in specified section. */
  const getStepValidation = (section: MhrSectVal): boolean => {
    return Object.values(validationState[section].value).every(val => val)
  }

  /** Is true when input field ref is in error. */
  const hasError = (ref: any): boolean => {
    return ref.hasError
  }

  /** Scroll to first SECTION tag that is invalid in specified flag block. */
  const scrollToInvalid = async (flagSection: MhrSectVal, viewId: string): Promise<boolean> => {
    // Create an array of the _ordered_ validation flags
    const flagBlockArr = Object.keys(validationState[flagSection].value)
      .map(key => validationState[flagSection].value[key])

    // Find the _first_ corresponding Section that is invalid in the specified view
    const view = document.getElementById(viewId)
    const invalidComponent = view.getElementsByTagName('section')[flagBlockArr.indexOf(false)]

    // If there is an invalid component, scroll to it
    if (invalidComponent) {
      await invalidComponent.scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
      return false
    }
    return true
  }

  return {
    MhrCompVal,
    MhrSectVal,
    hasError,
    setValidation,
    getValidation,
    getSectionValidation,
    getStepValidation,
    scrollToInvalid
  }
}
