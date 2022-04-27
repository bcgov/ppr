import { APIMHRSearchTypes, APISearchTypes, BlankSearchTypes, UIMHRSearchTypes, UISearchTypes } from '@/enums'
import { HintIF } from '.'

// Search type interface
export interface SearchTypeIF {
  divider: boolean
  hints: HintIF
  selectDisabled: boolean
  searchTypeUI: UISearchTypes|UIMHRSearchTypes
  searchTypeAPI: APISearchTypes|APIMHRSearchTypes|BlankSearchTypes
  textLabel: string
  group: number
  class?: string
  icon?: string
  color?: string
}
