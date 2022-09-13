import { APIStatusTypes, UIStatusTypes } from '@/enums'

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
