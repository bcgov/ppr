import { reactive, toRefs } from 'vue-demi'
import { MhrAPIToUIStatusTypesMap, PprAPIToUIStatusTypesMap } from '@/resources'
import {
  APIAmendmentTypes,
  APIRegistrationTypes,
  APIStatusTypes,
  MhApiStatusTypes,
  MhUIStatusTypes,
  UIAmendmentTypes,
  UIRegistrationTypes,
  UIStatusTypes
} from '@/enums'
import { RegistrationSortIF, RegistrationSummaryIF } from '@/interfaces'

export const useRegistration = (setSort: RegistrationSortIF) => {
  const localState = reactive({
    dateTxt: '',
    registrationNumber: setSort?.regNum || '',
    registrationType: setSort?.regType || '',
    status: setSort?.status || '',
    registeredBy: setSort?.regBy || '',
    registeringParty: setSort?.regParty || '',
    securedParties: setSort?.secParty || '',
    shouldClearType: false,
    folioNumber: setSort?.folNum || '',
    submittedStartDate: setSort?.startDate || null,
    submittedEndDate: setSort?.endDate || null,
    orderBy: setSort?.orderBy || '',
    orderVal: setSort?.orderVal || ''
  })

  const getFormattedDate = (dateStr: string): string => {
    if (dateStr) {
      const date = new Date(dateStr)
      return (
        date.toLocaleString('default', { month: 'long' }) +
        ' ' +
        date.getDate() +
        ', ' +
        date.getFullYear()
      )
    }
  }

  const getStatusDescription = (status: APIStatusTypes | MhApiStatusTypes,
    isChild: boolean, isPpr: boolean): string => {
    if (!status) return UIStatusTypes.DRAFT
    if (status === MhApiStatusTypes.FROZEN) return MhUIStatusTypes.ACTIVE
    if (isChild && (status === MhApiStatusTypes.HISTORICAL || status === MhApiStatusTypes.EXEMPT)) return ''
    return isPpr ? PprAPIToUIStatusTypesMap[status] : MhrAPIToUIStatusTypesMap[status]
  }

  const getRegisteringName = (name: string): string => {
    if (!name) {
      return 'Not Available'
    }
    return name
  }

  const getPdfLink = (reg: string): string => {
    return ''
  }

  const getRegistrationType = (
    regType: APIRegistrationTypes | APIAmendmentTypes
  ): UIRegistrationTypes | UIAmendmentTypes | string => {
    if (!regType) return ''

    const keyValueRegType = Object.keys(APIRegistrationTypes).find(
      name => APIRegistrationTypes[name] === regType
    )
    if (keyValueRegType) return UIRegistrationTypes[keyValueRegType]

    const keyValueAmType = Object.keys(APIAmendmentTypes).find(
      name => APIAmendmentTypes[name] === regType
    )
    if (keyValueAmType) return UIAmendmentTypes[keyValueAmType]

    // should never get here
    return ''
  }

  const clearFilters = () => {
    localState.dateTxt = ''
    localState.registrationNumber = ''
    localState.registrationType = ''
    localState.status = ''
    localState.registeredBy = ''
    localState.registeringParty = ''
    localState.securedParties = ''
    localState.folioNumber = ''
    localState.submittedStartDate = null
    localState.submittedEndDate = null
    localState.shouldClearType = true
    localState.orderBy = setSort?.orderBy || ''
    localState.orderVal = setSort?.orderVal || ''
  }

  const hasRenewal = (
    item: RegistrationSummaryIF
  ): boolean => {
    // check each child
    for (let i = 0; i < item.changes?.length || 0; i++) {
      if ((item.changes[i] as any)?.registrationClass === 'RENEWAL') {
        return true
      }
    }
    return false
  }

  return {
    getFormattedDate,
    getStatusDescription,
    getRegisteringName,
    getPdfLink,
    getRegistrationType,
    clearFilters,
    hasRenewal,
    ...toRefs(localState)
  }
}
