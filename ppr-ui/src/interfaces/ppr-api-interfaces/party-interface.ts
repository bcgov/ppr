import { AddressIF, IndividualNameIF } from '@/interfaces'
import { ActionTypes } from '@/enums'

// Party interface represents a single registering party, secured party, or debtor.
export interface PartyIF {
  code?: string, // Only for registering and submitting parties, provide code or name/address.
  businessName?: string, // Either businessName or personName is required if no code. Max length 150.
  personName?: IndividualNameIF, // Either businessName or personName is required if no code.
  birthDate?: string, // Debtor only UTC ISO 8601 datetime format YYYY-MM-DDThh:mm:ssTZD.
  emailAddress?: string, // Optional future for everyone currently only client code?.
  partyId?: number, // System generated used for amendment/change registrations.
  address?: AddressIF, // Reguired for debtors or if no party code.
  action?: ActionTypes // Optional action type for amendments
}
