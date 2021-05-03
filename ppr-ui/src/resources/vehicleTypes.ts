import { APIVehicleTypes, UIVehicleTypes } from '@/enums'

export const VehicleTypes: Array<any> = [
  {
    value: APIVehicleTypes.MOTOR_VEHICLE,
    text: UIVehicleTypes.MOTOR_VEHICLE
  },
  {
    value: APIVehicleTypes.BOAT,
    text: UIVehicleTypes.BOAT
  },
  {
    value: APIVehicleTypes.TRAILER,
    text: UIVehicleTypes.TRAILER
  },
  {
    value: APIVehicleTypes.OUTBOARD_MOTOR,
    text: UIVehicleTypes.OUTBOARD_MOTOR
  },
  {
    value: APIVehicleTypes.MANUFACTURED_HOME,
    text: UIVehicleTypes.MANUFACTURED_HOME
  },
  {
    value: APIVehicleTypes.AIRCRAFT_AIRFRAME,
    text: UIVehicleTypes.AIRCRAFT_AIRFRAME
  },
  {
    value: APIVehicleTypes.AIRCRAFT,
    text: UIVehicleTypes.AIRCRAFT
  }
]
