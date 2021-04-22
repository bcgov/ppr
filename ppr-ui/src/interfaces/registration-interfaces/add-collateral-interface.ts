import { VehicleCollateralIF } from '@/interfaces'

// New registration add vehicle and general collateral interface.
export interface AddCollateralIF {
  valid: boolean,
  vehicleCollateral?: VehicleCollateralIF[], // Either vehicle or general collatera is required.
  generalCollateral?: string // Max length 4000.
}
