import { reactive, toRefs } from 'vue'
import { PartyIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { Months } from '@/resources/months'
import { PartyAddressSchema } from '@/schemas'
import { useParty } from '@/composables/useParty'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import { checkAddress, formatAddress } from '@/composables/address/factories/address-factory'
import { cloneDeep, isEqual } from 'lodash'
import { localTodayDate } from '@/utils/date-helper'
import { storeToRefs } from 'pinia'

const initPerson = { first: '', middle: '', last: '' }
const initAddress = {
  street: '',
  streetAdditional: '',
  city: '',
  region: '',
  country: '',
  postalCode: '',
  deliveryInstructions: ''
}
const { getDay, getMonth, getMonthFull, getYear } = useParty()

export const useDebtor = (props, context) => {
  const { setAddSecuredPartiesAndDebtors } = useStore()
  const { getAddSecuredPartiesAndDebtors, getRegistrationFlowType } = storeToRefs(useStore())
  const localState = reactive({
    addressSchema: { ...PartyAddressSchema },
    currentDebtor: {
      businessName: '',
      personName: initPerson,
      birthDate: '',
      emailAddress: '',
      address: initAddress,
      action: null
    } as PartyIF,
    originalDebtor: null,
    year: '',
    day: '',
    monthValue: 0,
    months: Months,
    currentIsBusiness: props.isBusiness,
    registrationFlowType: getRegistrationFlowType.value,
    showAllAddressErrors: false
  })

  const getDebtor = () => {
    const debtors: PartyIF[] = getAddSecuredPartiesAndDebtors.value.debtors
    if (props.activeIndex >= 0) {
      // deep copy so original object doesn't get modified
      localState.currentDebtor = JSON.parse(JSON.stringify(debtors[props.activeIndex]))
      localState.currentDebtor.address = checkAddress(localState.currentDebtor.address, PartyAddressSchema)
      localState.currentIsBusiness = false
      if (localState.currentDebtor.businessName) {
        localState.currentIsBusiness = true
      } else {
        localState.year = getYear(localState.currentDebtor)
        localState.day = getDay(localState.currentDebtor)
      }
    } else {
      const blankDebtor = {
        businessName: '',
        personName: Object.assign({}, initPerson),
        birthDate: '',
        address: Object.assign({}, initAddress)
      }
      localState.currentDebtor = blankDebtor
    }
    localState.originalDebtor = cloneDeep(localState.currentDebtor)
  }

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeDebtor = (): void => {
    context.emit('removeDebtor', props.activeIndex)
    resetFormAndData(true)
  }

  const getMonthObject = () => {
    const partyMonth = {
      value: getMonth(localState.currentDebtor),
      title: getMonthFull(localState.currentDebtor)
    }
    return partyMonth
  }

  const addDebtor = () => {
    // messes with debtor comparison for individual
    if (localState.currentDebtor.businessName === undefined) {
      delete localState.currentDebtor.businessName
    }

    if (!localState.currentIsBusiness) {
      const dateOfBirth = new Date()
      // @ts-ignore - returned by toRef
      dateOfBirth.setFullYear(
        parseInt(localState.year),
        localState.monthValue - 1,
        parseInt(localState.day)
      )
      if (dateOfBirth instanceof Date && !isNaN(dateOfBirth.valueOf())) {
        localState.currentDebtor.birthDate = localTodayDate(dateOfBirth) + 'T00:00:00-08:00'
      } else {
        localState.currentDebtor.birthDate = null
        if (localState.originalDebtor && !localState.originalDebtor.birthDate) {
          localState.originalDebtor.birthDate = null
        }
      }
    }
    // format the original address before the compare
    if (localState.originalDebtor) {
      localState.originalDebtor.address = formatAddress(localState.originalDebtor.address)
    }
    // format the original birthdate the exact same before the compare
    if (localState.originalDebtor.birthDate && localState.originalDebtor.birthDate.length > 10) {
      const originalDateOfBirth = new Date(localState.originalDebtor.birthDate)
      localState.originalDebtor.birthDate = localTodayDate(originalDateOfBirth) + 'T00:00:00-08:00'
    }
    // if they didn't change anything, just exit
    if ((localState.registrationFlowType === RegistrationFlowType.AMENDMENT) &&
    isEqual(localState.currentDebtor, localState.originalDebtor)) {
      resetFormAndData(true)
      return
    }
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.debtors // eslint-disable-line
    // New debtor
    if (props.activeIndex === -1) {
      localState.currentDebtor.action = ActionTypes.ADDED
      newList.push(localState.currentDebtor)
    } else {
      // Edit debtor
      if (!localState.currentDebtor.action) {
        localState.currentDebtor.action = ActionTypes.EDITED
      }
      newList.splice(props.activeIndex, 1, localState.currentDebtor)
    }
    parties.debtors = newList
    setAddSecuredPartiesAndDebtors(parties)
    context.emit('resetEvent')
  }

  return {
    getDebtor,
    addDebtor,
    resetFormAndData,
    removeDebtor,
    getMonthObject,
    RegistrationFlowType,
    ActionTypes,
    ...toRefs(localState)
  }
}
