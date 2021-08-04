import { RegistrationIF, DraftIF } from '@/interfaces' // eslint-disable-line no-unused-vars
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
    if (status) {
      return 'Other'
    } else {
      return 'Draft'
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

  const filterResults = (tableData: Array<any>): void => {
    if (localState.registeringParty) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].registeringParty) {
          if (
            !tableData[i].registeringParty.includes(localState.registeringParty)
          ) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.registeredBy) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].registeredBy) {
          if (!tableData[i].registeredBy.includes(localState.registeredBy)) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.securedParties) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].securedParties) {
          if (
            !tableData[i].securedParties.includes(localState.securedParties)
          ) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.folioNumber) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].clientReferenceId) {
          if (
            !tableData[i].clientReferenceId.includes(localState.folioNumber)
          ) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.registrationNumber) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].registrationNumber) {
          if (
            !tableData[i].registrationNumber.includes(
              localState.registrationNumber
            )
          ) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.status) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].statusType) {
          if (tableData[i].statusType !== localState.status) {
            tableData[i].hide = true
          }
        }
      }
    }

    if (localState.daysToExpiry) {
      for (let i = 0; i < tableData.length; i++) {
        if (tableData[i].expireDays) {
          if (tableData[i].expireDays === localState.daysToExpiry) {
            tableData[i].hide = true
          }
        }
      }
    }
    localState.tableData = tableData
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
      console.log(localState.status)
      filterResults(localState.originalData)
    }
  )

  watch(
    () => localState.daysToExpiry,
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
