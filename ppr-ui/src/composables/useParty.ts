import { PartyIF, AddPartiesIF } from '@/interfaces' // eslint-disable-line no-unused-vars
export const useParty = () => {
  const getName = (party: PartyIF): string => {
    if (party.businessName) {
      return party.businessName
    } else {
      return party.personName.first + ' ' + party.personName.middle + ' ' + party.personName.last
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

  const isPartiesValid = (parties: AddPartiesIF): boolean => {
    if (parties.debtors.length === 0) {
      return false
    }
    if (parties.securedParties.length === 0) {
      return false
    }
    return true
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
