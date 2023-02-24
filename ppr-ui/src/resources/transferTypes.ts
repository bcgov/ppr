import { TransferTypeSelectIF } from '@/interfaces'
import { ApiTransferTypes, UITransferTypes } from '@/enums/transferTypes'
import { BlankSearchTypes } from '@/enums'

export const TransferTypes: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    selectDisabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer Header TBD' as any,
    color: 'primary'
  },
  {
    divider: false,
    selectDisabled: false,
    transferType: ApiTransferTypes.SALE_OR_GIFT,
    textLabel: UITransferTypes.SALE_OR_GIFT,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  },
  {
    class: 'transfer-type-list-header',
    selectDisabled: true,
    divider: false,
    group: 2,
    transferType: BlankSearchTypes.BLANK2 as any,
    textLabel: 'Transfer Due to Death' as any,
    color: 'primary'
  },
  {
    divider: false,
    selectDisabled: false,
    transferType: ApiTransferTypes.SURVIVING_JOINT_TENANT,
    textLabel: UITransferTypes.SURVIVING_JOINT_TENANT,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  },
  {
    divider: false,
    selectDisabled: false,
    transferType: ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL,
    textLabel: UITransferTypes.TO_EXECUTOR_PROBATE_WILL,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  },
  {
    divider: false,
    selectDisabled: false,
    transferType: ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
    textLabel: UITransferTypes.TO_EXECUTOR_UNDER_25K_WILL,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  },
  {
    divider: false,
    selectDisabled: false,
    transferType: ApiTransferTypes.TO_ADMIN_PROBATE_NO_WILL,
    textLabel: UITransferTypes.TO_ADMIN_PROBATE_NO_WILL,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  }
]
