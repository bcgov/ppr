import { MhrSubTypes } from '@/enums'
import type { RequirementsConfigIF } from '@/interfaces'

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
  [MhrSubTypes.DEALERS]: [
    {
      boldText: 'Have comprehensive general liability insurance ',
      regularText: 'equal to or greater than $2,000,000.00.'
    },
    {
      boldText: 'All filed documents will be stored for 7 years. ',
      regularText: 'If requested, a copy or certified copy of filed documents ' +
        '(such as the Bill of Sale, or other signed forms), ' +
        'will be provided within 7 business days, at the fee level set by the Registrar.'
    }
  ],
  [MhrSubTypes.GENERAL_PUBLIC]: [],
  [MhrSubTypes.MANUFACTURER]: [
    {
      boldText: 'Have comprehensive general liability insurance ',
      regularText: 'equal to or greater than $2,000,000.00.'
    },
    {
      boldText: 'Manufactured homes built are CSA approved ',
      regularText: '(Z240 or A277).'
    },
    {
      boldText: 'All filed documents will be stored for 7 years. ',
      regularText: 'If requested, a copy or certified copy of filed documents (such as the Bill of Sale, or other' +
        ' signed forms), will be provided within 7 business days, at the fee level set by the Registrar.'
    }
  ],
  [MhrSubTypes.QUALIFIED_SUPPLIER]: []
}
