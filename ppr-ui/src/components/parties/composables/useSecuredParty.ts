import { reactive, toRefs, computed } from '@vue/composition-api'
import { PartyIF, AddressIF, SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { PartyAddressSchema } from '@/schemas'
import { partyCodeSearch } from '@/utils'

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
    currentIsBusiness: null,
    toggleDialog: false,
    dialogResults: []
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

  const addSecuredParty = async () => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.securedParties // eslint-disable-line
    // New secured party
    if (props.activeIndex === -1) {
      if (localState.currentSecuredParty.businessName) {
        // go to the service and see if there are similar secured parties
        const response: [SearchPartyIF] = await partyCodeSearch(
          localState.currentSecuredParty.businessName
        )
        // check if any results
        if (response?.length > 0) {
          // show secured party selection popup
          localState.toggleDialog = true
          localState.dialogResults = response
          console.log(localState.dialogResults)
          return
        }
      }
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

  /**
   * Handles update events from address sub-components.
   */
  const updateAddress = (newAddress: AddressIF): void => {
    localState.currentSecuredParty.address = newAddress
  }

  return {
    getSecuredParty,
    addSecuredParty,
    resetFormAndData,
    removeSecuredParty,
    addressSchema,
    updateAddress,
    ...toRefs(localState)
  }
}
