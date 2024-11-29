import { AutoCompleteResultIF } from '@/interfaces'

// Auto complete Query response interface.
export interface AutoCompleteResponseIF {
  total: number,
  results: Array<AutoCompleteResultIF>
}
