
// New registration add secured parties and debtors interface.
export interface AddPartiesIF {
  valid: boolean,
  registeringParty: string[]
  securedParties: string[],
  debtors: string[]
}
