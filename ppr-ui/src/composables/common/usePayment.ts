import { reactive } from 'vue'
import { StaffPaymentOptions } from '@/enums'
import type { StaffPaymentIF } from '@/interfaces'
import { useStore } from '@/store/store'

/**
 *  Common Payment functionality that can be used to handle instances of the staff payment component.
 * **/
export const usePayment = () => {
  const { setStaffPayment } = useStore()
  const localState = reactive({
    staffPaymentValid: false,
    staffPayment: {
      option: StaffPaymentOptions.NONE,
      routingSlipNumber: '',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    }
  })

  /** Called when component's staff payment data has been updated. */
  const onStaffPaymentDataUpdate = async (val: StaffPaymentIF): Promise<void> => {
    let staffPaymentData: StaffPaymentIF = {
      ...val
    }

    switch (staffPaymentData.option) {
      case StaffPaymentOptions.FAS:
        staffPaymentData = {
          option: StaffPaymentOptions.FAS,
          routingSlipNumber: staffPaymentData.routingSlipNumber,
          isPriority: staffPaymentData.isPriority,
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: ''
        }
        localState.staffPaymentValid = false
        break

      case StaffPaymentOptions.BCOL:
        staffPaymentData = {
          option: StaffPaymentOptions.BCOL,
          bcolAccountNumber: staffPaymentData.bcolAccountNumber,
          datNumber: staffPaymentData.datNumber,
          folioNumber: staffPaymentData.folioNumber,
          isPriority: staffPaymentData.isPriority,
          routingSlipNumber: ''
        }
        localState.staffPaymentValid = false
        break

      case StaffPaymentOptions.NO_FEE:
        staffPaymentData = {
          option: StaffPaymentOptions.NO_FEE,
          routingSlipNumber: '',
          isPriority: false,
          bcolAccountNumber: '',
          datNumber: '',
          folioNumber: ''
        }
        localState.staffPaymentValid = true
        break
      case StaffPaymentOptions.NONE: // should never happen
        break
    }

    setStaffPayment(staffPaymentData)
  }

  return {
    onStaffPaymentDataUpdate,
    ...localState
  }
}
