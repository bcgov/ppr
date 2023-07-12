import { computed, reactive, toRefs } from 'vue-demi'
import { PartyIF, AddressIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useStore } from '@/store/store'
import { PartyAddressSchema } from '@/schemas'
import { ActionTypes, RegistrationFlowType, SecuredPartyTypes } from '@/enums'
import { checkAddress, formatAddress } from '@/composables/address/factories/address-factory'
import { cloneDeep, isEqual } from 'lodash'
import { useParty } from '@/composables/useParty'
import { isObjectEqual } from '@/utils/validation-helper'
import { storeToRefs } from 'pinia'
import { SecuredPartyRestrictedList } from '@/resources'
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
const { isPartiesValid } = useParty()

export const useSecuredParty = (context?) => {
  const { setAddSecuredPartiesAndDebtors } = useStore()
  const {
    // Getters
    getAddSecuredPartiesAndDebtors,
    getRegistrationFlowType,
    getRegistrationType
  } = storeToRefs(useStore())

  const localState = reactive({
    currentSecuredParty: {
      businessName: '',
      personName: initPerson,
      emailAddress: '',
      address: initAddress
    } as PartyIF,
    currentIsBusiness: null,
    partyType: null,
    registrationFlowType: getRegistrationFlowType,
    originalSecuredParty: null,
    isSecuredPartiesRestricted: computed((): boolean =>
      SecuredPartyRestrictedList.includes(getRegistrationType.value?.registrationTypeAPI))
  })

  const getSecuredParty = (isRegisteringParty: boolean, activeIndex: number) => {
    const securedParties: PartyIF[] =
      getAddSecuredPartiesAndDebtors.value.securedParties
    const registeringParty: PartyIF = getAddSecuredPartiesAndDebtors.value.registeringParty
    if (isRegisteringParty && registeringParty && registeringParty.action && !registeringParty.code) {
      // copy the existing registering party
      localState.currentSecuredParty = JSON.parse(JSON.stringify(registeringParty))
      localState.currentSecuredParty.address = checkAddress(localState.currentSecuredParty.address, PartyAddressSchema)
      localState.currentIsBusiness = false
      localState.partyType = SecuredPartyTypes.INDIVIDUAL
      if (localState.currentSecuredParty.businessName) {
        localState.currentIsBusiness = true
        localState.partyType = SecuredPartyTypes.BUSINESS
        localState.currentSecuredParty.personName = Object.assign({}, initPerson)
      }
    } else if (activeIndex >= 0) {
      // deep copy so original object doesn't get modified
      localState.currentSecuredParty = JSON.parse(JSON.stringify(securedParties[activeIndex]))
      localState.currentSecuredParty.address = checkAddress(localState.currentSecuredParty.address, PartyAddressSchema)
      localState.currentIsBusiness = false
      localState.partyType = SecuredPartyTypes.INDIVIDUAL
      if (localState.currentSecuredParty.businessName) {
        localState.currentIsBusiness = true
        localState.partyType = SecuredPartyTypes.BUSINESS
        localState.currentSecuredParty.personName = Object.assign({}, initPerson)
      }
    } else {
      localState.partyType = null
      const blankSecuredParty = {
        businessName: '',
        personName: Object.assign({}, initPerson),
        birthDate: '',
        emailAddress: '',
        address: Object.assign({}, initAddress)
      }
      localState.currentSecuredParty = blankSecuredParty
    }
    localState.originalSecuredParty = cloneDeep(localState.currentSecuredParty)
  }

  const addressSchema = PartyAddressSchema

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context?.emit('resetEvent')
    }
  }

  const isExistingSecuredParty = (partyCode: string, isRegisteringParty: boolean): boolean => {
    if (isRegisteringParty) {
      return getAddSecuredPartiesAndDebtors.value?.registeringParty?.code === partyCode
    }
    const securedParties = getAddSecuredPartiesAndDebtors.value.securedParties
    return securedParties.some(party => party.code === partyCode)
  }

  const hasMatchingSecuredParty = (addedParty: PartyIF, isEditMode: boolean, activeIndex: number): boolean => {
    // store state without newly added party.
    const parties = cloneDeep(getAddSecuredPartiesAndDebtors.value.securedParties)
    if (isEditMode) parties.splice(activeIndex, 1)
    if (localState.partyType === SecuredPartyTypes.INDIVIDUAL) {
      return parties.some(party =>
        isObjectEqual(party.personName, addedParty.personName) &&
        isObjectEqual(party.address, addedParty.address)
      )
    } else {
      return parties.some(party =>
        party.businessName?.toUpperCase() === addedParty.businessName?.toUpperCase() &&
        isObjectEqual(party.address, addedParty.address)
      )
    }
  }

  const removeSecuredParty = (activeIndex: number): void => {
    context?.emit('removeSecuredParty', activeIndex)
    resetFormAndData(true)
  }

  const addEditSecuredParty = async (activeIndex: number) => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.securedParties // eslint-disable-line
    if (!localState.currentSecuredParty.businessName) {
      delete localState.currentSecuredParty.businessName
    }

    // first format the original address
    // if they didn't change anything, just exit
    if (localState.originalSecuredParty) {
      localState.originalSecuredParty.address = formatAddress(localState.originalSecuredParty.address)
    }
    if ((localState.registrationFlowType === RegistrationFlowType.AMENDMENT) &&
    isEqual(localState.currentSecuredParty, localState.originalSecuredParty)) {
      resetFormAndData(true)
      return
    }
    // New secured party
    if (activeIndex === -1) {
      localState.currentSecuredParty.action = ActionTypes.ADDED
      newList.push(localState.currentSecuredParty)
    } else {
      // Edit party
      if (!localState.currentSecuredParty.action) {
        localState.currentSecuredParty.action = ActionTypes.EDITED
      }
      newList.splice(activeIndex, 1, localState.currentSecuredParty)
    }
    parties.securedParties = newList
    setAddSecuredPartiesAndDebtors(parties)
    context?.emit('resetEvent')
  }

  const setRegisteringParty = (registeringParty: PartyIF) => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    registeringParty.action = ActionTypes.EDITED
    parties.registeringParty = registeringParty
    parties.valid = isPartiesValid(parties, getRegistrationType.value.registrationTypeAPI)
    setAddSecuredPartiesAndDebtors(parties)
  }

  const addSecuredParty = (newParty: PartyIF, activeIndex: number = -1) => {
    const parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    const newList: PartyIF[] = parties.securedParties
    if (activeIndex > -1) {
      newParty.action = ActionTypes.ADDED
      newList.splice(activeIndex, 1, newParty)
    } else {
      // Add
      // eslint-disable-line
      newParty.action = ActionTypes.ADDED
      newList.push(newParty)
    }
    parties.securedParties = newList
    parties.valid = isPartiesValid(parties, getRegistrationType.value.registrationTypeAPI)
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
    addEditSecuredParty,
    resetFormAndData,
    removeSecuredParty,
    addressSchema,
    updateAddress,
    addSecuredParty,
    isExistingSecuredParty,
    RegistrationFlowType,
    ActionTypes,
    setRegisteringParty,
    hasMatchingSecuredParty,
    isObjectEqual,
    ...toRefs(localState)
  }
}
