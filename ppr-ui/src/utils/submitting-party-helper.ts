import type { AccountInfoIF, PartyIF, SubmittingPartyIF } from '@/interfaces'

export const parseAccountToSubmittingParty = (accountInfo: AccountInfoIF): SubmittingPartyIF => {
  return {
    businessName: accountInfo.name,
    address: accountInfo.mailingAddress,
    emailAddress: accountInfo.accountAdmin.email,
    phoneNumber: accountInfo.accountAdmin.phone,
    phoneExtension: accountInfo.accountAdmin.phoneExtension
  }
}
export const parseSubmittingPartyToAccountInfo = (party: PartyIF): AccountInfoIF => {
  return {
    name: party.businessName,
    mailingAddress: party.address,
    id: null,
    isBusinessAccount: !!party.businessName,
    accountAdmin: {
      firstName: party.personName?.first,
      lastName: party.personName?.last,
      email: party.emailAddress,
      phone: party.phoneNumber,
      phoneExtension: party.phoneExtension
    }
  }
}
