import { VehicleCollateralIF, SearchNameIF } from '@/interfaces'

// Interface for a single search result matching the search criteria.
export interface SearchResultIF {
  matchType: string, // EXACT or SIMILAR
  registrationNumber: string, // Conditional: only returned with search by registration number.
  baseRegistrationNumber: string,
  createDateTime: string, // UTC ISO formmatted date and time of financing statement.
  registrationType: string,
  vehicleCollateral?: VehicleCollateralIF // Conditional: included if not debtor search.
  debtor?: SearchNameIF // Conditional: included if business debtor name or indivdual debtor name search.
}
