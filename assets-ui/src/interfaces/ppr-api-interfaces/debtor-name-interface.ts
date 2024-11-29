import { IndividualNameIF } from '@/interfaces'

// Debtor business or individual name interface.
export interface DebtorNameIF {
  businessName?: string, // Conditional: returned with debtor business name search.
  personName?: IndividualNameIF // Conditional: returned with debtor individual name search.
}
