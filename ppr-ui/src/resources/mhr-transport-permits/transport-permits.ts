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
    title: 'Registered Location Change',
    feeSummaryTitle: 'Registered Location Change'
  },
  {
    type: LocationChangeTypes.TRANSPORT_PERMIT_CANCEL,
    title: 'Cancel Transport Permit',
    feeSummaryTitle: 'Cancel Transport Permit'
  },
  {
    type: LocationChangeTypes.EXTEND_PERMIT,
    title: 'Transport Permit - Extend',
    feeSummaryTitle: 'Extend Transport Permit'
  }
]
