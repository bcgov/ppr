import { APIStatusTypes, UIStatusTypes, mhUIStatusTypes, mhApiStatusTypes } from '@/enums'

export const StatusTypes = [
  {
    value: APIStatusTypes.DRAFT,
    text: UIStatusTypes.DRAFT
  },
  {
    value: APIStatusTypes.ACTIVE,
    mhrValue: APIStatusTypes.MHR_ACTIVE,
    text: UIStatusTypes.ACTIVE
  },
  {
    value: APIStatusTypes.EXPIRED,
    text: UIStatusTypes.EXPIRED
  },
  {
    value: APIStatusTypes.DISCHARGED,
    text: UIStatusTypes.DISCHARGED
  }
]

export const mhStatusTypes = [
  {
    value: mhApiStatusTypes.DRAFT,
    text: mhUIStatusTypes.DRAFT
  },
  {
    value: mhApiStatusTypes.ACTIVE,
    text: mhUIStatusTypes.ACTIVE
  },
  {
    value: mhApiStatusTypes.EXEMPT,
    text: mhUIStatusTypes.EXEMPT
  },
  {
    value: mhApiStatusTypes.HISTORICAL,
    text: mhUIStatusTypes.HISTORICAL
  }
]
