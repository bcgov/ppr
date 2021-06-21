import { reactive, toRefs, computed } from '@vue/composition-api'
import { PartyIF, AddressIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { PartyAddressSchema } from '@/schemas'

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

export const useSecuredParty = (props, context) => {
  const { setAddSecuredPartiesAndDebtors } = useActions<any>([
    'setAddSecuredPartiesAndDebtors'
  ])
  const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
    'getAddSecuredPartiesAndDebtors'
  ])
  const localState = reactive({
    currentSecuredParty: {
      businessName: '',
      personName: initPerson,
      emailAddress: '',
      address: initAddress
    } as PartyIF,
    currentIsBusiness: null
  })

  const getSecuredParty = () => {
    const securedParties: PartyIF[] =
      getAddSecuredPartiesAndDebtors.value.securedParties
    if (props.activeIndex >= 0) {
      localState.currentSecuredParty = securedParties[props.activeIndex]
      localState.currentIsBusiness = false
      if (localState.currentSecuredParty.businessName) {
        localState.currentIsBusiness = true
      }
    } else {
      const blankSecuredParty = {
        businessName: '',
        personName: Object.assign({}, initPerson),
        birthDate: '',
        emailAddress: '',
        address: Object.assign({}, initAddress)
      }
      localState.currentSecuredParty = blankSecuredParty
    }
  }

  const addressSchema = PartyAddressSchema

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeSecuredParty = (): void => {
    context.emit('removeSecuredParty', props.activeIndex)
    resetFormAndData(true)
  }

  const addSecuredParty = () => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.securedParties // eslint-disable-line
    // New debtor
    if (props.activeIndex === -1) {
      // localState.currentDebtor.id = newList.length + 1
      newList.push(localState.currentSecuredParty)
    } else {
      // Edit vehicle
      newList.splice(props.activeIndex, 1, localState.currentSecuredParty)
    }
    parties.securedParties = newList
    // collateral.valid = true
    setAddSecuredPartiesAndDebtors(parties)
    context.emit('resetEvent')
  }

  const addRegisteringParty = () => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.securedParties // eslint-disable-line
    // New debtor
    const tempSecuredParty = {
      businessName: 'Temp Registering Party',
      emailAddress: 'temp@email.com',
      address: {
        street: '123 Any St',
        streetAdditional: '',
        city: 'Victoria',
        region: 'BC',
        country: 'Canada',
        postalCode: 'V8T2T1',
        deliveryInstructions: ''
      }
    }
    newList.push(tempSecuredParty)

    parties.securedParties = newList

    setAddSecuredPartiesAndDebtors(parties)
  }

  /**
   * Handles update events from address sub-components.
   */
  const updateAddress = (newAddress: AddressIF): void => {
    localState.currentSecuredParty.address = newAddress
  }

  return {
    getSecuredParty,
    addSecuredParty,
    addRegisteringParty,
    resetFormAndData,
    removeSecuredParty,
    addressSchema,
    updateAddress,
    ...toRefs(localState)
  }
}
