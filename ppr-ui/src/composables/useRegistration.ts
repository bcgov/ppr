import { RegistrationIF, DraftIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { reactive, toRefs } from '@vue/composition-api'
import { RegistrationTypes, StatusTypes } from '@/resources'
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'

export const useRegistration = () => {
  const localState = reactive({
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

  const filterResults = (tableData: Array<any>): Array<any> => {
    return tableData
  }

  return {
    getFormattedDate,
    getStatusDescription,
    getPdfLink,
    getRegistrationType,
    filterResults,
    ...toRefs(localState)
  }
}
