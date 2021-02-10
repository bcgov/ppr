import { IndividualNameIF } from '@/interfaces'

// Search result Debtor business or individual name interface.
export interface SearchNameIF {
  type: string, // One of VehicleTypes
  businessName?: string, // Conditional: returned with debtor business name search.
  personName?: IndividualNameIF // Conditional: returned with debtor individual name search.
}
