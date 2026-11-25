import type { APIRegistrationTypes} from '@/enums';
import { ActionTypes } from '@/enums'
import type { PartyIF, AddPartiesIF } from '@/interfaces'
import { SecuredPartyRestrictedList } from '@/resources'
import { formatBirthdate, getBirthdateParts, getMonthName } from '@/utils/birthdate-helper'

export const useParty = () => {
  const getName = (party: PartyIF): string => {
    return isBusiness(party)
      ? party.businessName
      : party?.personName?.first + ' ' + (party?.personName?.middle || '') + ' ' + party?.personName?.last
  }

  const isBusiness = (party: PartyIF): boolean => {
    return !!party?.businessName
  }

  // Birthdates are calendar dates: use the YYYY-MM-DD part as-is, no time zone conversion.
  const getFormattedBirthdate = (party: PartyIF): string => {
    return formatBirthdate(party?.birthDate)
  }

  const getMonth = (party: PartyIF): number => {
    return getBirthdateParts(party?.birthDate)?.month
  }

  const getMonthFull = (party: PartyIF): string => {
    const month = getBirthdateParts(party?.birthDate)?.month
    return month ? getMonthName(month) : undefined
  }

  const getDay = (party: PartyIF): string => {
    return getBirthdateParts(party?.birthDate)?.day.toString()
  }

  const getYear = (party: PartyIF): string => {
    return getBirthdateParts(party?.birthDate)?.year.toString()
  }

  const isPartiesValid = (parties: AddPartiesIF, regType: APIRegistrationTypes): boolean => {
    const securedPartyCount = parties.securedParties?.filter((securedParty) =>
      securedParty?.action !== ActionTypes.REMOVED).length

    // if the registration is a crown registration, we can only have one secured party
    const isSecuredPartiesRestricted = SecuredPartyRestrictedList.includes(regType)
    const securedPartyValid = isSecuredPartiesRestricted ? securedPartyCount === 1 : securedPartyCount >= 1

    const debtorValid = parties.debtors?.some((debtor) => debtor.action !== ActionTypes.REMOVED)
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
