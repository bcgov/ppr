import { HomeOwnerPartyTypes } from '@/enums'

export interface OwnerRoleConfigIF {
  id: string
  class: string
  model: HomeOwnerPartyTypes,
  label: string
  tooltipContent: string
}
