import { reactive, toRefs, watch } from '@vue/composition-api'
import { StatusTypes } from '@/resources'
import {
  APIAmendmentTypes,
  APIRegistrationTypes,
  APIStatusTypes,
  UIAmendmentTypes,
  UIRegistrationTypes,
  UIStatusTypes
} from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'

export const useRegistration = () => {
  const localState = reactive({
    dateTxt: '',
    originalData: [],
    registrationNumber: '',
    registrationType: '',
    status: '',
    tableData: [],
    registeredBy: '',
    registeringParty: '',
    securedParties: '',
    shouldClearType: false,
    folioNumber: '',
    submittedStartDate: null,
    submittedEndDate: null
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

  const getStatusDescription = (status: APIStatusTypes): string => {
    if (!status) return UIStatusTypes.DRAFT
    for (let i = 0; i < StatusTypes.length; i++) {
      if (StatusTypes[i].value === status) {
        return StatusTypes[i].text
      }
    }
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
  }

  const passFilter = (
    item: RegistrationSummaryIF,
    filter: (param: RegistrationSummaryIF | DraftResultIF) => boolean
  ): boolean => {
    // check base reg
    if (filter(item)) {
      item.expand = false
      return true
    }
    // check each child
    for (let i = 0; i < item.changes?.length || 0; i++) {
      if (filter(item.changes[i])) {
        // child reg passes
        item.expand = true
        return true
      }
    }
    // neither the base reg or its children pass
    item.expand = false
    return false
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

  const filterResults = (originalData: RegistrationSummaryIF[]): any[] => {
    const newTableData = [] // filtered list of base registrations
    for (let i = 0; i < originalData.length; i++) {
      // start by setting expand to false if relevant
      if (originalData[i].changes) originalData[i].expand = false
      if (localState.registrationNumber) {
        const regNumFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.registrationNumber?.toUpperCase().includes(localState.registrationNumber.toUpperCase())
        }
        if (!passFilter(originalData[i], regNumFilter)) {
          // reg num filter is active and filters out this item
          continue
        }
      }

      if (localState.registrationType) {
        const regTypeFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.registrationType === localState.registrationType
        }
        if (!passFilter(originalData[i], regTypeFilter)) {
          // reg type filter is active and filters out this item
          continue
        }
      }

      if (localState.status) {
        const statusFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          const convertedStatus = item.statusType || APIStatusTypes.DRAFT
          return convertedStatus === localState.status
        }
        if (!passFilter(originalData[i], statusFilter)) {
          // status filter is active and filters out this item
          continue
        }
      }

      if (localState.registeringParty) {
        const regPartyFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.registeringParty?.toUpperCase().includes(localState.registeringParty.toUpperCase())
        }
        if (!passFilter(originalData[i], regPartyFilter)) {
          // reg party filter is active and filters out this item
          continue
        }
      }

      if (localState.registeredBy) {
        const regByFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.registeringName?.toUpperCase().includes(localState.registeredBy.toUpperCase())
        }
        if (!passFilter(originalData[i], regByFilter)) {
          // reg by filter is active and filters out this item
          continue
        }
      }

      if (localState.securedParties) {
        const secPartyFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.securedParties?.toUpperCase().includes(localState.securedParties.toUpperCase())
        }
        if (!passFilter(originalData[i], secPartyFilter)) {
          // sec party filter is active and filters out this item
          continue
        }
      }

      if (localState.folioNumber) {
        const folioFilter = (item: any): boolean => {
          // item is RegistrationSummaryIF or DraftResultIF
          return item.clientReferenceId?.toUpperCase().includes(localState.folioNumber.toUpperCase())
        }
        if (!passFilter(originalData[i], folioFilter)) {
          // folio filter is active and filters out this item
          continue
        }
      }

      if (localState.submittedStartDate && localState.submittedEndDate) {
        const sDateFilter = (item: any): boolean => {
          if (item.createDateTime) {
            const created = item.createDateTime.substring(0, 10)
            if (created < localState.submittedStartDate) return false
          }
          return true
        }
        const eDateFilter = (item: any): boolean => {
          if (item.createDateTime) {
            const created = item.createDateTime.substring(0, 10)
            if (created > localState.submittedEndDate) return false
          }
          return true
        }
        const dateFilter = (item: any): boolean => {
          return sDateFilter(item) && eDateFilter(item)
        }
        if (!passFilter(originalData[i], dateFilter)) {
          // submitted range filter is active and filters out this item
          continue
        }
      }

      // passed all filters, add to the new list
      newTableData.push({ ...originalData[i] })
    }

    // return new filtered list
    return newTableData
  }

  // filter watchers
  watch(() => localState.registeringParty, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.registrationType, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.registrationNumber, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.folioNumber, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.securedParties, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.registeredBy, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.status, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.submittedStartDate, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  watch(() => localState.submittedEndDate, () => {
    localState.tableData = filterResults(localState.originalData)
  })

  return {
    getFormattedDate,
    getStatusDescription,
    getPdfLink,
    getRegistrationType,
    filterResults,
    clearFilters,
    hasRenewal,
    ...toRefs(localState)
  }
}
