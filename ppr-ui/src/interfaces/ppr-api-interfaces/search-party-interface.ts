import { AddressIF } from '@/interfaces'

// Search Party interface represents a search result from a party code search
export interface SearchPartyIF {
  code: string, // party code.
  businessName?: string, 
  contact?: [
    name?: string,
    areaCode?: string,
    phoneNumber?: string
  ], 
  emailAddress?: string, 
  address?: AddressIF
}
