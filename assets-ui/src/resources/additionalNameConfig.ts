import { ApiTransferTypes, HomeOwnerPartyTypes } from '@/enums'
import { AdditionalNameConfigsIF } from '@/interfaces/mhr-registration-interfaces/AdditionalNameConfigIF'

export const AdditionalNameConfig: AdditionalNameConfigsIF = {
  [HomeOwnerPartyTypes.OWNER_IND]: {
    label: 'Additional Name Information (Optional)',
    hint: 'Example: Additional legal names, Jr., Sr., etc.',
    isRequired: false,
    tooltipContent: {
      default: `If the owner is a Trustee of a trust, enter the Trustee’s title. Example:<br><br>Trustee of the ABC
        Family Trust`
    }
  },
  [HomeOwnerPartyTypes.OWNER_BUS]: {
    label: 'Additional Name Information (Optional)',
    hint: 'Example: Additional legal names, Jr., Sr., etc.',
    isRequired: false,
    tooltipContent: {
      default: `If the owner is a Trustee of a trust, enter the Trustee’s title. Example:<br><br>Trustee of the ABC
        Family Trust`
    }
  },
  [HomeOwnerPartyTypes.EXECUTOR]: {
    label: 'Additional Name Information',
    hint: 'Example: Executor of the will of John Smith, deceased',
    isRequired: true,
    tooltipContent: {
      [ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL]:
        'Executor of the will is based on deceased owner with Grant of Probate with Will supporting document selected.',
      [ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL]:
        'Executor of the will is based on deceased owner with Affidavit of Executor supporting document selected.',
      default: ''
    }
  },
  [HomeOwnerPartyTypes.ADMINISTRATOR]: {
    label: 'Additional Name Information',
    hint: 'Example: Administrator of the estate of John Smith, deceased',
    isRequired: true,
    tooltipContent: {
      [ApiTransferTypes.TO_ADMIN_NO_WILL]:
      'Administrator of the estate is based on deceased owner with Grant of Administration ' +
      'supporting document selected.',
      default: ''
    }
  },
  [HomeOwnerPartyTypes.TRUSTEE]: {
    label: 'Additional Name Information',
    hint: 'Example: Trustee of the estate of John Smith, A Bankrupt',
    isRequired: true,
    tooltipContent: {
      default: ''
    }
  }
}
