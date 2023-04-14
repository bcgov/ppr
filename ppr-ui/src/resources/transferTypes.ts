import { TransferTypeSelectIF } from '@/interfaces'
import { ApiTransferTypes, UITransferTypes } from '@/enums/transferTypes'
import { BlankSearchTypes } from '@/enums'

export const StaffTransferTypes: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    selectDisabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer' as any,
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
      bullets: ['Transfer form', 'Bill of sale', 'Transfer fee']
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
      bullets: ['Ownership Transfer or Change form',
        'Original or certified copy of death certificate issued from Canada or the United States.']
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
      bullets: ['Ownership Transfer or Change form',
        'Court certified true copy of the Grant of Probate with the will attached.',
        'Original or certified copy of death certificate issued from Canada or the United States ' +
        'for deceased joint tenants, if any, except for the person who last died. ']
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
      bullets: ['Ownership Transfer or Change form',
        'Original signed Affidavit of Executor form',
        'Certified true copy of will',
        'Original or certified copy of death certificate issued from Canada or the United States.'
      ],
      note: 'Value of the estate must be no more than $25,000, ' +
        'including the total value of the manufactured home.'
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
      bullets: ['Original court certified true copy of Grant of Administration',
        'Affidavit of Administration with List of Assets and Liabilities', 'Transfer form', 'Transfer fee']
    }
  }
]

export const ClientTransferTypes: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    selectDisabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer' as any,
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
      bullets: ['Transfer form', 'Bill of sale', 'Transfer fee']
    }
  }
]
