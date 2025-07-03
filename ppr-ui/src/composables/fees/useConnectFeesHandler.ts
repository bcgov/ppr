import type { FeeSummaryTypes } from '@/composables/fees/enums'
import { storeToRefs } from 'pinia'
import { useConnectFeeStore } from '@/store/connectFee'
import { RegistrationFees } from '@/resources/feeSchedule'


export const useConnectFeesHandler = () => {
  const {
    fees,
    feeOptions,
    userSelectedPaymentMethod
  } = storeToRefs(useConnectFeeStore())
  const { setFees } = useConnectFeeStore()
  const { isRoleStaff, getStaffPayment } = storeToRefs(useStore())

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
          total: RegistrationFees[registrationFeeType].filingFees * quantity
        }
      })
    })
  }

  /** Waive the fees (no fee) */
  const waiveFees = (registrationFeeType: FeeSummaryTypes, isNoFee: boolean): void => {
    setFees({
      [registrationFeeType]: {
        ...fees.value[registrationFeeType],
        filingFees: isNoFee ? 0 : RegistrationFees[registrationFeeType].filingFees,
        waived: isNoFee
      }
    })
  }

  /** Set the quantity of the specified fee type */
  const setFeeQuantity = (registrationFeeType: FeeSummaryTypes, quantity: number): void => {
    setFees({
      ...fees.value,
      [registrationFeeType]: {
        ...RegistrationFees[registrationFeeType],
        quantity: quantity,
        total: RegistrationFees[registrationFeeType]?.filingFees * quantity +
          RegistrationFees[registrationFeeType]?.serviceFees
      }
    })
  }

  /** Set the priority fee (ie $100) */
  const setPriority = async (registrationFeeType: FeeSummaryTypes, isPriority: boolean): Promise<void> => {
    setFees({
      [registrationFeeType]: {
        ...RegistrationFees[registrationFeeType],
        priorityFees: isPriority ? 100 : 0
      }
    })
  }

  watch(() => getStaffPayment.value?.option, async (option: number) => {
    if (isRoleStaff.value) {
      await waiveFees(Object.keys(fees.value)[0] as FeeSummaryTypes, option === 0)
    }
  })

  watch(() => getStaffPayment.value?.isPriority, async (isPriority: boolean) => {
    if (isRoleStaff.value) {
      feeOptions.value.showPriorityFees = isPriority
      await setPriority(Object.keys(fees.value)[0] as FeeSummaryTypes, isPriority)
    }
  })

  return {
    setFeeQuantity,
    setRegistrationFees,
    setRegistrationFeeDesc,
    setRegistrationComboFees
  }
}
