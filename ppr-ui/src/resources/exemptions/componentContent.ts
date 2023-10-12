import { ContactInformationContentIF, ContentIF, RequirementsConfigIF } from '@/interfaces'

export const exDocIdContent: ContentIF = {
  title: 'Document ID',
  sideLabel: 'Document ID',
  description: 'Enter the 8-digit Document ID number.'
}

export const exRemarksContent: ContentIF = {
  title: 'Remarks',
  sideLabel: 'Add Remarks',
  description: 'Remarks will be shown when a search result is produced for this manufactured home.'
}

export const exConfirmRequirements: Array<RequirementsConfigIF> = [
  {
    boldText: 'Residential Exemption form ',
    regularText: 'meets the following requirements:',
    bullets: [
      'It has been signed by either a) the registered owner(s) (individually or by a duly authorized representative' +
      ' of an organization), or b) person(s) with the authority to act on behalf of the registered owner(s).',
      'All signatures have been witnessed by an independent third party, and the name and occupation of each witness' +
      ' has been recorded.'
    ],
    note: ' If the Residential Exemption form has been signed by a person acting on behalf of a registered owner, the' +
      ' qualified supplier submitting this application must provide evidence of the authority by which the signatory' +
      ' was authorized. Such authorization must be granted by one of the following: power of attorney, ' +
      'representation agreement, or committee.'
  },
  {
    boldText: 'Home location and homeowner(s) named in the Manufactured Home Registry match ',
    regularText: 'the home location and current ownership of the home on the Residential Exemption form.'
  },
  {
    boldText: 'Must have one of the following ',
    regularText: 'that shows the name of the homeowner(s) and home location and at least one of the homeowners as ' +
      'also being an owner of the land where the home is located:',
    bullets: [
      'Land Title Search, dated within 30 days of today, or',
      'Pending freehold transfer'
    ]
  },
  {
    boldText: 'Legal Land Description on the Land Title Search or pending freehold transfer matches ',
    regularText: 'the registered manufactured home location information. One or more of the following must correspond' +
      ' and there should be no material differences in the location descriptions:',
    bullets: [
      'PID,',
      'Lot / land district / plan number, or',
      'District lot / land district'
    ]
  },
  {
    boldText: 'Personal Property Registry search ',
    regularText: 'has been completed and there are no liens that block the exemption. PPR registrations that block' +
      ' the exemption include the following:',
    bullets: [
      'Marriage/Separation Agreement Affecting Manufactured Home',
      'Land Tax Deferment Lien on a Manufactured Home',
      'Maintenance Lien',
      'Manufactured Home Notice',
      'Possession under s.30 of the Sale of Goods Act'
    ],
    note: 'If there is a Personal Property Security Act (PPSA) security interest registered against this manufactured' +
      ' home, such registration has been discharged or consent to the exemption application of each secured party' +
      ' under the security agreement has been obtained.'
  }
]

export const exCertifyInfoContent: ContentIF = {
  title: 'Authorization',
  description: `The following account information will be recorded by BC Registries upon registration and payment. This
   information is used to confirm you have the authority to submit this registration.`,
  sideLabel: 'Confirm Authorization',
  mailAddressInfo: 'Test Address'
}
