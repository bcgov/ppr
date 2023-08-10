import { MhrSubTypes } from '@/enums'
import { RequirementsConfigIF } from '@/interfaces'

export const userAccessRequirements: Record<MhrSubTypes, RequirementsConfigIF[]> = {
  [MhrSubTypes.LAWYERS_NOTARIES]: [
    {
      boldTextPreTooltip: 'An ',
      boldTextPostTooltip: 'will be on this account.',
      underlinedText: 'active B.C. lawyer or notary in good standing',
      tooltipText: 'A practising member in good standing of the Law Society of British Columbia, ' +
                   'or a practising member in good standing of the Society of Notaries Public of British Columbia.',
      regularText: 'I understand that only a lawyer or notary, or someone who is being supervised ' +
                   'by a lawyer or notary, is authorized to complete Restricted Transactions.'
    },
    {
      boldText: 'All filed documents will be stored for 7 years. ',
      regularText: 'If requested, a copy or certified copy of filed documents ' +
      '(such as the Bill of Sale, or other signed forms), ' +
      'will be provided within 7 business days, at the fee level set by the Registrar.'
    }
  ],
  [MhrSubTypes.DEALERS]: [],
  [MhrSubTypes.GENERAL_PUBLIC]: [],
  [MhrSubTypes.MANUFACTURER]: [],
  [MhrSubTypes.QUALIFIED_SUPPLIER]: []
}
