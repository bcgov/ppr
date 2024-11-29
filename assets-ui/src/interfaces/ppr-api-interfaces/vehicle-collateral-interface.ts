import { ActionTypes, APIVehicleTypes } from '@/enums'

// Vehicle collateral interface.
export interface VehicleCollateralIF {
  id: number,
  type: APIVehicleTypes, // One of VehicleTypes
  serialNumber: string,
  year?: number | '', // Optional
  make?: string, // Optional
  model?: string, // Optional
  manufacturedHomeRegistrationNumber?: string, // Conditional: only returned on MHR number search.
  vehicleId?: number // System generated used for amendment/change registrations.
  action?: ActionTypes // Local state indicates corrected/added/removed
}
