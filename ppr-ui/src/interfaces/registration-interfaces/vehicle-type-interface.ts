import type { APIVehicleTypes, UIVehicleTypes } from '@/enums'

// Vehicle type interface
export interface VehicleTypeIF {
  vehicleTypeUI: UIVehicleTypes
  vehicleTypeAPI: APIVehicleTypes
  textLabel: string
}
