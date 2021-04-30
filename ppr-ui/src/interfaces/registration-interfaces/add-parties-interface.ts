import { PartyIF } from '@/interfaces'

// New registration add secured parties and debtors interface.
export interface AddPartiesIF {
  valid: boolean,
  registeringParty: PartyIF,
  securedParties: PartyIF[],
  debtors: PartyIF[]
}
