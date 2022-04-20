import { reactive, toRefs, computed } from '@vue/composition-api'
import { VehicleTypes, VehicleTypesNoMH } from '@/resources'
import { VehicleCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { ActionTypes, APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import { cloneDeep, isEqual } from 'lodash'

export const useVehicle = (props, context) => {
  const {
    getRegistrationType,
    getRegistrationFlowType,
    getVehicleCollateral
  } = useGetters<any>(['getRegistrationType', 'getRegistrationFlowType', 'getVehicleCollateral'])
  const { setCollateralValid } = useActions<any>(['setCollateralValid'])
  const { setVehicleCollateral } = useActions<any>(['setVehicleCollateral'])

  const registrationType = getRegistrationType.value.registrationTypeAPI

  const localState = reactive({
    currentVehicle: {} as VehicleCollateralIF,
    vehicleTypes: VehicleTypes,
    vehicleTypesNoMH: VehicleTypesNoMH,
    registrationFlowType: getRegistrationFlowType.value,
    getSerialLabel: computed(function () {
      switch (localState.currentVehicle.type) {
        case '':
          return 'Select a vehicle type first'
        case 'MH':
          return 'Serial Number (if MHR number is not available)'
        case 'BO':
          return 'Serial Number'
        case 'AF':
          return 'D.O.T. or Serial Number'
        case 'AC':
          return 'D.O.T. Number'
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
    }),
    originalVehicle: null
  })

  const getVehicle = () => {
    const vehicles = getVehicleCollateral.value as VehicleCollateralIF[]
    if (props.activeIndex >= 0) {
      // deep copy so original object doesn't get modified
      localState.currentVehicle = JSON.parse(JSON.stringify(vehicles[props.activeIndex]))
      localState.originalVehicle = cloneDeep(localState.currentVehicle)
    } else {
      localState.currentVehicle = {
        id: -1,
        type: '',
        serialNumber: '',
        model: '',
        make: '',
        year: ''
      }
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
    let newList = getVehicleCollateral.value as VehicleCollateralIF[] || []// eslint-disable-line

    // if they blanked out the mhr number, take it out, so api does not bomb
    if (localState.currentVehicle.manufacturedHomeRegistrationNumber?.trim() === '') {
      delete localState.currentVehicle.manufacturedHomeRegistrationNumber
    }

    // New vehicle
    if (props.activeIndex === -1) {
      localState.currentVehicle.action = ActionTypes.ADDED
      localState.currentVehicle.id = newList.length + 1
      newList.push(localState.currentVehicle)
    } else {
      // remove the NR state when comparing
      if (localState.originalVehicle.manufacturedHomeRegistrationNumber === 'NR') {
        delete localState.originalVehicle.manufacturedHomeRegistrationNumber
      }
      // if they didn't change anything, just exit
      if ((localState.registrationFlowType === RegistrationFlowType.AMENDMENT) &&
        isEqual(localState.currentVehicle, localState.originalVehicle)) {
        resetFormAndData(true)
        return
      }
      // Edit vehicle
      if (!localState.currentVehicle.action) {
        localState.currentVehicle.action = ActionTypes.EDITED
      }
      newList.splice(props.activeIndex, 1, localState.currentVehicle)
    }
    setVehicleCollateral(newList)
    setCollateralValid(true)
    context.emit('resetEvent')
  }

  const hasVehicleCollateral = (): boolean => {
    const vhArray = [
      APIRegistrationTypes.SECURITY_AGREEMENT,
      APIRegistrationTypes.REPAIRERS_LIEN,
      APIRegistrationTypes.MARRIAGE_MH,
      APIRegistrationTypes.LAND_TAX_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
      APIRegistrationTypes.SALE_OF_GOODS,
      APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
      APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
      APIRegistrationTypes.MAINTENANCE_LIEN,
      APIRegistrationTypes.MISC_MINERAL_RESOURCE,
      APIRegistrationTypes.CROWN_MINING_TAX,
      APIRegistrationTypes.CROWN_CORP_CAPITAL_TAX,
      APIRegistrationTypes.CROWN_CONSUMPTION_TRANSITION_TAX,
      APIRegistrationTypes.CROWN_HOTEL_ROOM_TAX,
      APIRegistrationTypes.CROWN_SOCIAL_SERVICE_TAX,
      APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT,
      APIRegistrationTypes.TRANSITION_FINANCING_STATEMENT,
      APIRegistrationTypes.TRANSITION_SALE_OF_GOODS,
      APIRegistrationTypes.TRANSITION_TAX_LIEN,
      APIRegistrationTypes.TRANSITION_MH,
      APIRegistrationTypes.LIEN_UNPAID_WAGES
    ]
    return vhArray.includes(registrationType)
  }

  const hasOptionalVehicleCollateral = (): boolean => {
    const vhArray = [
      APIRegistrationTypes.CARBON_TAX,
      APIRegistrationTypes.EXCISE_TAX,
      APIRegistrationTypes.FOREST,
      APIRegistrationTypes.INCOME_TAX,
      APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
      APIRegistrationTypes.LOGGING_TAX,
      APIRegistrationTypes.MINERAL_LAND_TAX,
      APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
      APIRegistrationTypes.SCHOOL_ACT,
      APIRegistrationTypes.MOTOR_FUEL_TAX,
      APIRegistrationTypes.MAINTENANCE_LIEN,
      APIRegistrationTypes.OTHER,
      APIRegistrationTypes.PROVINCIAL_SALES_TAX,
      APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
      APIRegistrationTypes.RURAL_PROPERTY_TAX
    ]
    return vhArray.includes(registrationType)
  }

  const mustHaveManufacturedHomeCollateral = (): boolean => {
    const mhArray = [
      APIRegistrationTypes.MARRIAGE_MH,
      APIRegistrationTypes.LAND_TAX_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_NOTICE
    ]
    return mhArray.includes(registrationType)
  }

  const excludesManufacturedHomeCollateral = (): boolean => {
    const mhArray = [APIRegistrationTypes.REPAIRERS_LIEN]
    return mhArray.includes(registrationType)
  }

  return {
    getVehicle,
    addVehicle,
    resetFormAndData,
    removeVehicle,
    hasVehicleCollateral,
    hasOptionalVehicleCollateral,
    mustHaveManufacturedHomeCollateral,
    excludesManufacturedHomeCollateral,
    ActionTypes,
    RegistrationFlowType,
    ...toRefs(localState)
  }
}
