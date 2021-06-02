import { reactive, toRefs, computed } from '@vue/composition-api' // eslint-disable-line no-unused-vars
import { AddPartiesIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers' // eslint-disable-line no-unused-vars

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
    address = address + '<br>' + party.address.city + ' ' + party.address.region + ' ' + party.address.postalCode
    return address
  }

  const getFormattedBirthdate = (party: PartyIF): string => {
    const date = new Date(party.birthDate)
    return date.toLocaleString('default', { month: 'long' }) + ' ' + date.getDate + ', ' + date.getFullYear
  }

  return {
    getName,
    getFormattedAddress,
    getFormattedBirthdate
  }
}
