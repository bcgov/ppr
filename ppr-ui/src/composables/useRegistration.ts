import { RegistrationSummaryIF, DraftResultIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { reactive, toRefs, watch, ref } from '@vue/composition-api'
import { RegistrationTypes, StatusTypes } from '@/resources'
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'

export const useRegistration = () => {
  const localState = reactive({
    tableData: [],
    originalData: [],
    registrationNumber: '',
    registrationType: '',
    status: '',
    registeredBy: '',
    registeringParty: '',
    securedParties: '',
    folioNumber: '',
    daysToExpiry: '',
    submittedStartDate: null,
    submittedEndDate: null,
    registrationTypes: RegistrationTypes,
    statusTypes: StatusTypes
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

  const getStatusDescription = (status: string): string => {
    for (let i = 0; i < StatusTypes.length; i++) {
      if (StatusTypes[i].value === status) {
        return StatusTypes[i].text
      }
    }
  }

  const getPdfLink = (reg: string): string => {
    return ''
  }

  const getRegistrationType = (status: string): string => {
    if (status) {
      const keyValue = Object.keys(APIRegistrationTypes).find(
        name => APIRegistrationTypes[name] === status
      )
      return UIRegistrationTypes[keyValue]
    }
    return ''
  }

  const filterResults = (originalData: Array<any>): void => {
    const newTableData = [...originalData]
    // start off by showing everthing
    for (let i = 0; i < newTableData.length; i++) {
      newTableData[i].hide = false
    }
    // then filter values one at a time, if they contain a value
    if (localState.registeringParty) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].registeringParty) {
          if (
            !originalData[i].registeringParty.includes(
              localState.registeringParty
            )
          ) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.registeredBy) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].registeredBy) {
          if (!originalData[i].registeredBy.includes(localState.registeredBy)) {
            newTableData[i].hide = true
          }
        } else {
          newTableData[i].hide = true
        }
      }
    }

    if (localState.registrationType) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].registrationType) {
          if (
            originalData[i].registrationType !== localState.registrationType
          ) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.registeringParty) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].registeringParty) {
          if (
            !originalData[i].registeringParty.includes(
              localState.registeringParty
            )
          ) {
            newTableData[i].hide = true
          }
        } else {
          newTableData[i].hide = true
        }
      }
    }

    if (localState.securedParties) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].securedParties) {
          if (
            !originalData[i].securedParties.includes(localState.securedParties)
          ) {
            newTableData[i].hide = true
          }
        } else {
          newTableData[i].hide = true
        }
      }
    }

    if (localState.folioNumber) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].clientReferenceId) {
          if (
            !originalData[i].clientReferenceId.includes(localState.folioNumber)
          ) {
            newTableData[i].hide = true
          }
        } else {
          newTableData[i].hide = true
        }
      }
    }

    if (localState.registrationNumber) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].registrationNumber) {
          if (
            !originalData[i].registrationNumber.includes(
              localState.registrationNumber
            )
          ) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.status) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].statusType) {
          if (originalData[i].statusType !== localState.status) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.daysToExpiry) {
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].expireDays) {
          if (originalData[i].expireDays === localState.daysToExpiry) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.submittedStartDate) {
      const startDate = new Date(localState.submittedStartDate)
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].createDateTime) {
          const originalStartDate = new Date(originalData[i].createDateTime)
          if (startDate > originalStartDate) {
            newTableData[i].hide = true
          }
        }
      }
    }

    if (localState.submittedEndDate) {
      const endDate = new Date(localState.submittedEndDate)
      for (let i = 0; i < originalData.length; i++) {
        if (originalData[i].createDateTime) {
          const originalEndDate = new Date(originalData[i].createDateTime)
          if (endDate < originalEndDate) {
            newTableData[i].hide = true
          }
        }
      }
    }

    localState.tableData = newTableData
  }

  watch(
    () => localState.registeringParty,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.registrationType,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.registrationNumber,
    () => {
      filterResults(localState.originalData)
    }
  )
  watch(
    () => localState.folioNumber,
    () => {
      filterResults(localState.originalData)
    }
  )
  watch(
    () => localState.securedParties,
    () => {
      filterResults(localState.originalData)
    }
  )
  watch(
    () => localState.registeredBy,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.status,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.daysToExpiry,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.submittedStartDate,
    () => {
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.submittedEndDate,
    () => {
      filterResults(localState.originalData)
    }
  )

  return {
    getFormattedDate,
    getStatusDescription,
    getPdfLink,
    getRegistrationType,
    filterResults,
    ...toRefs(localState)
  }
}
