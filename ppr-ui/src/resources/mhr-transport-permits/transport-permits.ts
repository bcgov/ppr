import { LocationChangeTypes } from '@/enums'

export const locationChangeTypes = [
  {
    type: LocationChangeTypes.TRANSPORT_PERMIT,
    title: 'Transport Permit',
    feeSummaryTitle: 'Transport Permit'
  },
  {
    type: LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK,
    title: 'Transport Permit - Moving within the same Manufactured Home Park',
    feeSummaryTitle: 'Transport Permit'
  },
  {
    type: LocationChangeTypes.REGISTERED_LOCATION,
    title: 'Register Location Change',
    feeSummaryTitle: 'Register Location Change'
  }
]
