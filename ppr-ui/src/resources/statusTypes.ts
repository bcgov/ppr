import { APIStatusTypes, UIStatusTypes, MhUIStatusTypes, MhApiStatusTypes } from '@/enums'

export const StatusTypes = [
  {
    value: APIStatusTypes.DRAFT,
    title: UIStatusTypes.DRAFT
  },
  {
    value: APIStatusTypes.ACTIVE,
    title: UIStatusTypes.ACTIVE
  },
  {
    value: APIStatusTypes.EXPIRED,
    title: UIStatusTypes.EXPIRED
  },
  {
    value: APIStatusTypes.DISCHARGED,
    title: UIStatusTypes.DISCHARGED
  }
]

export const MhStatusTypes = [
  {
    value: MhApiStatusTypes.DRAFT,
    title: MhUIStatusTypes.DRAFT
  },
  {
    value: MhApiStatusTypes.ACTIVE,
    title: MhUIStatusTypes.ACTIVE
  },
  {
    value: MhApiStatusTypes.EXEMPT,
    title: MhUIStatusTypes.EXEMPT
  },
  {
    value: MhApiStatusTypes.CANCELLED,
    title: MhUIStatusTypes.CANCELLED
  }
]

export const PprAPIToUIStatusTypesMap = {
  [APIStatusTypes.DRAFT]: UIStatusTypes.DRAFT,
  [APIStatusTypes.ACTIVE]: UIStatusTypes.ACTIVE,
  [APIStatusTypes.EXPIRED]: UIStatusTypes.EXPIRED,
  [APIStatusTypes.DISCHARGED]: UIStatusTypes.DISCHARGED
}

export const MhrAPIToUIStatusTypesMap = {
  [MhApiStatusTypes.DRAFT]: MhUIStatusTypes.DRAFT,
  [MhApiStatusTypes.ACTIVE]: MhUIStatusTypes.ACTIVE,
  [MhApiStatusTypes.EXEMPT]: MhUIStatusTypes.EXEMPT,
  [MhApiStatusTypes.CANCELLED]: MhUIStatusTypes.CANCELLED
}
