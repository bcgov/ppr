import { ref, computed, reactive, watch } from '@vue/composition-api'
import useVuelidate from '@vuelidate/core'
import { required, email, maxLength, alpha, numeric, alphaNum, between } from '@vuelidate/validators'
import { useGetters } from 'vuex-composition-helpers'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { APIVehicleTypes } from '@/enums'

const errors = reactive({})

export const useCollateralForm = (index: number) => {

  const { getAddCollateral } = useGetters<any>(['getAddCollateral'])
  const vehicles: VehicleCollateralIF[] = getAddCollateral.value.vehicleCollateral

  const getVehicle = (): VehicleCollateralIF => {
    if (index >= 0) {
      return vehicles[index]
    } else {
      return { id: -1, type: '', year: 2021, make: '', model: '', serialNumber: '' }
    }
  }

  const vehicle = reactive(getVehicle())

  const type = ref(vehicle.type)
  const year = ref(vehicle.year)
  const make = ref(vehicle.make)
  const model = ref(vehicle.model)
  const serialNumber = ref(vehicle.serialNumber)

  const lowYear = 1800
  const thisYear = new Date().getFullYear() + 1

  const rules = computed(() => {
    return {
      type: { required },
      year: { required, between: between(1800, thisYear) },
      make: { required },
      model: { required },
      serialNumber: { required }
    }
  })

  const $v = useVuelidate(
    rules,
    { type, year, make, model, serialNumber }
  )
  const handleBlur = (key) => {
    $v[key].$dirty = true;
  }

  const validateSerialNumber = () => {
    switch (type.value) {
      case APIVehicleTypes.MOTOR_VEHICLE:

        break
      case APIVehicleTypes.AIRCRAFT:
        return {
          required,
          maxLength: maxLength(25),
          alpha
        }
        break
      case APIVehicleTypes.AIRCRAFT_AIRFRAME:
        return {
          required,
          maxLength: maxLength(25),
          alpha
        }
        break
      case APIVehicleTypes.BOAT:
        return {
          required,
          maxLength: maxLength(25),
          alphaNum
        }
        break
      case APIVehicleTypes.MANUFACTURED_HOME:
        return {
          required,
          maxLength: maxLength(6),
          numeric
        }
        break
      case APIVehicleTypes.OUTBOARD_MOTOR:
        return {
          required,
          maxLength: maxLength(25),
          alphaNum
        }
        break
      case APIVehicleTypes.TRAILER:
        return {
          required,
          maxLength: maxLength(25),
          alphaNum
        }
        break
    }
  }
  const isValidForm = () => {
    $v.$dirty = true;
    if (!$v.$invalid) {
      return true;
    } else {
      return false;
    }
  }

  const formErrors = () => {
    let errors = []
    if (!$v['type'].$required) {
      errors.push('Please select a type')
    }
    return errors
  }

  return { vehicle, errors, validateSerialNumber, isValidForm, formErrors, $v, handleBlur }
}
