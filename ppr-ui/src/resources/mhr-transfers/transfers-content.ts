import { ApiTransferTypes } from '@/enums'

export const transfersContent = {
  declaredHomeValueHint: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'Must match the declared value at death, as recorded on the list of Assets and Liabilities',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Must match the declared value at death as recorded on the list of Assets and Liabilities'
  },
  executorTooltip: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'Executor of the will is based on deceased owner with Grant of Probate with Will supporting document selected.',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Executor of the will is based on deceased owner with Affidavit of Executor supporting document selected.'
  }
}
