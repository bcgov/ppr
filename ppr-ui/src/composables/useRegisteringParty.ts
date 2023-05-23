import { useStore } from '@/store/store'
import { useParty } from './useParty'
import { AddPartiesIF } from '@/interfaces'
import { getStaffegisteringParty, getRegisteringPartyFromAuth } from '@/utils'

export const useRegisteringParty = () => {
  const { isPartiesValid } = useParty()
  const {
    // Getters
    getAddSecuredPartiesAndDebtors,
    getRegistrationType,
    isRoleStaffReg,
    isRoleStaffBcol,
    isRoleStaffSbc,
    // Actions
    setAddSecuredPartiesAndDebtors
  } = useStore()

  const getRegisteringParty = async () => {
    let regParty = null
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors
    if (isRoleStaffBcol || isRoleStaffReg) {
      regParty = await getStaffegisteringParty(isRoleStaffBcol)
    } else if (isRoleStaffSbc) {
      // do nothing (keep regParty null)
    } else {
      regParty = await getRegisteringPartyFromAuth()
    }
    parties.registeringParty = regParty
    parties.valid = isPartiesValid(parties, getRegistrationType.registrationTypeAPI)
    setAddSecuredPartiesAndDebtors(parties)
  }

  return {
    getRegisteringParty
  }
}
