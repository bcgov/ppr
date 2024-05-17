import { ActionTypes } from '@/enums'

// Existing court order information may not be altered. All elements are required.
export interface CourtOrderIF {
  courtOrder?: boolean // Optional property indicating court order otherwise commission order
  courtName: string, // Max length 250.
  courtRegistry: string, // Max length 60.
  fileNumber: string, // Max length 20.
  orderDate: string, // UTC ISO 8601 datetime format YYYY-MM-DDThh:mm:ssTZD.
  effectOfOrder: string, // Max length 500.
  action?: ActionTypes // Optional action type for amendments
}
