import { useStore } from '@/store/store'
import type {
  mhrInfoValidationStateIF,
  MhrRegistrationHomeOwnerIF
} from '@/interfaces'
import { computed } from 'vue'
import { useHomeOwners, useMhrInformation, useTransferOwners, useTransportPermits } from '@/composables'
import { ActionTypes, LocationChangeTypes } from '@/enums'
import { storeToRefs } from 'pinia'

export const useMhrInfoValidation = (validationState: mhrInfoValidationStateIF) => {
  const {
    hasLien,
    isRoleStaffReg,
    isRoleStaffSbc,
    getMhrTransportPermit,
    hasUnsavedChanges
  } = storeToRefs(useStore())
  const {
    isGlobalEditingMode,
    getGroupById
  } = useHomeOwners(true)
  const {
    isTransferDueToDeath
  } = useTransferOwners()
  const {
    getLienInfo
  } = useMhrInformation()
  const {
    isNotManufacturersLot,
    isAmendLocationActive,
    isCancelChangeLocationActive,
    hasAmendmentChanges,
    isActiveHomeOutsideBc,
    isNewPermitActive
  } = useTransportPermits()


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
    return (!isTransferDueToDeath.value || owner.action !== ActionTypes.REMOVED) ||
      (
        // Deceased Owner validations
        (owner.hasDeathCertificate && !!owner.deathCertificateNumber && owner.deathCertificateNumber?.length <= 20 &&
          !!owner.deathDateTime) ||
        // Historical Owner validations
        (!!owner.deathCorpNumber && owner.deathCorpNumber?.length <= 20 && !!owner.deathDateTime)
      )
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
      (isRoleStaffReg.value ? validationState.isDocumentIdValid : true) &&
      validationState.isValidTransferType &&
      validationState.isValidTransferOwners &&
      validationState.isTransferDetailsValid &&
      (!hasLien.value || getLienInfo().isSubmissionAllowed)
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

  const isValidTransportPermit = computed((): boolean => {

    if (isCancelChangeLocationActive.value) {
      return (
        isRoleStaffReg.value ? validationState.isDocumentIdValid : true
      )
    }

    const isSameParkLocation =
      getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK

    if (isSameParkLocation) {
      return (
        (isRoleStaffReg.value ? validationState.isDocumentIdValid : true) &&
        (isAmendLocationActive.value ? true : validationState.isLocationChangeTypeValid) &&
        validationState.isNewPadNumberValid &&
        // validate changes made for amend transport permit
        (isAmendLocationActive.value ? hasAmendmentChanges.value : true)
      )
    } else {
      return (
        (isRoleStaffReg.value ? validationState.isDocumentIdValid : true) &&
        ((isAmendLocationActive.value || isNewPermitActive.value) ? true : validationState.isLocationChangeTypeValid) &&
        validationState.isHomeLocationTypeValid &&
        validationState.isHomeCivicAddressValid &&
        validationState.isHomeLandOwnershipValid &&
        // no tax certificate validation for amend transport permits
        ((isNotManufacturersLot.value && !isAmendLocationActive.value && !isActiveHomeOutsideBc.value)
          ? validationState.isTaxCertificateValid : true) &&
        // validate changes made for amend transport permit
        (isAmendLocationActive.value ? hasAmendmentChanges.value : true)
      )
    }
  })

  const isValidTransportPermitReview = computed((): boolean => {

    return (
      ((isRoleStaffReg.value || isRoleStaffSbc.value) ? validationState.isSubmittingPartyValid : true) &&
      validationState.isRefNumValid &&
      validationState.isCompletionConfirmed &&
      validationState.isAuthorizationValid &&
      (isRoleStaffReg.value ? validationState.isStaffPaymentValid : true)
    )
  })

  const isValidExtendTransportPermit = computed((): boolean => {
    return (
      (isRoleStaffReg.value ? validationState.isDocumentIdValid : true) &&
      ((isNotManufacturersLot.value && !isAmendLocationActive.value && !isActiveHomeOutsideBc.value)
        ? validationState.isTaxCertificateValid : true)
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
        document.getElementById(forceTarget)?.scrollIntoView({ behavior: 'smooth' })
        return
      }

      if (scrollToTop) {
        document?.getElementById('mhr-information-header')?.scrollIntoView({ behavior: 'smooth' })
        return
      }
      document?.getElementsByClassName('border-error-left').length > 0 &&
      document?.getElementsByClassName('border-error-left')[0]
        .scrollIntoView({ block: 'start', inline: 'nearest', behavior: 'smooth' })
    }, 500)
  }

  /** Reset the validation state to default **/
  const resetValidationState = (): void => {
     
    Object.keys(validationState).forEach(flag => validationState[flag] = false)
  }

  return {
    setValidation,
    getInfoValidation,
    isValidTransfer,
    isValidDeceasedOwner,
    isValidDeceasedOwnerGroup,
    isValidTransferReview,
    isValidTransportPermit,
    isValidTransportPermitReview,
    isValidExtendTransportPermit,
    scrollToFirstError,
    resetValidationState
  }
}
