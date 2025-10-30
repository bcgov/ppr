import type { FeeSummaryTypes } from '@/composables/fees/enums'
import { storeToRefs } from 'pinia'
import { useConnectFeeStore } from '@/store/connectFee'
import { RegistrationFees } from '@/resources/feeSchedule'

export const useConnectFeesHandler = () => {
  const {
    fees,
    feeOptions
  } = storeToRefs(useConnectFeeStore())
  const { setFees } = useConnectFeeStore()
  const { isSearchCertified, isRoleStaff, getStaffPayment,  } = storeToRefs(useStore())

  /** Set the registration fees */
  const setRegistrationFees = (registrationFeeType: FeeSummaryTypes): void => {
    setFees({[registrationFeeType]: { ...RegistrationFees[registrationFeeType] }})
  }

  /** Set the registration fees */
  const setRegistrationFeeDesc = (registrationFeeType: FeeSummaryTypes, filingType: string): void => {
    setFees({[registrationFeeType]: {
      ...RegistrationFees[registrationFeeType],
        filingTypeCode: filingType
    }})
  }

  /** Set the registration fees for combination charges */
  const setRegistrationComboFees = (registrationFeeType: FeeSummaryTypes, quantity: number = null): void => {
    setFees({
      ...fees.value,
      ...(registrationFeeType && {
        [registrationFeeType]: {
          ...RegistrationFees[registrationFeeType],
          quantity: quantity,
          waived: fees.value[registrationFeeType]?.waived,
          total: RegistrationFees[registrationFeeType].filingFees * quantity,
        }
      })
    })
  }

  /** Waive the fees (no fee) */
  const waiveFees = (registrationFeeType: FeeSummaryTypes, isNoFee: boolean): void => {
    const updatedFees = { ...fees.value }
    Object.keys(updatedFees).forEach(key => {
      updatedFees[key] = {
        ...updatedFees[key],
        filingFees: isNoFee ? 0 : RegistrationFees[key]?.filingFees ?? updatedFees[key].filingFees,
        waived: isNoFee
      }
    })
    setFees(updatedFees)
  }

  /** Set the quantity of the specified fee type */
  const setFeeQuantity = (registrationFeeType: FeeSummaryTypes, quantity: number): void => {
    setFees({
      ...fees.value,
      [registrationFeeType]: {
        ...RegistrationFees[registrationFeeType],
        quantity: quantity,
        waived: fees.value[registrationFeeType]?.waived,
        total: RegistrationFees[registrationFeeType]?.filingFees * quantity +
          RegistrationFees[registrationFeeType]?.serviceFees,
        priorityFees: fees.value[registrationFeeType]?.priorityFees ?? 0,
        certifiedFees: fees.value[registrationFeeType]?.certifiedFees ?? 0
      }
    })
  }

  /** Set the priority fee (ie $100) */
  const setPriority = async (registrationFeeType: FeeSummaryTypes, isPriority: boolean): Promise<void> => {
    setFees({
      ...fees.value,
      ...(registrationFeeType && {
        [registrationFeeType]: {
          ...fees.value[registrationFeeType],
          priorityFees: isPriority ? 100 : 0
        }
      })
    })
  }

  /** Set the certified fees */
  const setCertifiedSearchFee = (registrationFeeType: FeeSummaryTypes, isCertified): void => {
    setFees({
      ...fees.value,
      ...(registrationFeeType && {
        [registrationFeeType]: {
          ...fees.value[registrationFeeType],
          certifiedFees: isCertified ? 25 : 0
        }
      })
    })
  }

  watch(() => getStaffPayment.value?.option, async (option: number) => {
    if (isRoleStaff.value) {
      for (const key of Object.keys(fees.value)) {
        await waiveFees(key as FeeSummaryTypes, option === 0)
      }
    }
  })

  watch(() => getStaffPayment.value?.isPriority, async (isPriority: boolean) => {
    if (isRoleStaff.value) {
      feeOptions.value.showPriorityFees = isPriority
      await setPriority(Object.keys(fees.value)[0] as FeeSummaryTypes, isPriority)
    }
  })

  watch(() => isSearchCertified.value, async (isCertified: boolean) => {
    if (isRoleStaff.value) {
      feeOptions.value.showCertifiedSearchFees = isCertified
      await setCertifiedSearchFee(Object.keys(fees.value)[0] as FeeSummaryTypes, isCertified)
    }
  })

  return {
    waiveFees,
    setFeeQuantity,
    setRegistrationFees,
    setRegistrationFeeDesc,
    setRegistrationComboFees
  }
}
