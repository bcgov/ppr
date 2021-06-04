import { reactive, toRefs, ref } from '@vue/composition-api'
import { PartyIF, AddressIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { Months } from '@/resources/months'
import { Countries, getCountryRegions } from '@/resources/countriesProvinces'
import { PartyAddressSchema } from '@/schemas'
import { LinkedErrors } from '@sentry/browser/dist/integrations'

const initPerson = { first: '', middle: '', last: '' }
const initAddress = {
  street: '',
  streetAdditional: '',
  city: '',
  region: '',
  country: '',
  postalCode: ''
}

export const useDebtor = (props, context) => {
  const { setAddSecuredPartiesAndDebtors } = useActions<any>(['setAddSecuredPartiesAndDebtors'])
  const { getAddSecuredPartiesAndDebtors } = useGetters<any>(['getAddSecuredPartiesAndDebtors'])
  const localState = reactive({
    currentDebtor: { businessName: '', personName: initPerson, birthDate: '', address: initAddress } as PartyIF,
    year: '',
    month: '',
    day: '',
    months: Months,
    countries: Countries
  })

  const getDebtor = () => {
    const debtors: PartyIF[] = getAddSecuredPartiesAndDebtors.value.debtors
    if (props.activeIndex >= 0) {
      localState.currentDebtor = debtors[props.activeIndex]
      props.isBusiness = false
      if (localState.currentDebtor.businessName) {
        props.isBusiness = true
      }
    }
  }

  const provinces = ref(getCountryRegions(localState.currentDebtor.address.country))
  const addressSchema = PartyAddressSchema

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeDebtor = (): void => {
    context.emit('removeDebtor', props.activeIndex)
    resetFormAndData(true)
  }

  const addDebtor = () => {
    if (!props.isBusiness) {
      const dateOfBirth = new Date()
      dateOfBirth.setFullYear(parseInt(localState.year), parseInt(localState.month) - 1, parseInt(localState.day))
      localState.currentDebtor.birthDate = dateOfBirth.toUTCString()
    }
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.debtors // eslint-disable-line
    // New debtor
    if (props.activeIndex === -1) {
      // localState.currentDebtor.id = newList.length + 1
      newList.push(localState.currentDebtor)
    } else {
      // Edit vehicle
      newList.splice(props.activeIndex, 1, localState.currentDebtor)
    }
    parties.debtors = newList
    // collateral.valid = true
    setAddSecuredPartiesAndDebtors(parties)
    context.emit('resetEvent')
  }

  /**
   * Handles update events from address sub-components.
   */
  const updateAddress = (newAddress: AddressIF): void => {
    localState.currentDebtor.address = newAddress
  }

  return {
    getDebtor,
    addDebtor,
    resetFormAndData,
    removeDebtor,
    provinces,
    addressSchema,
    updateAddress,
    ...toRefs(localState)
  }
}
