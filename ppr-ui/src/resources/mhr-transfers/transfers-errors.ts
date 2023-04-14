import { ApiTransferTypes } from '@/enums'

export const transfersErrors = {
  noSupportingDocSelected: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'You must delete a deceased owner using Grant of Probate with Will before adding an executor',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'You must delete a deceased owner using Affidavit of Executor before adding an executor'
  },
  declaredHomeValueMax: {
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Declared value of home must not exceed $25,000 for this transfer type'
  }
}
