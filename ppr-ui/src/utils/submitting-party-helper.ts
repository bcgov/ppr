import { AccountInfoIF, SubmittingPartyIF } from '@/interfaces'

export const parseAccountToSubmittingParty = (accountInfo: AccountInfoIF): SubmittingPartyIF => {
  return {
    businessName: accountInfo.name,
    address: accountInfo.mailingAddress,
    emailAddress: accountInfo.accountAdmin.email,
    phoneNumber: accountInfo.accountAdmin.phone,
    phoneExtension: accountInfo.accountAdmin.phoneExtension
  }
}
