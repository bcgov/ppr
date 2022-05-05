import { IndividualNameIF } from '@/interfaces'

// Interface for a single search result matching the search criteria.
export interface ManufacturedHomeSearchResultIF {
  id: number
  ownerName: IndividualNameIF
  status: string // ACTIVE or EXEMPT or HISTORIC
  mhrNumber: string
  serialNumber: string
  baseInformation?: {
    year?: number | '' // Optional
    make?: string // Optional
    model?: string // Optional
  }
  homeLocation?: string // Optional
  selected?: boolean // Optional
  lienSelected?: boolean // Optional
}
