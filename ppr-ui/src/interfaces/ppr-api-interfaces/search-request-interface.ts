
// Search Query request (search step 1) interface.
export interface SearchCriteriaIF {
  type: string, // One of APISearchTypes
  criteria: {
    value?: string // Conditional: required if not debtor search
    debtorName?: { // Conditional: required if debtor search
      first?: string, // Conditional: required if debtor individual name search
      second?: string, // Optional if debtor individual name search
      last?: string, // Conditional: required if debtor individual name search
      business?: string // Conditional: required if debtor business name search
    }
  },
  clientReferenceId?: string, // Optional.
  startDateTime?: string, // Optional: ISO formatted date and time.
  endDateTime?: string // Optional: ISO formatted date and time.
}
