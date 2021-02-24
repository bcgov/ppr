import { APISearchTypes, UISearchTypes } from '@/enums'
import { HintIF } from '.'

// Search type interface
export interface SearchTypeIF {
  divider: boolean
  hints: HintIF
  selectDisabled: boolean
  searchTypeUI: UISearchTypes
  searchTypeAPI: APISearchTypes
  textLabel: string
}
