import { reactive, toRefs, computed } from '@vue/composition-api'
import { VehicleTypes } from '@/resources'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'

export const useVehicle = (props, context) => {
  const { setAddCollateral } = useActions<any>(['setAddCollateral'])
  const { getAddCollateral } = useGetters<any>(['getAddCollateral'])
  const localState = reactive({
    currentVehicle: {} as VehicleCollateralIF,
    vehicleTypes: VehicleTypes,
    getSerialLabel: computed(function () {
      switch (localState.currentVehicle.type) {
        case '':
          return 'Select a vehicle type first'
        case 'MH':
          return 'Serial Number (if MHR number is not available)'
        case 'BO':
          return 'Boat Serial Number'
        case 'AF':
        case 'AC':
          return 'Aircraft Airframe D.O.T number'
        case 'OM':
          return 'Outboard Motor Serial Number'
        case 'TR':
          return 'Trailer Serial Number'
        default:
          return 'Serial or VIN Number'
      }
    }),
    getSerialDisabled: computed(function () {
      return localState.currentVehicle.type === ''
    }),
    getSerialHint: computed(function () {
      let hint = 'Up to 25 characters'
      switch (localState.currentVehicle.type) {
        case '':
          hint = ''
          break
        case 'AC':
          hint = 'Up to 25 letters'
          break
        case 'MH':
          hint = 'Must contain 6 digits'
          break
      }
      return hint
    })
  })

  const getVehicle = () => {
    const vehicles: VehicleCollateralIF[] = getAddCollateral.value.vehicleCollateral
    if (props.activeIndex >= 0) {
      localState.currentVehicle = vehicles[props.activeIndex]
    } else {
      localState.currentVehicle = { id: -1, type: '', serialNumber: '', model: '', make: '', year: '' }
    }
  }

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeVehicle = (): void => {
    context.emit('removeVehicle', props.activeIndex)
    resetFormAndData(true)
  }

  const addVehicle = () => {
    let collateral = getAddCollateral.value // eslint-disable-line
    let newList: VehicleCollateralIF[] = collateral.vehicleCollateral // eslint-disable-line
    // New vehicle
    if (props.activeIndex === -1) {
      localState.currentVehicle.id = newList.length + 1
      newList.push(localState.currentVehicle)
    } else {
      // Edit vehicle
      newList.splice(props.activeIndex, 1, localState.currentVehicle)
    }
    collateral.vehicleCollateral = newList
    collateral.valid = true
    setAddCollateral(collateral)
    context.emit('resetEvent')
  }

  return {
    getVehicle,
    addVehicle,
    resetFormAndData,
    removeVehicle,
    ...toRefs(localState)
  }
}
