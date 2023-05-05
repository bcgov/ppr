import { ApiTransferTypes } from '@/enums'

export const transfersContent = {
  declaredHomeValueHint: {
    [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
      'Must match the declared value at death as recorded on the list of Assets and Liabilities',
    [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
      'Must match the declared value at death as recorded on the list of Assets and Liabilities',
    [ApiTransferTypes.TO_ADMIN_NO_WILL]:
      'Must match the declared value at death as recorded on the list of Assets and Liabilities'
  }
}
