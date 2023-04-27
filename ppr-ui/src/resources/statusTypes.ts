import { APIStatusTypes, UIStatusTypes, MhUIStatusTypes, MhApiStatusTypes } from '@/enums'

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

export const MhStatusTypes = [
  {
    value: MhApiStatusTypes.DRAFT,
    text: MhUIStatusTypes.DRAFT
  },
  {
    value: MhApiStatusTypes.ACTIVE,
    text: MhUIStatusTypes.ACTIVE
  },
  {
    value: MhApiStatusTypes.EXEMPT,
    text: MhUIStatusTypes.EXEMPT
  },
  {
    value: MhApiStatusTypes.HISTORICAL,
    text: MhUIStatusTypes.HISTORICAL
  }
]
