import { LocationChangeTypes } from '@/enums'

export const locationChangeTypes = [
  {
    type: LocationChangeTypes.TRANSPORT_PERMIT,
    title: 'Transport Permit'
  },
  {
    type: LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK,
    title: 'Transport Permit - Moving within the same Manufactured Home Park'
  },
  {
    type: LocationChangeTypes.REGISTERED_LOCATION,
    title: 'Register Location Change'
  }
]
