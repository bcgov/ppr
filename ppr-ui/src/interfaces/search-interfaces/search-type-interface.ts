import { APIMHRSearchTypes, APISearchTypes, UIMHRSearchTypes, UISearchTypes } from '@/enums'
import { HintIF } from '.'

// Search type interface
export interface SearchTypeIF {
  divider: boolean
  hints: HintIF
  selectDisabled: boolean
  searchTypeUI: UISearchTypes|UIMHRSearchTypes
  searchTypeAPI: APISearchTypes|APIMHRSearchTypes
  textLabel: string
  group: number
  class?: string
}
