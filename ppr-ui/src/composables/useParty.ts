import { APIRegistrationTypes, ActionTypes } from '@/enums'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { SecuredPartyRestrictedList } from '@/resources'

export const useParty = () => {
  const getName = (party: PartyIF): string => {
    return isBusiness(party)
      ? party.businessName
      : party.personName.first + ' ' + (party.personName.middle || '') + ' ' + party.personName.last
  }

  const isBusiness = (party: PartyIF): boolean => {
    return !!party.businessName
  }

  const getFormattedBirthdate = (party: PartyIF): string => {
    if (party.birthDate) {
      const date = new Date(party.birthDate)
      return (
        date.toLocaleString('default', { month: 'long' }) +
        ' ' +
        date.getDate() +
        ', ' +
        date.getFullYear()
      )
    }
  }

  const getMonth = (party: PartyIF): number => {
    if (party.birthDate) {
      const date = new Date(party.birthDate)
      return date.getMonth() + 1
    }
  }

  const getMonthFull = (party: PartyIF): string => {
    if (party.birthDate) {
      const date = new Date(party.birthDate)
      return date.toLocaleString('default', { month: 'long' })
    }
  }

  const getDay = (party: PartyIF): string => {
    if (party.birthDate) {
      const date = new Date(party.birthDate)
      return date.getDate().toString()
    }
  }

  const getYear = (party: PartyIF): string => {
    if (party.birthDate) {
      const date = new Date(party.birthDate)
      return date.getFullYear().toString()
    }
  }

  const isPartiesValid = (parties: AddPartiesIF, regType: APIRegistrationTypes): boolean => {
    const securedPartyCount = parties.securedParties.filter((securedParty) =>
      securedParty.action !== ActionTypes.REMOVED).length

    // if the registration is a crown registration, we can only have one secured party
    const isSecuredPartiesRestricted = SecuredPartyRestrictedList.includes(regType)
    const securedPartyValid = isSecuredPartiesRestricted ? securedPartyCount === 1 : securedPartyCount >= 1

    const debtorValid = parties.debtors.some((debtor) => debtor.action !== ActionTypes.REMOVED)
    const registeringPartyValid = !!parties.registeringParty

    return debtorValid && securedPartyValid && registeringPartyValid
  }

  return {
    getName,
    isBusiness,
    getFormattedBirthdate,
    getMonth,
    getMonthFull,
    getDay,
    getYear,
    isPartiesValid
  }
}
