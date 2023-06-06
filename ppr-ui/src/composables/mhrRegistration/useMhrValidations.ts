import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'

export const useMhrValidations = (validationState: any) => {
  /** Set specified flag */
  const setValidation = (section: MhrSectVal, component: MhrCompVal, isValid: boolean): void => {
    // Only sets specified flag if the section and component are part of the validation model
    if (validationState[section]?.value[component] !== undefined) {
      validationState[section].value[component] = isValid
    }
  }

  /** Get specified flag */
  const getValidation = (section: MhrSectVal, component: MhrCompVal): boolean => {
    return validationState[section].value[component]
  }

  /** Is true when all flags are true in specified section. */
  const getStepValidation = (section: MhrSectVal): boolean => {
    // If section is not part of validation model return true
    if (!validationState[section]) return true
    return Object.values(validationState[section].value).every(val => val)
  }

  /** Is true when app-wide validations is flagged and specified component is invalid . */
  const getSectionValidation = (section: MhrSectVal, component: MhrCompVal): boolean => {
    return validationState.reviewConfirmValid.value.validateSteps && !validationState[section].value[component]
  }

  /** Reset submission validations to default . */
  const resetAllValidations = (): void => {
    // Gets all sections in model
    const sections = Object.keys(validationState) as MhrSectVal[]
    for (const section of sections) {
      // Gets all components for the specifc section
      const components = Object.keys(validationState[section].value) as MhrCompVal[]
      // Sets all components to false
      for (const component of components) {
        setValidation(section, component, false)
      }
    }
    // Default for ADD_EDIT_OWNERS_VALID -> OWNERS_VALID is true
    if (sections.includes(MhrSectVal.ADD_EDIT_OWNERS_VALID)) {
      setValidation(MhrSectVal.ADD_EDIT_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
    }
  }

  /** Is true when input field ref is in error. */
  const hasError = (ref: any): boolean => {
    return ref?.hasError
  }

  /** Scroll to first SECTION tag that is invalid in specified flag block. */
  const scrollToInvalid =
    async (flagSection: MhrSectVal, viewId: string, optionalFlags: Array<boolean> = null): Promise<boolean> => {
      // Create an array of the _ordered_ validation flags
      const flagBlockArr = Object.keys(validationState[flagSection].value)
        .map(key => validationState[flagSection].value[key])

      // Prepend optional flags to array (ie for review pages)
      if (optionalFlags) flagBlockArr.unshift(...optionalFlags)

      // Find the _first_ corresponding Section that is invalid in the specified view
      const view = document.getElementById(viewId)
      const invalidComponent = view.getElementsByTagName('section')[flagBlockArr.indexOf(false)]

      // If there is an invalid component, scroll to it
      if (invalidComponent) {
        setTimeout(() => {
          invalidComponent.scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
        }, 500)
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
    resetAllValidations,
    scrollToInvalid
  }
}
