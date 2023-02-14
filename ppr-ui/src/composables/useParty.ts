import { ActionTypes } from '@/enums'
import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { isSecuredPartyRestrictedList } from '@/utils'

export const useParty = () => {
  const getName = (party: PartyIF): string => {
    if (party.businessName) {
      return party.businessName
    } else {
      return party.personName.first + ' ' + (party.personName.middle || '') + ' ' + party.personName.last
    }
  }

  const isBusiness = (party: PartyIF): boolean => {
    if (party.businessName) {
      return true
    } else {
      return false
    }
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
      const mon = date.getMonth() + 1
      return mon
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

  const isPartiesValid = (parties: AddPartiesIF, regType: string): boolean => {
    let debtorValid = false
    let securedPartyValid = false
    let registeringPartyValid = false
    let securedPartyCount = 0
    for (let i = 0; i < parties.debtors.length; i++) {
      // is valid if there is at least one debtor
      if (parties.debtors[i].action !== ActionTypes.REMOVED) {
        debtorValid = true
      }
    }
    for (let i = 0; i < parties.securedParties.length; i++) {
      // is valid if there is at least one secured party
      if (parties.securedParties[i].action !== ActionTypes.REMOVED) {
        securedPartyCount++
      }
    }

    // if the registration is a crown registration, we can only have one secured party
    if (isSecuredPartyRestrictedList(regType)) {
      if (securedPartyCount === 1) {
        securedPartyValid = true
      }
    } else {
      if (securedPartyCount >= 1) {
        securedPartyValid = true
      }
    }

    if (parties.registeringParty) {
      registeringPartyValid = true
    }

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
