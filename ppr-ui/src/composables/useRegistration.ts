import { RegistrationIF, DraftIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { UIRegistrationTypes, APIRegistrationTypes } from '@/enums'

export const useRegistration = () => {
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

  return {
    getFormattedDate,
    getStatusDescription,
    getPdfLink,
    getRegistrationType
  }
}
