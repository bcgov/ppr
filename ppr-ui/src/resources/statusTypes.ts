import { APIStatusTypes, UIStatusTypes, mhUIStatusTypes } from '@/enums'

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
    value: mhUIStatusTypes.DRAFT,
    text: mhUIStatusTypes.DRAFT
  },
  {
    value: mhUIStatusTypes.ACTIVE,
    mhrValue: mhUIStatusTypes.ACTIVE,
    text: mhUIStatusTypes.ACTIVE
  },
  {
    value: mhUIStatusTypes.EXEMPT,
    text: mhUIStatusTypes.EXEMPT
  },
  {
    value: mhUIStatusTypes.HISTORICAL,
    text: mhUIStatusTypes.HISTORICAL
  }
]
