import type { ContactInformationContentIF, PartyIF, SubmittingPartyIF } from '@/interfaces'

/* eslint-disable max-len */
export const submittingPartyRegistrationContent: ContactInformationContentIF = {
  title: 'Submitting Party',
  description: 'Provide the name and contact information for the person or business submitting this registration. ' +
               'You can add the submitting party information manually, or, if the submitting party has a Personal ' +
               'Property Registry party code, you can look up the party code or name.',
  sideLabel: 'Add Submitting Party',
  mailAddressInfo: 'Registry documents and decal will be mailed to this address.'
}

export const submittingPartyContentStaff: ContactInformationContentIF = {
  title: 'Submitting Party',
  description: 'Enter the name and contact information for the person or business submitting this registration, ' +
    'either by entering the details manually, using the PPR party code lookup, or selecting an owner as the submitting' +
    ' party.',
  sideLabel: 'Add Submitting Party',
  mailAddressInfo: 'Registry documents and decal will be mailed to this address.'
}

export const submittingPartyChangeContent : ContactInformationContentIF = {
  title: 'Submitting Party for this change',
  description: 'Provide the name and contact information for the person or business submitting this registration. ' +
               'You can add the submitting party information manually, or, if the submitting party has a Personal ' +
               'Property Registry party code, you can look up the party code or name.',
  sideLabel: 'Add Submitting Party',
  mailAddressInfo: 'Registry documents and decal will be mailed to this address.'
}

export const submittingPartySbcTransportPermitContent : ContactInformationContentIF = {
  title: 'Submitting Party for this change',
  description: 'Provide the name and contact information for the person or business submitting this registration. ',
  sideLabel: 'Add Submitting Party',
  mailAddressInfo: 'Registry documents, if any, will be mailed to this address.'
}

export const personGivingNoticeContent: ContactInformationContentIF = {
  title: 'Person Giving Notice',
  description: 'Contact information for the person making the claim will be shown ' +
    'when a search result is produced for this manufactured home.',
  sideLabel: 'Person Giving Notice'
}

export const collectorInformationContent: ContactInformationContentIF = {
  title: 'Collector',
  description: 'Contact information for the collector will be shown when a search result is produced for this manufactured home.',
  sideLabel: 'Collector'
}
/* eslint-enable max-len */

export const hasNoPersonGivingNoticeText = 'There is no Person Giving Notice for this unit note.'

export const emptyContactInfo: Readonly<PartyIF | SubmittingPartyIF> = {
  personName: {
    first: '',
    last: '',
    middle: ''
  },
  businessName: '',
  emailAddress: '',
  phoneNumber: '',
  phoneExtension: '',
  address: {
    street: '',
    streetAdditional: '',
    city: '',
    region: '',
    country: '',
    postalCode: '',
    deliveryInstructions: ''
  }
}
