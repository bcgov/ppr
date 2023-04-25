import { ApiTransferTypes } from '@/enums'

export const transfersErrors = {
  ownersMustBeDeceased: 'All owners must be deceased.',
  ownersMustBeDeceasedAndExecutorAdded: 'All owners must be deceased and an executor added.',
  mustContainOneExecutor: 'Must contain at least one executor.',
  mustContainOneExecutorInGroup: 'Group must contain at least one executor.',
  noSupportingDocSelected: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'You must delete a deceased owner using Grant of Probate with Will before adding an executor',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'You must delete a deceased owner using Affidavit of Executor before adding an executor'
  },
  declaredHomeValueMax: {
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Declared value of home must not exceed $25,000 for this transfer type'
  },
  allOwnersHaveDeathCerts: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'One of the deceased owners must have a Grant of Probate with Will.',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'One of the deceased owners must have an Affidavit of Executor with Death Certificate.'
  }
}
