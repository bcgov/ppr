import { TransferTypeSelectIF } from '@/interfaces'
import { ApiTransferTypes, UITransferTypes } from '@/enums/transferTypes'
import { BlankSearchTypes } from '@/enums'

export const StaffTransferTypesOrg: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
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
    disabled: true,
    divider: false,
    group: 2,
    transferType: BlankSearchTypes.BLANK2 as any,
    textLabel: 'Transfer Due to Death' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
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
    disabled: false,
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
    disabled: false,
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
    disabled: false,
    transferType: ApiTransferTypes.TO_ADMIN_NO_WILL,
    textLabel: UITransferTypes.TO_ADMIN_NO_WILL,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form',
        'Certified true copy of Grant of Administration issued by the court',
        'Affidavit of Administration with list of Assets and Liabilities',
        'Original or certified copy of death certificate issued from Canada or the United States ' +
          'for deceased joint tenants, if any, except for the person who last died.'
      ]
    }
  }
]

export const StaffTransferTypes: Array<TransferTypeSelectIF> = [
  // Bill Of Sale Transfers
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Bill Of Sale Transfers' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.SALE_OR_GIFT,
    textLabel: UITransferTypes.SALE_OR_GIFT,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form', 'Bill of Sale']
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_FAMILY_ACT,
    textLabel: UITransferTypes.TRANS_FAMILY_ACT,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Land Title Transfer documents",
        "Evidence that the home was purchased with the land"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_INFORMAL_SALE,
    textLabel: UITransferTypes.TRANS_INFORMAL_SALE,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Informal Bill of Sale",
        "Statutory Declaration"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_QUIT_CLAIM,
    textLabel: UITransferTypes.TRANS_QUIT_CLAIM,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Bill of Sale (to Secured Party)"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_RECEIVERSHIP,
    textLabel: UITransferTypes.TRANS_RECEIVERSHIP,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Bill of Sale (signed by Receiver)",
        "Proof of appointment of Receiver",
        "Statutory Declaration"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_SEVER_GRANT,
    textLabel: UITransferTypes.TRANS_SEVER_GRANT,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Bill of Sale"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_WRIT_POSSESSION,
    textLabel: UITransferTypes.TRANS_WRIT_POSSESSION,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Bill of Sale (signed by Bailiff)",
        "Certified true copy of the Writ (either Seizure and Sale or Writ of Possession- issued by the Court)"
      ]
    }
  },

  // Transfers Due to Death
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 2,
    transferType: BlankSearchTypes.BLANK2 as any,
    textLabel: 'Transfers Due to Death' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
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
    disabled: false,
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
    disabled: false,
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
    disabled: false,
    transferType: ApiTransferTypes.TO_ADMIN_NO_WILL,
    textLabel: UITransferTypes.TO_ADMIN_NO_WILL,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form',
        'Certified true copy of Grant of Administration issued by the court',
        'Affidavit of Administration with list of Assets and Liabilities',
        'Original or certified copy of death certificate issued from Canada or the United States ' +
          'for deceased joint tenants, if any, except for the person who last died.'
      ]
    }
  },

  // Other Transfers
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 3,
    transferType: BlankSearchTypes.BLANK2 as any,
    textLabel: 'Other Transfers' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.ABAN,
    textLabel: UITransferTypes.ABAN,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Affidavit of Abandonment and Sale form",
        "Tax Certificate may be required"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.BANK,
    textLabel: UITransferTypes.BANK,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Copy of Bankruptcy Trustee(s) appointment by Industry Canada",
        "Certified copy of assignments for creditors",
        "Court Order (required for court ordered bankruptcy)"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.COU,
    textLabel: UITransferTypes.COU,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Original certified true copy of Court Order (must specify the home registration number and order " +
        "the Manufactured Home Registry to complete a change)"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.FORE,
    textLabel: UITransferTypes.FORE,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Original Court certified true copy of Court Order",
        "Solicitor's letters (if court order requests this)"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.GENT,
    textLabel: UITransferTypes.GENT,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Statutory Declaration",
        "Additional proof of ownership"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TRANS_LAND_TITLE,
    textLabel: UITransferTypes.TRANS_LAND_TITLE,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Land title transfer documents",
        "Evidence that the Manufactured Home was part of the sale."
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.REIV,
    textLabel: UITransferTypes.REIV,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Affidavit of Repossession - Involuntary form",
        "Purchaser's statement, if required",
        "Copy of the valid lien/PPR registration",
        "If owner(s) are bankrupt, see requirements for Bankruptcy"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.REPV,
    textLabel: UITransferTypes.REPV,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Affidavit of Repossession - Voluntary form",
        "Copy of the valid lien/PPR registration"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.SZL,
    textLabel: UITransferTypes.SZL,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Affidavit of Crown Land Seizure from government authority"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.TAXS,
    textLabel: UITransferTypes.TAXS,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Notice / Letter from tax collector stating home was sold to tax sale purchaser",
        "Tax Sale Notice must be removed prior to this transfer"
      ]
    }
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.VEST,
    textLabel: UITransferTypes.VEST,
    group: 3,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: [
        "Ownership Transfer or Change form",
        "Certified true copy of Court Order",
        "Solicitor letter, if required"
      ]
    }
  }
]

export const ClientTransferTypes: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.SALE_OR_GIFT,
    textLabel: UITransferTypes.SALE_OR_GIFT,
    group: 1,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Transfer form', 'Bill of sale', 'Transfer fee']
    }
  }
]

export const QualifiedSupplierTransferTypes: Array<TransferTypeSelectIF> = [
  {
    class: 'transfer-type-list-header',
    disabled: true,
    divider: false,
    group: 1,
    transferType: BlankSearchTypes.BLANK1 as any,
    textLabel: 'Transfer' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
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
    disabled: true,
    divider: false,
    group: 2,
    transferType: BlankSearchTypes.BLANK2 as any,
    textLabel: 'Transfer Due to Death' as any,
    color: 'primary'
  },
  {
    divider: false,
    disabled: false,
    transferType: ApiTransferTypes.SURVIVING_JOINT_TENANT,
    textLabel: UITransferTypes.SURVIVING_JOINT_TENANT,
    group: 2,
    tooltip: {
      title: 'Supporting Documents Required',
      bullets: ['Ownership Transfer or Change form',
        'Original or certified copy of death certificate issued from Canada or the United States.']
    }
  }
]
