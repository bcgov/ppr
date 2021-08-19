import { reactive, toRefs, computed } from '@vue/composition-api'
import { VehicleTypes, VehicleTypesNoMH } from '@/resources'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { APIRegistrationTypes } from '@/enums'

export const useVehicle = (props, context) => {
  const { setAddCollateral } = useActions<any>(['setAddCollateral'])
  const { getAddCollateral } = useGetters<any>(['getAddCollateral'])
  const { getRegistrationType } = useGetters<any>(['getRegistrationType'])
  const registrationType = getRegistrationType.value.registrationTypeAPI
  const localState = reactive({
    currentVehicle: {} as VehicleCollateralIF,
    vehicleTypes: VehicleTypes,
    vehicleTypesNoMH: VehicleTypesNoMH,
    getSerialLabel: computed(function () {
      switch (localState.currentVehicle.type) {
        case '':
          return 'Select a vehicle type first'
        case 'MH':
          return 'Serial Number (if MHR number is not available)'
        case 'BO':
          return 'Serial Number'
        case 'AF':
          return 'D.O.T or Serial Number'
        case 'AC':
          return 'D.O.T Number'
        case 'OB':
          return 'Serial Number'
        case 'TR':
          return 'Trailer Serial Number'
        default:
          return 'Serial or VIN Number'
      }
    }),
    getSerialDisabled: computed(function () {
      return localState.currentVehicle.type === ''
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

  const hasVehicleCollateral = (): boolean => {
    const vhArray = [
      APIRegistrationTypes.SECURITY_AGREEMENT,
      APIRegistrationTypes.REPAIRERS_LIEN,
      APIRegistrationTypes.MARRIAGE_MH,
      APIRegistrationTypes.LAND_TAX_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
      APIRegistrationTypes.SALE_OF_GOODS
    ]
    return vhArray.includes(registrationType)
  }

  const hasGeneralCollateral = (): boolean => {
    const ghArray = [
      APIRegistrationTypes.SECURITY_AGREEMENT,
      APIRegistrationTypes.SALE_OF_GOODS,
      APIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
      APIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
      APIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
      // APIRegistrationTypes.MISCELLANEOUS_REGISTRATION,
      // APIRegistrationTypes.MISCELLANEOUS_OTHER
    ]
    return ghArray.includes(registrationType)
  }

  const mustHaveManufacturedHomeCollateral = (): boolean => {
    const mhArray = [
      APIRegistrationTypes.MARRIAGE_MH,
      APIRegistrationTypes.LAND_TAX_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_LIEN
    ]
    return mhArray.includes(registrationType)
  }

  const excludesManufacturedHomeCollateral = (): boolean => {
    const mhArray = [
      APIRegistrationTypes.REPAIRERS_LIEN
    ]
    return mhArray.includes(registrationType)
  }

  return {
    getVehicle,
    addVehicle,
    resetFormAndData,
    removeVehicle,
    hasVehicleCollateral,
    hasGeneralCollateral,
    mustHaveManufacturedHomeCollateral,
    excludesManufacturedHomeCollateral,
    ...toRefs(localState)
  }
}
