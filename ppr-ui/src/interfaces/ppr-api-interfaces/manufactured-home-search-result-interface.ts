import { IndividualNameIF } from '@/interfaces'

// Interface for a single search result matching the search criteria.
export interface ManufacturedHomeSearchResultIF {
  id: number
  ownerName: IndividualNameIF
  organizationName?: string
  status: string // ACTIVE or EXEMPT or HISTORIC
  mhrNumber: string
  serialNumber: string
  activeCount?: number
  baseInformation?: {
    year?: number | '' // Optional
    make?: string // Optional
    model?: string // Optional
  }
  homeLocation?: string // Optional
  selected?: boolean // Optional
  includeLienInfo?: boolean // Optional
  ownerStatus?: string
  activeCount?: number
  exemptCount?: number
  historicalCount?: number
}
