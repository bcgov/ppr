import { useGetters } from 'vuex-composition-helpers'
// @ts-ignore
import { mhrInfoValidationState, MhrRegistrationHomeOwnerIF, mhrInfoValidationStateIF } from '@/interfaces'
import { computed } from '@vue/composition-api'
import { useHomeOwners } from '@/composables'

export const useMhrInfoValidation = (validationState: mhrInfoValidationStateIF) => {
  const {
    hasLien,
    isRoleStaffReg,
    hasUnsavedChanges
  } = useGetters<any>([
    'hasLien',
    'isRoleStaffReg',
    'hasUnsavedChanges'
  ])

  const {
    isGlobalEditingMode
  } = useHomeOwners(true)

  /** Set specified flag */
  const setValidation = (propertyKey: string, isValid: boolean): void => {
    validationState[propertyKey] = isValid
  }

  /** Get specified flag */
  const getValidation = (propertyKey: string): boolean => {
    return validationState[propertyKey]
  }

  /** Returns true when the Transfer is complete and valid **/
  const isValidTransfer = computed((): boolean => {
    return (
      hasUnsavedChanges.value &&
      !isGlobalEditingMode.value &&
      validationState.isValidTransferType &&
      validationState.isValidTransferOwners &&
      validationState.isTransferDetailsValid &&
      !hasLien.value
    )
  })

  /** Returns true when the Transfer Review is complete and valid **/
  const isValidTransferReview = computed((): boolean => {
    return (
      (isRoleStaffReg.value ? validationState.isSubmittingPartyValid : true) &&
      validationState.isRefNumValid &&
      validationState.isCompletionConfirmed &&
      validationState.isAuthorizationValid &&
      (isRoleStaffReg.value ? validationState.isStaffPaymentValid : true)
    )
  })

  /** Scroll to first designated error on Information or Review page **/
  const scrollToFirstError = async (scrollToTop: boolean = false): Promise<void> => {
    setTimeout(() => {
      if (scrollToTop) {
        document.getElementById('mhr-information-header').scrollIntoView({ behavior: 'smooth' })
        return
      }
      document.getElementsByClassName('border-error-left').length > 0 &&
      document.getElementsByClassName('border-error-left')[0]
        .scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
    }, 10)
  }

  return {
    setValidation,
    getValidation,
    isValidTransfer,
    isValidTransferReview,
    scrollToFirstError
  }
}
