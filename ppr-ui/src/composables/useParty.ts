import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export const useParty = () => {
  const getName = (party: PartyIF): string => {
    if (party.businessName) {
      return party.businessName
    } else {
      return party.personName.first + ' ' + party.personName.last
    }
  }

  const getFormattedAddress = (party: PartyIF): string => {
    let address = party.address.street
    if (party.address.streetAdditional) {
      address = address + '<br>' + party.address.streetAdditional
    }
    address =
      address +
      '<br>' +
      party.address.city +
      ' ' +
      party.address.region +
      ' ' +
      party.address.postalCode
    return address
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

  return {
    getName,
    getFormattedAddress,
    getFormattedBirthdate,
    getMonth,
    getMonthFull,
    getDay,
    getYear
  }
}
