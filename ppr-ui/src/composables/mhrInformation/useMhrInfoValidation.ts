import { useGetters } from 'vuex-composition-helpers'
// @ts-ignore
import {
  mhrInfoValidationStateIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'
import { computed } from '@vue/composition-api'
import { useHomeOwners, useTransferOwners } from '@/composables'
import { ActionTypes } from '@/enums'

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
    isGlobalEditingMode,
    getGroupById
  } = useHomeOwners(true)
  const {
    isTransferDueToDeath
  } = useTransferOwners()

  /** Set specified flag */
  const setValidation = (propertyKey: string, isValid: boolean): void => {
    validationState[propertyKey] = isValid
  }

  /** Get specified flag */
  const getInfoValidation = (propertyKey: string): boolean => {
    return validationState[propertyKey]
  }

  /** Returns true when the specified owner is a valid deceased owner **/
  const isValidDeceasedOwner = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    return (!isTransferDueToDeath.value || owner.action !== ActionTypes.REMOVED) || (owner.hasDeathCertificate &&
      !!owner.deathCertificateNumber && !!owner.deathDateTime)
  }

  /**  Returns true when the specific group is a valid deceased owner group **/
  const isValidDeceasedOwnerGroup = (groupId: number): any => {
    return getGroupById(groupId)?.owners?.every(owner => isValidDeceasedOwner(owner))
  }

  /** Returns true when the Transfer is complete and valid **/
  const isValidTransfer = computed((): boolean => {
    return (
      hasUnsavedChanges.value &&
      !isGlobalEditingMode.value &&
      validationState.isValidTransferType &&
      validationState.isValidTransferOwners &&
      (isTransferDueToDeath.value || validationState.isTransferDetailsValid) &&
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

  /**
   * Scroll to first designated error on Information or Review page
   * @param scrollToTop Force scroll to top of MHR
   * @param forceTarget A custom ID to force scroll too.
   * @return void
   * **/
  const scrollToFirstError = async (scrollToTop: boolean = false, forceTarget: string = ''): Promise<void> => {
    setTimeout(() => {
      if (forceTarget) {
        document.getElementById(forceTarget).scrollIntoView({ behavior: 'smooth' })
        return
      }

      if (scrollToTop) {
        document.getElementById('mhr-information-header').scrollIntoView({ behavior: 'smooth' })
        return
      }
      document.getElementsByClassName('border-error-left').length > 0 &&
      document.getElementsByClassName('border-error-left')[0]
        .scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
    }, 10)
  }

  /** Reset the validation state to default **/
  const resetValidationState = (): void => {
    // eslint-disable-next-line no-return-assign
    Object.keys(validationState).forEach(flag => validationState[flag] = false)
  }

  return {
    setValidation,
    getInfoValidation,
    isValidTransfer,
    isValidDeceasedOwner,
    isValidDeceasedOwnerGroup,
    isValidTransferReview,
    scrollToFirstError,
    resetValidationState
  }
}
