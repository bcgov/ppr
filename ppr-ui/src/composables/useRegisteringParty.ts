import { useGetters, useActions } from 'vuex-composition-helpers'
import { useParty } from './useParty'
import { AddPartiesIF } from '@/interfaces'
import { getStaffegisteringParty, getRegisteringPartyFromAuth } from '@/utils'

export const useRegisteringParty = () => {
  const { isPartiesValid } = useParty()
  const {
    getAddSecuredPartiesAndDebtors,
    getRegistrationType,
    isRoleStaffReg,
    isRoleStaffBcol,
    isRoleStaffSbc
  } = useGetters<any>([
    'getAddSecuredPartiesAndDebtors',
    'getRegistrationType',
    'isRoleStaffReg',
    'isRoleStaffBcol',
    'isRoleStaffSbc'
  ])
  const { setAddSecuredPartiesAndDebtors } = useActions<any>([
    'setAddSecuredPartiesAndDebtors'
  ])

  const getRegisteringParty = async () => {
    let regParty = null
    var parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value
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
