import { AddPartiesIF } from '@/interfaces'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { getRegisteringPartyFromAuth, getStaffegisteringParty } from '@/utils'
import { useParty } from './useParty'

export const useRegisteringParty = () => {
  const { isPartiesValid } = useParty()
  const {
    getAddSecuredPartiesAndDebtors,
    isRoleStaffReg,
    isRoleStaffBcol,
    isRoleStaffSbc
  } = useGetters<any>([
    'getAddSecuredPartiesAndDebtors',
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
    parties.valid = isPartiesValid(parties)
    setAddSecuredPartiesAndDebtors(parties)
  }

  return {
    getRegisteringParty
  }
}
