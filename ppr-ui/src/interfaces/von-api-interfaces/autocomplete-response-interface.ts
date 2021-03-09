import { AutoCompleteResultIF } from '@/interfaces'

// Search Query response (search step 1) interface.
export interface AutoCompleteResponseIF {
  total: number,
  results: Array<AutoCompleteResultIF>
}
