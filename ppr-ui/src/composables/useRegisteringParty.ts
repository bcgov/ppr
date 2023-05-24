import { useStore } from '@/store/store'
import { useParty } from './useParty'
import { AddPartiesIF } from '@/interfaces'
import { getStaffegisteringParty, getRegisteringPartyFromAuth } from '@/utils'
import { storeToRefs } from 'pinia'

export const useRegisteringParty = () => {
  const { isPartiesValid } = useParty()
  const {
    // Actions
    setAddSecuredPartiesAndDebtors
  } = useStore()
  const {
    // Getters
    getAddSecuredPartiesAndDebtors,
    getRegistrationType,
    isRoleStaffReg,
    isRoleStaffBcol,
    isRoleStaffSbc
  } = storeToRefs(useStore())

  const getRegisteringParty = async () => {
    let regParty = null
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
    if (isRoleStaffBcol.value || isRoleStaffReg.value) {
      regParty = await getStaffegisteringParty(isRoleStaffBcol.value)
    } else if (isRoleStaffSbc.value) {
      // do nothing (keep regParty null)
    } else {
      regParty = await getRegisteringPartyFromAuth()
    }
    parties.registeringParty = regParty
    parties.valid = isPartiesValid(parties, getRegistrationType.value.registrationTypeAPI)
    setAddSecuredPartiesAndDebtors(parties)
  }

  return {
    getRegisteringParty
  }
}
