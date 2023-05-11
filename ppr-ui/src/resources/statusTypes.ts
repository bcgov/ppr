import { APIStatusTypes, UIStatusTypes, MhUIStatusTypes, MhApiStatusTypes } from '@/enums'

export const StatusTypes = [
  {
    value: APIStatusTypes.DRAFT,
    text: UIStatusTypes.DRAFT
  },
  {
    value: APIStatusTypes.ACTIVE,
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
  [MhApiStatusTypes.HISTORICAL]: MhUIStatusTypes.HISTORICAL
}
